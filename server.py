"""FastAPI Backend Server for Dalal Street AI Trading Terminal."""

import logging
from typing import Optional, Dict
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

from config import DEFAULT_CAPITAL_INR, get_watchlist
from data_ingestion.smart_money import fetch_fii_dii_activity
from data_ingestion.news_feed import fetch_all_market_news, find_news_for_ticker
from data_ingestion.market_data import fetch_stock_technical_profile
from screening.screener import run_screener
from risk.position_sizer import calculate_inr_position
from agents.sentiment_agent import analyze_stock_sentiment
from agents.debate_agent import run_bull_bear_debate
import simulation

logger = logging.getLogger(__name__)

app = FastAPI(title="Dalal Street AI Trading API", version="1.1.0")

# Enable CORS for local Node.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DebateRequest(BaseModel):
    symbol: str
    llm: Optional[str] = "gemini"

class BuyOrderRequest(BaseModel):
    symbol: str
    shares: int
    price: float
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    ai_score: Optional[float] = 0.0
    ai_verdict: Optional[str] = "BUY"

class SellOrderRequest(BaseModel):
    symbol: str
    exit_price: float
    shares: Optional[int] = None
    reason: Optional[str] = "Manual Exit"

class ResetPortfolioRequest(BaseModel):
    initial_cash: Optional[float] = 500000.0

from fastapi.responses import FileResponse, HTMLResponse
import os

@app.get("/")
def serve_root():
    """Serve the Dalal Street AI Light Theme Dashboard."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(app_dir, "public_html", "index.html"),
        os.path.join(app_dir, "frontend", "public", "index.html"),
        os.path.join(app_dir, "index.html"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return FileResponse(p)
    return {"status": "online", "system": "Dalal Street AI", "endpoints": ["/api/health", "/api/screen", "/api/news/scan", "/docs"]}

@app.get("/dalal-street-ai.apk")
def download_apk():
    """Serve Dalal Street AI Android APK directly."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(app_dir, "dalal-street-ai.apk"),
        os.path.join(app_dir, "public_html", "dalal-street-ai.apk"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return FileResponse(p, filename="dalal-street-ai.apk", media_type="application/vnd.android.package-archive")
    raise HTTPException(status_code=404, detail="APK file not found")

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "Dalal Street AI", "version": "1.1.0"}

@app.get("/api/fii-dii")
def get_fii_dii():
    """Fetch live provisional institutional cash activity from NSE."""
    return fetch_fii_dii_activity()

@app.get("/api/news")
def get_news(ticker: Optional[str] = None):
    """Fetch latest Indian financial news from RSS feeds."""
    news = fetch_all_market_news(limit_per_feed=8)
    if ticker:
        matched = find_news_for_ticker(ticker, news)
        return {"total": len(matched), "news": matched}
    return {"total": len(news), "news": news}

@app.get("/api/news/scan")
def get_scanned_news(limit: int = 15):
    """Scan live market news on mobile/app launch, identifying stock catalysts and macro headlines."""
    from data_ingestion.news_feed import scan_market_news
    return scan_market_news(limit_per_feed=limit)


@app.get("/api/screen")
def screen_stocks(
    universe: str = Query("largecap", description="Universe: 'largecap', 'penny', or 'all'"),
    capital: float = Query(DEFAULT_CAPITAL_INR, description="Portfolio capital in INR"),
    min_score: float = Query(50.0, description="Minimum setup score (0-100)")
):
    """Scan and rank Indian equities."""
    screened = run_screener(universe=universe, account_capital_inr=capital, min_score=min_score)
    return {"universe": universe, "count": len(screened), "stocks": screened}

@app.get("/api/chart/{symbol}")
def get_chart_data(symbol: str, period: str = "6mo"):
    """Fetch candlestick OHLC data formatted for TradingView Lightweight

    Charts.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval="1d")
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No chart data found for {symbol}")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()

        candlesticks = []
        ema_50_line = []
        ema_200_line = []

        for date, row in df.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            candlesticks.append({
                "time": date_str,
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
            })
            if not pd.isna(row["EMA_50"]):
                ema_50_line.append({"time": date_str, "value": round(float(row["EMA_50"]), 2)})
            if not pd.isna(row["EMA_200"]):
                ema_200_line.append({"time": date_str, "value": round(float(row["EMA_200"]), 2)})

        return {
            "symbol": symbol,
            "candlesticks": candlesticks,
            "ema_50": ema_50_line,
            "ema_200": ema_200_line,
        }
    except Exception as e:
        logger.error(f"Error fetching chart data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/debate")
def run_debate(req: DebateRequest):
    """Trigger live AI Investment Committee debate for a selected stock."""
    profile = fetch_stock_technical_profile(req.symbol)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Could not load technical profile for {req.symbol}")

    all_news = fetch_all_market_news(limit_per_feed=6)
    stock_news = find_news_for_ticker(req.symbol, all_news)
    fii_dii = fetch_fii_dii_activity()

    sentiment = analyze_stock_sentiment(req.symbol, stock_news, preferred_provider=req.llm)
    debate = run_bull_bear_debate(
        symbol=req.symbol,
        technical_profile=profile,
        sentiment_data=sentiment,
        fii_dii_flow=fii_dii,
        preferred_provider=req.llm
    )

    return {
        "symbol": req.symbol,
        "sentiment": sentiment,
        "debate": debate,
        "fii_dii": fii_dii,
    }

@app.get("/api/calculate-size")
def calculate_size(
    entry_price: float,
    atr_14: float,
    capital: float = DEFAULT_CAPITAL_INR,
    risk_pct: float = 1.0,
    max_alloc_pct: float = 15.0
):
    """Dynamic position sizing calculator endpoint."""
    return calculate_inr_position(
        entry_price=entry_price,
        atr_14=atr_14,
        account_capital_inr=capital,
        risk_per_trade_pct=risk_pct,
        max_allocation_pct=max_alloc_pct
    )

# ----------------- SIMULATION / PAPER TRADING ENDPOINTS -----------------

@app.get("/api/simulation/portfolio")
def get_simulation_portfolio():
    """Get active virtual portfolio with live P&L and metrics."""
    portfolio_raw = simulation.load_portfolio()
    
    # Fetch live price updates for active positions
    live_prices: Dict[str, float] = {}
    for sym in portfolio_raw.get("positions", {}).keys():
        try:
            profile = fetch_stock_technical_profile(sym, period="5d")
            if profile and profile.get("current_price"):
                live_prices[sym] = profile["current_price"]
        except Exception:
            pass

    return simulation.get_portfolio_status(live_prices=live_prices)

@app.post("/api/simulation/buy")
def simulation_buy(order: BuyOrderRequest):
    """Simulate a paper buy order."""
    res = simulation.execute_buy(
        symbol=order.symbol,
        shares=order.shares,
        price=order.price,
        stop_loss=order.stop_loss,
        target_1=order.target_1,
        target_2=order.target_2,
        ai_score=order.ai_score or 0.0,
        ai_verdict=order.ai_verdict or "BUY"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@app.post("/api/simulation/sell")
def simulation_sell(order: SellOrderRequest):
    """Simulate a paper sell / close position order."""
    res = simulation.execute_sell(
        symbol=order.symbol,
        exit_price=order.exit_price,
        shares_to_sell=order.shares,
        reason=order.reason or "Manual Exit"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@app.post("/api/simulation/reset")
def simulation_reset(req: ResetPortfolioRequest):
    """Reset virtual portfolio back to initial cash."""
    return simulation.reset_portfolio(initial_cash=req.initial_cash or 500000.0)

def get_local_ip() -> str:
    """Detect machine's local LAN IPv4 address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    import uvicorn
    local_ip = get_local_ip()
    print("=" * 60)
    print(f"🚀 Dalal Street AI Backend running at:")
    print(f"   Local PC:    http://127.0.0.1:8000")
    print(f"   Phone/LAN:   http://{local_ip}:8000")
    print("=" * 60)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
