# -*- coding: utf-8 -*-
"""Configuration settings for Indian Stock AI Agent (NSE / BSE)."""

# Default Capital & Risk Settings (in INR ₹)
DEFAULT_CAPITAL_INR = 500000.0   # ₹5,00,000 initial portfolio
DEFAULT_RISK_PER_TRADE_PCT = 1.0 # 1.0% max loss of portfolio per trade (₹5,000)
MAX_ALLOCATION_PER_STOCK_PCT = 15.0 # Max 15% of portfolio in any single stock (₹75,000)
DEFAULT_STOP_LOSS_ATR_MULT = 2.0  # Stop loss placed at 2x ATR(14) below entry

# 1. Liquid Large-Cap Watchlist: Core Nifty 50 & Institutional Bellwethers
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

# 2. High-Growth Mid-Cap Watchlist: Nifty Midcap 100/150 Leaders
MIDCAP_WATCHLIST = [
    "DIXON.NS",       # Dixon Technologies
    "POLYCAB.NS",     # Polycab India
    "PERSISTENT.NS",  # Persistent Systems
    "COFORGE.NS",     # Coforge Ltd
    "KPITTECH.NS",    # KPIT Technologies
    "FEDERALBNK.NS",  # Federal Bank
    "ASHOKLEY.NS",    # Ashok Leyland
    "VOLTAS.NS",      # Voltas
    "MAXHEALTH.NS",   # Max Healthcare
    "ASTRAL.NS",      # Astral Ltd
    "CUMMINSIND.NS",  # Cummins India
    "IDFCFIRSTB.NS",  # IDFC First Bank
    "APOLLOTYRE.NS",  # Apollo Tyres
    "AUROPHARMA.NS",  # Aurobindo Pharma
]

# 3. High-Momentum Small-Cap Watchlist: Nifty Smallcap 100/250 Leaders
SMALLCAP_WATCHLIST = [
    "KAYNES.NS",      # Kaynes Technology
    "CDSL.NS",        # Central Depository Services
    "BSE.NS",         # BSE Ltd
    "ANGELONE.NS",    # Angel One
    "RVNL.NS",        # Rail Vikas Nigam Ltd
    "MAZDOCK.NS",     # Mazagon Dock Shipbuilders
    "COCHINSHIP.NS",  # Cochin Shipyard
    "HUDCO.NS",       # Housing & Urban Development Corp
    "OLECTRA.NS",     # Olectra Greentech
    "POONAWALLA.NS",  # Poonawalla Fincorp
    "NBCC.NS",        # NBCC India
    "TEJASNET.NS",    # Tejas Networks
    "CYIENT.NS",      # Cyient Ltd
    "MANAPPURAM.NS",  # Manappuram Finance
]

# 4. Active High-Volume Indian Penny Stocks (< ₹100 / High Beta)
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
    "PNB.NS",          # Punjab National Bank (~₹95-105)
    "MOREPENLAB.NS",   # Morepen Laboratories (~₹45-60)
]

# Backward compatibility alias
WATCHLIST = LARGECAP_WATCHLIST

def get_watchlist(universe: str = "largecap"):
    """Return watchlist by universe type ('largecap', 'midcap', 'smallcap', 'penny', 'all')."""
    u = universe.lower()
    if u == "midcap":
        return MIDCAP_WATCHLIST
    elif u == "smallcap":
        return SMALLCAP_WATCHLIST
    elif u == "penny":
        return PENNY_WATCHLIST
    elif u == "all":
        return list(dict.fromkeys(LARGECAP_WATCHLIST + MIDCAP_WATCHLIST + SMALLCAP_WATCHLIST + PENNY_WATCHLIST))
    return LARGECAP_WATCHLIST

# Mapping ticker symbols to clean company search keywords for news matching
TICKER_KEYWORD_MAP = {
    # Large Caps
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
    # Mid Caps
    "DIXON.NS": ["Dixon", "Dixon Tech"],
    "POLYCAB.NS": ["Polycab", "Polycab India"],
    "PERSISTENT.NS": ["Persistent", "Persistent Systems"],
    "COFORGE.NS": ["Coforge"],
    "KPITTECH.NS": ["KPIT", "KPIT Tech"],
    "FEDERALBNK.NS": ["Federal Bank"],
    "ASHOKLEY.NS": ["Ashok Leyland"],
    "VOLTAS.NS": ["Voltas"],
    "MAXHEALTH.NS": ["Max Healthcare", "Max Health"],
    "ASTRAL.NS": ["Astral", "Astral Poly"],
    "CUMMINSIND.NS": ["Cummins", "Cummins India"],
    "IDFCFIRSTB.NS": ["IDFC First", "IDFC First Bank"],
    "APOLLOTYRE.NS": ["Apollo Tyres", "Apollo Tyre"],
    "AUROPHARMA.NS": ["Aurobindo", "Aurobindo Pharma"],
    # Small Caps
    "KAYNES.NS": ["Kaynes", "Kaynes Tech"],
    "CDSL.NS": ["CDSL"],
    "BSE.NS": ["BSE", "Bombay Stock Exchange"],
    "ANGELONE.NS": ["Angel One", "Angel Broking"],
    "RVNL.NS": ["RVNL", "Rail Vikas"],
    "MAZDOCK.NS": ["Mazagon Dock", "Mazdock"],
    "COCHINSHIP.NS": ["Cochin Shipyard"],
    "HUDCO.NS": ["HUDCO"],
    "OLECTRA.NS": ["Olectra", "Olectra Greentech"],
    "POONAWALLA.NS": ["Poonawalla", "Poonawalla Fincorp"],
    "NBCC.NS": ["NBCC"],
    "TEJASNET.NS": ["Tejas Networks", "Tejas"],
    "CYIENT.NS": ["Cyient"],
    "MANAPPURAM.NS": ["Manappuram", "Manappuram Finance"],
    # Penny Stocks
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
    "PNB.NS": ["PNB", "Punjab National Bank"],
    "MOREPENLAB.NS": ["Morepen", "Morepen Labs"],
}

# Indian Financial News RSS Feeds
RSS_FEEDS = {
    "Moneycontrol Latest": "https://www.moneycontrol.com/rss/latestnews.xml",
    "Moneycontrol Market Reports": "https://www.moneycontrol.com/rss/marketreports.xml",
    "Economic Times Stocks": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "LiveMint Markets": "https://www.livemint.com/rss/markets"
}
