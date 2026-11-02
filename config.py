"""Configuration settings for Indian Stock AI Agent (NSE / BSE)."""

# Default Capital & Risk Settings (in INR ₹)
DEFAULT_CAPITAL_INR = 500000.0   # ₹5,00,000 initial portfolio
DEFAULT_RISK_PER_TRADE_PCT = 1.0 # 1.0% max loss of portfolio per trade (₹5,000)
MAX_ALLOCATION_PER_STOCK_PCT = 15.0 # Max 15% of portfolio in any single stock (₹75,000)
DEFAULT_STOP_LOSS_ATR_MULT = 2.0  # Stop loss placed at 2x ATR(14) below entry

# Liquid Watchlist: Core Nifty 50 & Active Indian Equities (NSE symbols with .NS)
LARGECAP_WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "BHARTIARTL.NS",
    "SBIN.NS",
    "M&M.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS",
    "BAJFINANCE.NS",
    "MARUTI.NS",
    "TITAN.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "ADANIENT.NS",
    "TATASTEEL.NS",
    "HAL.NS",
    "BEL.NS",
    "TRENT.NS",
]

# Active High-Volume Indian Penny Stocks & Small-Caps (< ₹100 / High Beta)
PENNY_WATCHLIST = [
    "SUZLON.NS",       # Suzlon Energy (~₹55-70)
    "YESBANK.NS",      # Yes Bank (~₹18-25)
    "IDEA.NS",         # Vodafone Idea (~₹8-12)
    "RPOWER.NS",       # Reliance Power (~₹30-45)
    "JPPOWER.NS",      # Jaiprakash Power (~₹15-22)
    "GTLINFRA.NS",     # GTL Infra (~₹2-4)
    "NHPC.NS",         # NHPC Ltd (~₹80-95)
    "IRFC.NS",         # Indian Railway Finance Corp (~₹140)
    "SOUTHBANK.NS",    # South Indian Bank (~₹25-35)
    "UCOBANK.NS",      # UCO Bank (~₹40-55)
    "IOB.NS",          # Indian Overseas Bank (~₹50-65)
    "CENTRALBK.NS",    # Central Bank of India (~₹50-65)
    "INFIBEAM.NS",     # Infibeam Avenues (~₹25-35)
    "MOREPENLAB.NS",   # Morepen Laboratories (~₹45-60)
]

# Backward compatibility alias
WATCHLIST = LARGECAP_WATCHLIST

def get_watchlist(universe: str = "largecap"):
    """Return watchlist by universe type ('largecap', 'penny', 'all')."""
    u = universe.lower()
    if u == "penny":
        return PENNY_WATCHLIST
    elif u == "all":
        # Deduplicated combination
        return list(dict.fromkeys(LARGECAP_WATCHLIST + PENNY_WATCHLIST))
    return LARGECAP_WATCHLIST

# Mapping ticker symbols to clean company search keywords for news matching
TICKER_KEYWORD_MAP = {
    "RELIANCE.NS": ["Reliance", "RIL", "Mukesh Ambani", "Jio"],
    "TCS.NS": ["TCS", "Tata Consultancy"],
    "HDFCBANK.NS": ["HDFC Bank", "HDFC"],
    "INFY.NS": ["Infosys"],
    "ICICIBANK.NS": ["ICICI Bank", "ICICI"],
    "BHARTIARTL.NS": ["Bharti Airtel", "Airtel"],
    "SBIN.NS": ["State Bank of India", "SBI"],
    "M&M.NS": ["Mahindra", "M&M", "Mahindra & Mahindra"],
    "LT.NS": ["Larsen & Toubro", "L&T"],
    "ITC.NS": ["ITC"],
    "SUNPHARMA.NS": ["Sun Pharma"],
    "BAJFINANCE.NS": ["Bajaj Finance", "Bajaj Finserv"],
    "MARUTI.NS": ["Maruti Suzuki", "Maruti"],
    "TITAN.NS": ["Titan"],
    "NTPC.NS": ["NTPC"],
    "ONGC.NS": ["ONGC"],
    "POWERGRID.NS": ["Power Grid", "PowerGrid"],
    "ADANIENT.NS": ["Adani Enterprises", "Adani"],
    "TATASTEEL.NS": ["Tata Steel"],
    "HAL.NS": ["Hindustan Aeronautics", "HAL"],
    "BEL.NS": ["Bharat Electronics", "BEL"],
    "TRENT.NS": ["Trent", "Zudio", "Westside"],
    # Penny stocks keywords
    "SUZLON.NS": ["Suzlon", "Suzlon Energy"],
    "YESBANK.NS": ["Yes Bank"],
    "IDEA.NS": ["Vodafone Idea", "VI", "Idea"],
    "RPOWER.NS": ["Reliance Power", "R-Power", "Anil Ambani"],
    "JPPOWER.NS": ["Jaiprakash Power", "JP Power"],
    "GTLINFRA.NS": ["GTL Infra"],
    "NHPC.NS": ["NHPC"],
    "IRFC.NS": ["IRFC", "Indian Railway Finance"],
    "SOUTHBANK.NS": ["South Indian Bank"],
    "UCOBANK.NS": ["UCO Bank"],
    "IOB.NS": ["Indian Overseas Bank", "IOB"],
    "CENTRALBK.NS": ["Central Bank of India"],
    "INFIBEAM.NS": ["Infibeam"],
    "MOREPENLAB.NS": ["Morepen", "Morepen Labs"],
}

# Indian Financial News RSS Feeds
RSS_FEEDS = {
    "Moneycontrol Latest": "https://www.moneycontrol.com/rss/latestnews.xml",
    "Moneycontrol Market Reports": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Economic Times Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "LiveMint Markets": "https://www.livemint.com/rss/markets"
}
