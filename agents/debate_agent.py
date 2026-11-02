"""Bull vs Bear Investment Committee Debate & Portfolio Manager Synthesis Agent

for Indian Equities.
"""

import json
import logging
from typing import Dict, Any, Optional
from agents.llm_client import generate_ai_completion

logger = logging.getLogger(__name__)

DEBATE_SYSTEM_PROMPT = """You are an elite Investment Committee managing an Indian Equity fund (NSE).
You consist of three roles:
1. Bull Analyst: Identifies technical breakout triggers, volume spikes, and upside momentum.
2. Bear Analyst: The devil's advocate. Scrutinizes macro risks, FII outflows, valuation, and overhead resistance.
3. Portfolio Manager: Synthesizes the debate into a single definitive trading verdict.

You must output strictly valid JSON matching this schema:
{
  "bull_case": "2 concise sentences on the strongest reasons to buy now",
  "bear_case": "2 concise sentences on the biggest risks or reasons to hesitate",
  "portfolio_manager_verdict": "STRONG BUY" | "BUY" | "ACCUMULATE ON DIP" | "AVOID",
  "conviction": "HIGH" | "MEDIUM" | "SPECULATIVE",
  "execution_guidance": "1 actionable sentence on how to enter (e.g., market order, wait for retest of 20 EMA, etc.)"
}
"""

def run_bull_bear_debate(
    symbol: str,
    technical_profile: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    fii_dii_flow: Dict[str, Any],
    preferred_provider: Optional[str] = None
) -> Dict[str, Any]:
    """Run a structured Bull vs Bear debate and synthesize a definitive verdict

    for an Indian equity setup.
    """
    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    
    price = technical_profile.get("current_price")
    rsi = technical_profile.get("rsi_14")
    vol_surge = technical_profile.get("volume_surge_ratio")
    ema_50 = technical_profile.get("ema_50")
    ema_200 = technical_profile.get("ema_200")
    
    sentiment_label = sentiment_data.get("sentiment_label", "Neutral")
    fii_net = fii_dii_flow.get("fii_net_cr", 0.0)
    dii_net = fii_dii_flow.get("dii_net_cr", 0.0)

    user_prompt = f"""Evaluate Stock: {clean_sym} (NSE India)

Market & Quantitative Profile:
- Current Price: ₹{price:,.2f}
- 14-day RSI: {rsi}
- Volume Surge: {vol_surge}x of 20-DMA
- 50 EMA: ₹{ema_50} | 200 EMA: ₹{ema_200}
- News Sentiment: {sentiment_label} (Catalysts: {', '.join(sentiment_data.get('catalysts', []))})
- Macro Institutional Flow: FII Net = ₹{fii_net:+,.2f} Cr, DII Net = ₹{dii_net:+,.2f} Cr

Conduct the Bull vs Bear debate and provide the Portfolio Manager's verdict. Output strictly valid JSON."""

    raw_response = generate_ai_completion(
        prompt=user_prompt,
        system_prompt=DEBATE_SYSTEM_PROMPT,
        preferred_provider=preferred_provider
    )

    if raw_response and raw_response != "__NO_API_KEY__":
        try:
            cleaned = raw_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            data["source"] = f"LLM Investment Committee ({preferred_provider or 'Active AI'})"
            return data
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON debate response: {e}. Raw: {raw_response[:100]}")

    # Deterministic Heuristic Synthesis when API key is not yet set
    is_fii_selling = fii_net < -1000
    is_rsi_high = rsi > 65
    is_strong_trend = price > ema_50 and ema_50 > ema_200

    bull_points = f"{clean_sym} is demonstrating firm technical leadership trading above its key 50 and 200 EMAs with healthy {vol_surge}x volume accumulation."
    if vol_surge > 1.2:
        bull_points += " Above-average delivery volume confirms institutional interest on dips."

    bear_points = f"Broader market faces headline drag with net FII selling of ₹{abs(fii_net):,.0f} Cr."
    if is_rsi_high:
        bear_points += f" Short-term RSI of {rsi} suggests near-term consolidation may occur before the next leg up."
    else:
        bear_points += " Any sudden index-level gap down could temporarily test trailing support."

    if is_strong_trend and not is_rsi_high:
        verdict = "STRONG BUY"
        conviction = "HIGH"
        guidance = f"Enter initial position near ₹{price:,.2f} with trailing stop-loss strictly maintained."
    elif is_strong_trend and is_rsi_high:
        verdict = "ACCUMULATE ON DIP"
        conviction = "MEDIUM"
        guidance = f"Do not chase at current highs; place limit orders closer to 20 EMA (₹{technical_profile.get('ema_20')})."
    else:
        verdict = "BUY"
        conviction = "MEDIUM"
        guidance = "Scale in with 50% initial sizing; add remainder once breakout is confirmed on daily close."

    return {
        "bull_case": bull_points,
        "bear_case": bear_points,
        "portfolio_manager_verdict": verdict,
        "conviction": conviction,
        "execution_guidance": guidance,
        "source": "Rule-Based Committee Engine (Set GEMINI_API_KEY in .env for full LLM debate)"
    }
