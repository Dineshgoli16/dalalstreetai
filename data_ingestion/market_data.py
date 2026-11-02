"""Market data fetching and technical indicator computation for Indian stocks (NSE/BSE)."""

import logging
from typing import Dict, Optional, Any
import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    # Use exponential moving average (Wilder's RSI)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)."""
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    return atr

def fetch_stock_technical_profile(symbol: str, period: str = "1y") -> Optional[Dict[str, Any]]:
    """Fetch historical daily data for an Indian stock (e.g.

    'RELIANCE.NS') and compute technical indicators.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval="1d")
        
        if df.empty or len(df) < 50:
            logger.warning(f"Insufficient historical data for {symbol}")
            return None
            
        # Clean multi-index columns if returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Technical Indicators
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['RSI_14'] = calculate_rsi(df['Close'], period=14)
        df['ATR_14'] = calculate_atr(df, period=14)
        df['VOL_SMA_20'] = df['Volume'].rolling(window=20).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest

        current_price = float(latest['Close'])
        prev_close = float(prev['Close'])
        pct_change = ((current_price - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

        ema_20 = float(latest['EMA_20']) if not pd.isna(latest['EMA_20']) else current_price
        ema_50 = float(latest['EMA_50']) if not pd.isna(latest['EMA_50']) else current_price
        ema_200 = float(latest['EMA_200']) if not pd.isna(latest['EMA_200']) else current_price
        rsi_14 = float(latest['RSI_14']) if not pd.isna(latest['RSI_14']) else 50.0
        atr_14 = float(latest['ATR_14']) if not pd.isna(latest['ATR_14']) else (current_price * 0.02)
        
        vol_current = float(latest['Volume'])
        vol_sma_20 = float(latest['VOL_SMA_20']) if not pd.isna(latest['VOL_SMA_20']) and latest['VOL_SMA_20'] > 0 else vol_current
        vol_surge_ratio = vol_current / vol_sma_20 if vol_sma_20 > 0 else 1.0

        high_52w = float(df['High'].max())
        low_52w = float(df['Low'].min())

        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "prev_close": round(prev_close, 2),
            "pct_change": round(pct_change, 2),
            "ema_20": round(ema_20, 2),
            "ema_50": round(ema_50, 2),
            "ema_200": round(ema_200, 2),
            "rsi_14": round(rsi_14, 2),
            "atr_14": round(atr_14, 2),
            "volume_today": int(vol_current),
            "volume_sma_20": int(vol_sma_20),
            "volume_surge_ratio": round(vol_surge_ratio, 2),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "is_above_200_ema": bool(current_price > ema_200),
            "is_above_50_ema": bool(current_price > ema_50),
            "is_golden_cross": bool(ema_50 > ema_200),
        }
    except Exception as e:
        logger.error(f"Error computing technicals for {symbol}: {e}")
        return None
