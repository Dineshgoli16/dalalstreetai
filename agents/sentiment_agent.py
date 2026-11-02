"""News & Sentiment Analysis Agent for Indian Equities."""

import json
import logging
from typing import Dict, List, Any, Optional
from agents.llm_client import generate_ai_completion

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior equity research analyst covering the Indian stock market (NSE/BSE).
Your job is to analyze real-time financial news, broker ratings, and corporate filings to assess the net market sentiment for a specific stock.
Output your response strictly as valid JSON matching this schema:
{
  "sentiment_score": float between -1.0 and 1.0,
  "sentiment_label": "Bullish" | "Neutral" | "Bearish",
  "catalysts": ["catalyst 1", "catalyst 2"],
  "risks": ["risk 1", "risk 2"],
  "summary": "1-2 sentence executive assessment"
}
"""

def analyze_stock_sentiment(
    symbol: str,
    news_items: List[Dict[str, Any]],
    preferred_provider: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze sentiment of news headlines for a given Indian stock using Gemini

    or Claude.
    """
    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    
    if not news_items:
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "Neutral",
            "catalysts": ["No recent breaking company-specific headlines."],
            "risks": ["General market volatility."],
            "summary": f"No company-specific news detected for {clean_sym}; trading primarily on technical momentum and sector trends.",
            "source": "Heuristic Default"
        }

    # Format news items for prompt
    news_text = ""
    for idx, item in enumerate(news_items[:4], start=1):
        news_text += f"{idx}. [{item.get('source')}] {item.get('title')}\n   Summary: {item.get('summary')}\n\n"

    user_prompt = f"""Target Stock: {clean_sym} (NSE)

Recent News & Broker Reports:
{news_text}

Analyze the news above for {clean_sym}. Output strictly valid JSON."""

    raw_response = generate_ai_completion(
        prompt=user_prompt,
        system_prompt=SYSTEM_PROMPT,
        preferred_provider=preferred_provider
    )

    if raw_response and raw_response != "__NO_API_KEY__":
        try:
            # Strip markdown json code fences if present
            cleaned = raw_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            data["source"] = f"LLM ({preferred_provider or 'Active AI'})"
            return data
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON sentiment response: {e}. Raw: {raw_response[:100]}")

    # Intelligent Heuristic Fallback when API key is not yet set
    positive_words = ["buy", "upgrade", "growth", "profit", "beat", "dividend", "order", "expansion", "surge"]
    negative_words = ["reduce", "sell", "downgrade", "fall", "loss", "drop", "penalty", "sebi", "probe", "cut"]

    score = 0.0
    catalysts = []
    risks = []

    combined_text = " ".join([item.get("title", "") + " " + item.get("summary", "") for item in news_items]).lower()

    for word in positive_words:
        if word in combined_text:
            score += 0.2
    for word in negative_words:
        if word in combined_text:
            score -= 0.25

    score = max(-1.0, min(1.0, round(score, 2)))
    
    if score > 0.15:
        label = "Bullish"
        catalysts.append("Positive broker recommendations or earnings optimism.")
    elif score < -0.15:
        label = "Bearish"
        risks.append("Negative analyst revisions or short-term headwinds.")
    else:
        label = "Neutral"

    return {
        "sentiment_score": score,
        "sentiment_label": label,
        "catalysts": catalysts or ["Steady sector performance."],
        "risks": risks or ["Macro interest rate / FII sensitivity."],
        "summary": f"News flow reflects {label.lower()} undertone based on recent broker commentaries.",
        "source": "Heuristic Analyzer (Set GEMINI_API_KEY in .env for full AI reasoning)"
    }
