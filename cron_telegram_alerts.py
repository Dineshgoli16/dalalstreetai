"""Autonomous 24/7 Market Screener & Telegram Alert Daemon for cPanel Cron Jobs.

Runs periodically via cPanel Cron (e.g. every 15-30 minutes during NSE market hours:
09:15 - 15:30 IST) to scan the market, calculate technical indicators, FII/DII flows,
and broadcast high-probability trade setups to a Telegram Bot or Channel.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

# Ensure local modules resolve properly
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

load_dotenv(os.path.join(APP_DIR, ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from data_ingestion.smart_money import fetch_fii_dii_activity
from screening.screener import run_screener
from data_ingestion.news_feed import fetch_all_market_news, find_news_for_ticker
from risk.position_sizer import calculate_inr_position


def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    """Send formatted HTML message to Telegram via Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200:
            logger.info("Telegram notification delivered successfully.")
            return True
        else:
            logger.error(f"Failed to send Telegram message: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram network error: {e}")
        return False


def run_market_alert(dry_run: bool = False, universe: str = "all") -> str:
    """Execute market scan and generate formatted alert."""
    now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
    
    # 1. Fetch FII/DII Institutional Flow
    fii_dii = fetch_fii_dii_activity()
    fii_net = fii_dii.get("fii_net_cr", 0.0)
    dii_net = fii_dii.get("dii_net_cr", 0.0)
    combined = fii_dii.get("combined_net_cr", 0.0)
    market_bias = fii_dii.get("sentiment", "Neutral").upper()
    bias_emoji = "🟢" if combined >= 0 else "🔴"

    # 2. Run Screener for high-probability setups
    logger.info(f"Scanning {universe} stocks for setups...")
    ranked_stocks = run_screener(universe=universe, account_capital_inr=500000.0, min_score=40.0)

    lines = []
    lines.append(f"📊 <b>DALAL STREET AI MARKET ALERT</b>")
    lines.append(f"⏱ <i>{now_str} IST</i>\n")
    
    # Smart Money Section
    lines.append(f"<b>🏛 Smart Money Flow (FII/DII):</b>")
    lines.append(f"• FII Net: <b>{'₹' if fii_net < 0 else '+₹'}{fii_net:,.1f} Cr</b>")
    lines.append(f"• DII Net: <b>{'₹' if dii_net < 0 else '+₹'}{dii_net:,.1f} Cr</b>")
    lines.append(f"• Bias: {bias_emoji} <b>{market_bias}</b> (Net: {'₹' if combined < 0 else '+₹'}{combined:,.1f} Cr)\n")

    # Top Ranked Opportunities
    if ranked_stocks:
        lines.append(f"<b>🎯 Top Screened Opportunities ({len(ranked_stocks)} Found):</b>\n")
        
        # Display top 3
        top_candidates = ranked_stocks[:3]
        for idx, stock in enumerate(top_candidates, 1):
            sym = stock.get("symbol", "")
            price = stock.get("current_price", 0.0)
            score = stock.get("score", 0.0)
            tech = stock.get("technical_profile", {})
            rsi = tech.get("rsi_14", 0.0)
            vol_surge = tech.get("volume_surge_ratio", 1.0)
            sizing = stock.get("sizing", {})
            sl = sizing.get("stop_loss", 0.0)
            t1 = sizing.get("target_1", 0.0)
            shares = sizing.get("shares_recommended", 0)

            score_badge = "🔥 STRONG BUY" if score >= 75 else ("⚡ BUY" if score >= 60 else "👀 WATCH")
            penny_tag = " [Penny Stock]" if stock.get("is_penny_stock") else ""

            lines.append(f"<b>{idx}. {sym}</b>{penny_tag} - {score_badge}")
            lines.append(f"   • Price: <b>₹{price:,.2f}</b> | Score: <b>{score:.1f}/100</b>")
            lines.append(f"   • RSI: {rsi:.1f} | Volume Surge: {vol_surge:.2f}x")
            if sl > 0 and t1 > 0:
                lines.append(f"   • SL: <b>₹{sl:,.2f}</b> | TGT: <b>₹{t1:,.2f}</b> | Sizing: {shares} shares")
            lines.append("")
    else:
        lines.append("<i>No high-conviction breakout setups passed the filter at this moment.</i>\n")

    # Footer note
    lines.append("⚡ <i>Automated from Dalal Street AI cPanel Daemon</i>")
    
    full_message = "\n".join(lines)
    
    # Send or Print
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if dry_run or not token or not chat_id:
        logger.info("=== DRY RUN ALERT MESSAGE ===")
        print(full_message)
        if not token or not chat_id:
            logger.info("Tip: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env or cPanel to receive this in Telegram.")
    else:
        logger.info(f"Dispatching alert to Telegram Chat ID: {chat_id}")
        send_telegram_message(token, chat_id, full_message)
        
    return full_message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dalal Street AI Telegram Cron Alert")
    parser.add_argument("--dry-run", action="store_true", help="Print alert to console instead of sending to Telegram")
    parser.add_argument("--universe", default="all", choices=["largecap", "penny", "all"], help="Stock universe to scan")
    args = parser.parse_args()

    run_market_alert(dry_run=args.dry_run, universe=args.universe)
