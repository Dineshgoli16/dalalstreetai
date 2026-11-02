"""Main CLI runner for Dalal Street AI: Indian Stock Trading Multi-Agent

System.
"""

import sys
import os
import argparse

# Reconfigure stdout/stderr to UTF-8 to handle Indian Rupee symbol on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_CAPITAL_INR, WATCHLIST
from data_ingestion.smart_money import fetch_fii_dii_activity, fetch_bulk_deals
from data_ingestion.news_feed import fetch_all_market_news, find_news_for_ticker
from screening.screener import run_screener
from agents.sentiment_agent import analyze_stock_sentiment
from agents.debate_agent import run_bull_bear_debate

def print_banner():
    print("=" * 80)
    print("      DALAL STREET AI: INDIAN STOCK MARKET MULTI-AGENT SYSTEM         ")
    print("        Technical Screener + Smart Money + AI Bull/Bear Debate        ")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Dalal Street AI Trading Multi-Agent System")
    parser.add_argument("--capital", type=float, default=DEFAULT_CAPITAL_INR, help="Total account capital in INR ₹")
    parser.add_argument("--min-score", type=float, default=55.0, help="Minimum setup score (0-100) to display")
    parser.add_argument("--limit", type=int, default=3, help="Number of top setups to analyze with AI")
    parser.add_argument("--llm", type=str, choices=["gemini", "claude"], default="gemini", help="AI provider ('gemini' or 'claude')")
    args = parser.parse_args()

    print_banner()
    print(f"\n[+] Portfolio Capital : ₹{args.capital:,.2f}")
    print(f"[+] AI Engine Model   : {args.llm.upper()}")
    print("[+] Scanning liquid Indian equities (NSE)...")

    # 1. Institutional Flow / Smart Money Check
    print("\n" + "-" * 80)
    print("  [1] INSTITUTIONAL SMART MONEY FLOW (FII / DII)")
    print("-" * 80)
    fii_dii = fetch_fii_dii_activity()
    print(f"  Source: {fii_dii.get('source', 'NSE')} | Date: {fii_dii.get('date', 'Latest')}")
    print(f"  FII Net Cash : ₹{fii_dii.get('fii_net_cr', 0.0):+,.2f} Cr")
    print(f"  DII Net Cash : ₹{fii_dii.get('dii_net_cr', 0.0):+,.2f} Cr")
    print(f"  Combined Flow: ₹{fii_dii.get('combined_net_cr', 0.0):+,.2f} Cr")
    print(f"  Market Bias  : {fii_dii.get('sentiment', 'Neutral')}")

    # 2. Ingest Latest Indian Market News
    print("\n" + "-" * 80)
    print("  [2] FETCHING INDIAN FINANCIAL NEWS (Moneycontrol, ET, LiveMint)")
    print("-" * 80)
    news_items = fetch_all_market_news(limit_per_feed=8)
    print(f"  Ingested {len(news_items)} live headlines across Indian market feeds.")

    # 3. Run Screener & Risk Engine
    print("\n" + "-" * 80)
    print(f"  [3] SCREENING TOP SETUPS (Universe: {len(WATCHLIST)} Stocks)")
    print("-" * 80)
    screened_stocks = run_screener(tickers=WATCHLIST, account_capital_inr=args.capital, min_score=args.min_score)

    if not screened_stocks:
        print("  No stocks met the screening threshold today. Market may be consolidating.")
        return

    top_picks = screened_stocks[:args.limit]
    print(f"  Found {len(screened_stocks)} candidate stocks. Running AI Multi-Agent analysis on Top {len(top_picks)}:\n")

    for idx, pick in enumerate(top_picks, start=1):
        sym = pick["symbol"]
        clean_sym = sym.replace(".NS", "")
        score = pick["score"]
        action = pick["action"]
        price = pick["current_price"]
        pct = pick["pct_change"]
        tech = pick["technical_profile"]
        sizing = pick["sizing"]

        # Fetch matching news for this stock
        matching_news = find_news_for_ticker(sym, news_items)

        # AI Agent 1: News & Sentiment Agent
        sentiment_result = analyze_stock_sentiment(sym, matching_news, preferred_provider=args.llm)

        # AI Agent 2: Bull vs. Bear Investment Committee Debate
        debate_result = run_bull_bear_debate(
            symbol=sym,
            technical_profile=tech,
            sentiment_data=sentiment_result,
            fii_dii_flow=fii_dii,
            preferred_provider=args.llm
        )

        print(f"  #{idx}. {clean_sym} ({sym}) | Technical Score: {score}/100")
        print(f"      Current Price : ₹{price:,.2f} ({pct:+,.2f}%) | 52W High: ₹{tech['high_52w']:,.2f}")
        print(f"      Technicals    : RSI(14)={tech['rsi_14']} | 50 EMA=₹{tech['ema_50']} | 200 EMA=₹{tech['ema_200']}")
        print(f"      Volume Surge  : {tech['volume_surge_ratio']}x 20-DMA")
        print(f"      Checklist     : {', '.join(pick['checklist'])}")
        
        # News Sentiment Box
        print("      " + "." * 65)
        print(f"      AI NEWS & SENTIMENT ({sentiment_result.get('source', 'Analyzer')}):")
        print(f"      -> Net Sentiment : {sentiment_result.get('sentiment_label')} (Score: {sentiment_result.get('sentiment_score')})")
        print(f"      -> Summary       : {sentiment_result.get('summary')}")
        if sentiment_result.get("catalysts"):
            print(f"      -> Catalysts     : {'; '.join(sentiment_result.get('catalysts')[:2])}")
        if sentiment_result.get("risks"):
            print(f"      -> Risks         : {'; '.join(sentiment_result.get('risks')[:2])}")

        # Bull vs. Bear Debate Box
        print("      " + "." * 65)
        print("      AI INVESTMENT COMMITTEE DEBATE:")
        print(f"      [BULL CASE] : {debate_result.get('bull_case')}")
        print(f"      [BEAR CASE] : {debate_result.get('bear_case')}")
        print(f"      >> AI VERDICT     : {debate_result.get('portfolio_manager_verdict')} (Conviction: {debate_result.get('conviction')})")
        print(f"      >> EXECUTION RULE : {debate_result.get('execution_guidance')}")

        # Risk & Capital Allocation Box
        print("      " + "." * 65)
        print("      CAPITAL ALLOCATION & RISK MANAGEMENT (INR):")
        print(f"      -> Shares to Buy       : {sizing['shares_to_buy']} shares")
        print(f"      -> Total Investment    : ₹{sizing['total_investment_inr']:,.2f} ({sizing['portfolio_allocation_pct']}% of portfolio)")
        print(f"      -> Stop Loss           : ₹{sizing['stop_loss_price']:,.2f} (-{sizing['stop_loss_pct']}%)")
        print(f"      -> Max Loss on Trade   : ₹{sizing['actual_risk_inr']:,.2f}")
        print(f"      -> Target 1 (1:2 R:R)  : ₹{sizing['target_1_price']:,.2f} (+₹{sizing['target_1_gain_inr']:,.2f})")
        print(f"      -> Target 2 (1:3 R:R)  : ₹{sizing['target_2_price']:,.2f} (+₹{sizing['target_2_gain_inr']:,.2f})")
        if sizing["is_capped_by_allocation"]:
            print("      [!] Note: Position size was capped by 15% single-stock allocation limit.")
        
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
