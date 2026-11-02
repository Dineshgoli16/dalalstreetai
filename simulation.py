"""Paper Trading & Trade Simulation Engine for Dalal Street AI.

Tracks virtual cash, active positions, realized/unrealized P&L, and trade
performance analytics with persistent JSON storage.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "simulation_portfolio.json")

DEFAULT_VIRTUAL_CAPITAL = 500000.0  # ₹5,00,000

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_portfolio() -> Dict[str, Any]:
    """Load virtual portfolio from disk or initialize default."""
    _ensure_data_dir()
    if not os.path.exists(PORTFOLIO_FILE):
        default_state = {
            "initial_cash_inr": DEFAULT_VIRTUAL_CAPITAL,
            "cash_inr": DEFAULT_VIRTUAL_CAPITAL,
            "positions": {},  # symbol -> position dict
            "history": [],    # list of closed trades
        }
        save_portfolio(default_state)
        return default_state

    try:
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading portfolio file: {e}")
        return {
            "initial_cash_inr": DEFAULT_VIRTUAL_CAPITAL,
            "cash_inr": DEFAULT_VIRTUAL_CAPITAL,
            "positions": {},
            "history": [],
        }

def save_portfolio(portfolio: Dict[str, Any]):
    """Save virtual portfolio state to disk."""
    _ensure_data_dir()
    try:
        with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
            json.dump(portfolio, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving portfolio file: {e}")

def execute_buy(
    symbol: str,
    shares: int,
    price: float,
    stop_loss: Optional[float] = None,
    target_1: Optional[float] = None,
    target_2: Optional[float] = None,
    ai_score: float = 0.0,
    ai_verdict: str = "BUY"
) -> Dict[str, Any]:
    """Execute a simulated paper buy order."""
    if shares <= 0:
        return {"success": False, "message": "Shares must be greater than zero."}
    if price <= 0:
        return {"success": False, "message": "Price must be positive."}

    portfolio = load_portfolio()
    total_cost = shares * price

    if total_cost > portfolio["cash_inr"]:
        return {
            "success": False,
            "message": f"Insufficient virtual cash. Needed: ₹{total_cost:,.2f}, Available: ₹{portfolio['cash_inr']:,.2f}"
        }

    # Deduct cash
    portfolio["cash_inr"] -= total_cost

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # If position already exists, average it
    if symbol in portfolio["positions"]:
        pos = portfolio["positions"][symbol]
        new_shares = pos["shares"] + shares
        new_cost = pos["total_cost"] + total_cost
        avg_price = new_cost / new_shares
        
        pos["shares"] = new_shares
        pos["total_cost"] = round(new_cost, 2)
        pos["entry_price"] = round(avg_price, 2)
        pos["last_updated"] = now_str
        pos["stop_loss"] = stop_loss or pos.get("stop_loss")
        pos["target_1"] = target_1 or pos.get("target_1")
    else:
        portfolio["positions"][symbol] = {
            "symbol": symbol,
            "shares": shares,
            "entry_price": round(price, 2),
            "entry_time": now_str,
            "total_cost": round(total_cost, 2),
            "stop_loss": round(stop_loss, 2) if stop_loss else None,
            "target_1": round(target_1, 2) if target_1 else None,
            "target_2": round(target_2, 2) if target_2 else None,
            "ai_score": ai_score,
            "ai_verdict": ai_verdict,
        }

    save_portfolio(portfolio)
    return {
        "success": True,
        "message": f"Successfully simulated BUY of {shares} shares of {symbol} at ₹{price:,.2f}.",
        "position": portfolio["positions"][symbol],
        "remaining_cash_inr": round(portfolio["cash_inr"], 2)
    }

def execute_sell(
    symbol: str,
    exit_price: float,
    shares_to_sell: Optional[int] = None,
    reason: str = "Manual Exit"
) -> Dict[str, Any]:
    """Execute a simulated paper sell / close order."""
    portfolio = load_portfolio()
    
    if symbol not in portfolio["positions"]:
        return {"success": False, "message": f"No active position found for {symbol}."}

    pos = portfolio["positions"][symbol]
    total_held = pos["shares"]
    sell_qty = total_held if (shares_to_sell is None or shares_to_sell >= total_held) else shares_to_sell

    revenue = sell_qty * exit_price
    cost_basis = sell_qty * pos["entry_price"]
    pnl = revenue - cost_basis
    return_pct = (pnl / cost_basis) * 100.0 if cost_basis > 0 else 0.0

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add to closed trade history
    trade_record = {
        "symbol": symbol,
        "shares": sell_qty,
        "entry_price": pos["entry_price"],
        "exit_price": round(exit_price, 2),
        "entry_time": pos["entry_time"],
        "exit_time": now_str,
        "cost_basis_inr": round(cost_basis, 2),
        "revenue_inr": round(revenue, 2),
        "pnl_inr": round(pnl, 2),
        "return_pct": round(return_pct, 2),
        "reason": reason,
        "ai_score": pos.get("ai_score", 0.0),
        "ai_verdict": pos.get("ai_verdict", "BUY")
    }
    portfolio["history"].insert(0, trade_record)

    # Credit cash
    portfolio["cash_inr"] += revenue

    # Update or remove position
    if sell_qty >= total_held:
        del portfolio["positions"][symbol]
    else:
        pos["shares"] -= sell_qty
        pos["total_cost"] = round(pos["shares"] * pos["entry_price"], 2)

    save_portfolio(portfolio)
    return {
        "success": True,
        "message": f"Closed {sell_qty} shares of {symbol} at ₹{exit_price:,.2f} ({return_pct:+.2f}%).",
        "trade": trade_record,
        "remaining_cash_inr": round(portfolio["cash_inr"], 2)
    }

def reset_portfolio(initial_cash: float = DEFAULT_VIRTUAL_CAPITAL) -> Dict[str, Any]:
    """Reset virtual portfolio back to clean state."""
    portfolio = {
        "initial_cash_inr": initial_cash,
        "cash_inr": initial_cash,
        "positions": {},
        "history": [],
    }
    save_portfolio(portfolio)
    return {"success": True, "message": f"Portfolio reset to ₹{initial_cash:,.2f}."}

def get_portfolio_status(live_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Get active portfolio summary, unrealized P&L, and trade analytics."""
    portfolio = load_portfolio()
    prices = live_prices or {}

    total_invested = 0.0
    total_unrealized_pnl = 0.0
    positions_list = []

    for sym, pos in portfolio["positions"].items():
        curr_price = prices.get(sym, pos["entry_price"])
        market_val = pos["shares"] * curr_price
        pos_pnl = market_val - pos["total_cost"]
        pos_pnl_pct = (pos_pnl / pos["total_cost"]) * 100.0 if pos["total_cost"] > 0 else 0.0

        total_invested += pos["total_cost"]
        total_unrealized_pnl += pos_pnl

        positions_list.append({
            **pos,
            "current_price": round(curr_price, 2),
            "market_value_inr": round(market_val, 2),
            "unrealized_pnl_inr": round(pos_pnl, 2),
            "unrealized_pnl_pct": round(pos_pnl_pct, 2)
        })

    # Trade Analytics on History
    history = portfolio.get("history", [])
    total_closed = len(history)
    wins = [t for t in history if t["pnl_inr"] > 0]
    losses = [t for t in history if t["pnl_inr"] < 0]
    
    total_realized_pnl = sum(t["pnl_inr"] for t in history)
    win_rate = (len(wins) / total_closed * 100.0) if total_closed > 0 else 0.0

    gross_profit = sum(t["pnl_inr"] for t in wins)
    gross_loss = abs(sum(t["pnl_inr"] for t in losses))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)

    best_trade_pct = max([t["return_pct"] for t in history], default=0.0)
    worst_trade_pct = min([t["return_pct"] for t in history], default=0.0)
    avg_return_pct = round(sum(t["return_pct"] for t in history) / total_closed, 2) if total_closed > 0 else 0.0

    current_net_worth = portfolio["cash_inr"] + total_invested + total_unrealized_pnl
    total_portfolio_return_pct = ((current_net_worth - portfolio["initial_cash_inr"]) / portfolio["initial_cash_inr"]) * 100.0

    return {
        "initial_cash_inr": round(portfolio["initial_cash_inr"], 2),
        "cash_inr": round(portfolio["cash_inr"], 2),
        "invested_inr": round(total_invested, 2),
        "current_net_worth_inr": round(current_net_worth, 2),
        "total_portfolio_return_pct": round(total_portfolio_return_pct, 2),
        "total_unrealized_pnl_inr": round(total_unrealized_pnl, 2),
        "total_realized_pnl_inr": round(total_realized_pnl, 2),
        "positions": positions_list,
        "history": history[:20], # Most recent 20 closed trades
        "analytics": {
            "total_trades": total_closed,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": round(win_rate, 1),
            "profit_factor": profit_factor,
            "best_trade_pct": round(best_trade_pct, 2),
            "worst_trade_pct": round(worst_trade_pct, 2),
            "avg_return_pct": avg_return_pct,
        }
    }
