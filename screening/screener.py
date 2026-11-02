"""Technical and quantitative screening engine for Indian equities."""

import logging
from typing import List, Dict, Any, Optional
from config import WATCHLIST, DEFAULT_CAPITAL_INR, DEFAULT_RISK_PER_TRADE_PCT, MAX_ALLOCATION_PER_STOCK_PCT
from data_ingestion.market_data import fetch_stock_technical_profile
from risk.position_sizer import calculate_inr_position

logger = logging.getLogger(__name__)

def evaluate_stock_setup(
    symbol: str,
    account_capital_inr: float = DEFAULT_CAPITAL_INR,
    risk_per_trade_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    max_allocation_pct: float = MAX_ALLOCATION_PER_STOCK_PCT
) -> Optional[Dict[str, Any]]:
    """Analyze a single stock's technical profile, grade its setup quality, and

    compute INR risk & sizing.
    """
    profile = fetch_stock_technical_profile(symbol)
    if not profile:
        return None

    current_price = profile["current_price"]
    ema_20 = profile["ema_20"]
    ema_50 = profile["ema_50"]
    ema_200 = profile["ema_200"]
    rsi = profile["rsi_14"]
    vol_ratio = profile["volume_surge_ratio"]
    high_52w = profile["high_52w"]
    atr = profile["atr_14"]

    # Filter Criteria
    # 1. Macro Trend: Price must be above 200 EMA & 50 EMA above 200 EMA
    is_uptrend = (current_price > ema_200) and (ema_50 >= ema_200 * 0.98)
    
    # 2. Momentum: RSI between 45 and 72
    is_momentum_healthy = 45.0 <= rsi <= 72.0
    
    # 3. Not overextended from 20 EMA (> 8% above 20 EMA is chasing)
    is_not_overextended = ((current_price - ema_20) / ema_20) < 0.08

    # Scoring Algorithm (0 - 100)
    score = 40.0
    checklist = []

    if current_price > ema_200:
        score += 15.0
        checklist.append("Above 200 EMA (Uptrend)")
    else:
        checklist.append("Below 200 EMA (Weak)")

    if current_price > ema_50:
        score += 10.0
        checklist.append("Above 50 EMA")
        
    if ema_20 > ema_50:
        score += 10.0
        checklist.append("Short-term EMA bullish cross")

    if 55.0 <= rsi <= 68.0:
        score += 15.0
        checklist.append(f"RSI in Bullish Sweet Spot ({rsi})")
    elif 45.0 <= rsi < 55.0:
        score += 5.0
        checklist.append(f"RSI Neutral/Consolidating ({rsi})")
    elif rsi > 70.0:
        checklist.append(f"RSI Overbought ({rsi})")
    else:
        checklist.append(f"RSI Weak ({rsi})")

    if vol_ratio >= 1.2:
        score += 15.0
        checklist.append(f"Volume Surge ({vol_ratio}x 20-DMA)")
    elif vol_ratio >= 0.9:
        score += 5.0
        checklist.append(f"Average Volume ({vol_ratio}x)")
    else:
        checklist.append(f"Low Volume ({vol_ratio}x)")

    # Proximity to 52-week high (Strength / Leadership filter)
    dist_from_52w_high_pct = ((high_52w - current_price) / high_52w) * 100.0
    if dist_from_52w_high_pct <= 5.0:
        score += 10.0
        checklist.append("Near 52-Week High (Relative Strength)")

    # Penny stock classification & safety checks
    is_penny_stock = current_price < 100.0
    if is_penny_stock:
        checklist.append("⚡ Penny / Pocket Stock (< ₹100)")
        if profile["volume_today"] < 300000:
            score -= 20.0
            checklist.append("⚠️ Low Penny Liquidity (Circuit Risk)")
        else:
            checklist.append("Liquid Volume")

    score = min(max(score, 0.0), 100.0)

    # Compute INR Position Sizing
    sizing = calculate_inr_position(
        entry_price=current_price,
        atr_14=atr,
        account_capital_inr=account_capital_inr,
        risk_per_trade_pct=risk_per_trade_pct,
        max_allocation_pct=max_allocation_pct
    )

    action = "STRONG BUY" if (score >= 75 and is_uptrend and is_momentum_healthy) else \
             "BUY" if (score >= 60 and is_uptrend) else \
             "WATCH" if (score >= 50) else "AVOID"

    return {
        "symbol": symbol,
        "score": round(score, 1),
        "action": action,
        "current_price": current_price,
        "pct_change": profile["pct_change"],
        "is_penny_stock": is_penny_stock,
        "checklist": checklist,
        "technical_profile": profile,
        "sizing": sizing,
    }

def run_screener(
    tickers: Optional[List[str]] = None,
    universe: str = "largecap",
    account_capital_inr: float = DEFAULT_CAPITAL_INR,
    min_score: float = 50.0
) -> List[Dict[str, Any]]:
    """Scan all tickers in the watchlist and return ranked setups."""
    from config import get_watchlist
    candidate_list = tickers or get_watchlist(universe)
    results = []
    
    for symbol in candidate_list:
        try:
            setup = evaluate_stock_setup(symbol, account_capital_inr=account_capital_inr)
            if setup and setup["score"] >= min_score:
                results.append(setup)
        except Exception as e:
            logger.error(f"Error evaluating {symbol}: {e}")

    # Sort candidates by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

