"""Indian financial news scraper and RSS ingestion module."""

import logging
from typing import Dict, List, Any
import feedparser
from config import RSS_FEEDS, TICKER_KEYWORD_MAP

logger = logging.getLogger(__name__)

def fetch_all_market_news(limit_per_feed: int = 10) -> List[Dict[str, Any]]:
    """Fetch recent Indian market news from configured RSS feeds (Moneycontrol,

    Economic Times, LiveMint).
    """
    all_news = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            entries = parsed.entries[:limit_per_feed]
            
            for entry in entries:
                published = entry.get("published", entry.get("updated", "Recent"))
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link", "")

                # Clean all HTML tags from summary (img, a, p, etc.)
                import re
                clean_summary = re.sub(r'<[^>]+>', ' ', summary)
                clean_summary = " ".join(clean_summary.split())
                
                all_news.append({
                    "source": source_name,
                    "title": title,
                    "summary": clean_summary[:280], # First 280 chars
                    "published": published,
                    "link": link
                })
        except Exception as e:
            logger.warning(f"Error fetching RSS feed '{source_name}': {e}")
            
    return all_news

def find_news_for_ticker(ticker: str, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter news items matching keywords for a specific Indian stock ticker."""
    keywords = TICKER_KEYWORD_MAP.get(ticker, [])
    # Default to base symbol without .NS if not in map
    if not keywords:
        clean_symbol = ticker.replace(".NS", "").replace(".BO", "")
        keywords = [clean_symbol]

    matched_news = []
    for item in news_list:
        text_to_search = (item.get("title", "") + " " + item.get("summary", "")).lower()
        if any(keyword.lower() in text_to_search for keyword in keywords):
            matched_news.append(item)
            
    return matched_news

def scan_market_news(limit_per_feed: int = 12) -> Dict[str, Any]:
    """Scan latest market news and cross-reference with all watchlist stocks.
    
    Returns categorized stock catalysts and broad market news.
    """
    from datetime import datetime
    all_news = fetch_all_market_news(limit_per_feed=limit_per_feed)
    
    tagged_news = []
    seen_titles = set()
    
    for item in all_news:
        title = item.get("title", "").strip()
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        matched_tickers = []
        text = (title + " " + item.get("summary", "")).lower()
        for ticker, keywords in TICKER_KEYWORD_MAP.items():
            if any(k.lower() in text for k in keywords):
                matched_tickers.append(ticker)
        
        item_copy = dict(item)
        item_copy["matched_tickers"] = matched_tickers
        tagged_news.append(item_copy)
        
    stock_catalysts = [item for item in tagged_news if item["matched_tickers"]]
    general_news = [item for item in tagged_news if not item["matched_tickers"]]
    
    return {
        "total": len(tagged_news),
        "catalysts": stock_catalysts,
        "market_news": general_news,
        "scanned_at": datetime.now().strftime("%I:%M %p, %d %b %Y")
    }

