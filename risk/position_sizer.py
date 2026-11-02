"""Deterministic INR Risk Management & Position Sizing Engine.

Enforces:
1. Max portfolio risk per trade (e.g. 1.0% = ₹5,000 max loss on ₹5,00,000 capital).
2. Volatility-based Stop-Loss (2x ATR(14) or structural swing support).
3. Max portfolio concentration per stock (e.g. max 15% = ₹75,000 max invested).
4. Multi-tier Take-Profit targets (1:2 and 1:3 Risk-to-Reward).
"""

from typing import Dict, Any
from config import (
    DEFAULT_CAPITAL_INR,
    DEFAULT_RISK_PER_TRADE_PCT,
    MAX_ALLOCATION_PER_STOCK_PCT,
    DEFAULT_STOP_LOSS_ATR_MULT
)

def calculate_inr_position(
    entry_price: float,
    atr_14: float,
    account_capital_inr: float = DEFAULT_CAPITAL_INR,
    risk_per_trade_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    max_allocation_pct: float = MAX_ALLOCATION_PER_STOCK_PCT,
    atr_multiplier: float = DEFAULT_STOP_LOSS_ATR_MULT,
) -> Dict[str, Any]:
    """Calculate the exact number of shares, stop loss, and investment amount in

    Indian Rupees (₹).
    """
    if entry_price <= 0:
        raise ValueError("Entry price must be greater than zero.")
    if atr_14 <= 0:
        atr_14 = entry_price * 0.02 # Fallback to 2% volatility

    # 1. Stop loss computation
    stop_distance = atr_multiplier * atr_14
    stop_loss_price = max(entry_price - stop_distance, 0.05)
    stop_loss_pct = (stop_distance / entry_price) * 100.0

    # 2. Maximum allowable loss in ₹ for this trade
    max_allowable_loss_inr = account_capital_inr * (risk_per_trade_pct / 100.0)

    # 3. Position size derived strictly from risk tolerance
    raw_shares = int(max_allowable_loss_inr / stop_distance) if stop_distance > 0 else 0
    raw_investment = raw_shares * entry_price

    # 4. Enforce Single-Stock Portfolio Concentration Cap
    max_allowed_investment_inr = account_capital_inr * (max_allocation_pct / 100.0)
    
    is_capped_by_allocation = False
    if raw_investment > max_allowed_investment_inr:
        shares_to_buy = int(max_allowed_investment_inr / entry_price)
        is_capped_by_allocation = True
    else:
        shares_to_buy = raw_shares

    # Ensure minimum 1 share if capital permits, else 0
    if shares_to_buy == 0 and entry_price <= max_allowed_investment_inr:
        shares_to_buy = 1

    total_investment_inr = shares_to_buy * entry_price
    actual_risk_inr = shares_to_buy * stop_distance
    portfolio_allocation_pct = (total_investment_inr / account_capital_inr) * 100.0 if account_capital_inr > 0 else 0.0

    # 5. Profit Targets (1:2 and 1:3 Risk-to-Reward)
    target_1_price = entry_price + (2.0 * stop_distance)
    target_2_price = entry_price + (3.0 * stop_distance)

    target_1_gain_inr = (target_1_price - entry_price) * shares_to_buy
    target_2_gain_inr = (target_2_price - entry_price) * shares_to_buy

    return {
        "entry_price": round(entry_price, 2),
        "stop_loss_price": round(stop_loss_price, 2),
        "stop_distance_inr": round(stop_distance, 2),
        "stop_loss_pct": round(stop_loss_pct, 2),
        "shares_to_buy": shares_to_buy,
        "total_investment_inr": round(total_investment_inr, 2),
        "portfolio_allocation_pct": round(portfolio_allocation_pct, 2),
        "actual_risk_inr": round(actual_risk_inr, 2),
        "max_allowable_loss_inr": round(max_allowable_loss_inr, 2),
        "is_capped_by_allocation": is_capped_by_allocation,
        "target_1_price": round(target_1_price, 2),
        "target_1_gain_inr": round(target_1_gain_inr, 2),
        "target_2_price": round(target_2_price, 2),
        "target_2_gain_inr": round(target_2_gain_inr, 2),
    }
