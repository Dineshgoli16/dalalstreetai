# -*- coding: utf-8 -*-
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import yfinance as yf

LARGECAP = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "SBIN.NS", "M&M.NS", "LT.NS", "ITC.NS",
    "SUNPHARMA.NS", "BAJFINANCE.NS", "MARUTI.NS", "TITAN.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "ADANIENT.NS", "TATASTEEL.NS", "HAL.NS",
    "BEL.NS", "TRENT.NS"
]

MIDCAP = [
    "DIXON.NS", "POLYCAB.NS", "PERSISTENT.NS", "COFORGE.NS", "KPITTECH.NS",
    "FEDERALBNK.NS", "ASHOKLEY.NS", "VOLTAS.NS", "MAXHEALTH.NS", "ASTRAL.NS",
    "CUMMINSIND.NS", "IDFCFIRSTB.NS", "APOLLOTYRE.NS", "AUROPHARMA.NS"
]

SMALLCAP = [
    "KAYNES.NS", "CDSL.NS", "BSE.NS", "ANGELONE.NS", "RVNL.NS",
    "MAZDOCK.NS", "COCHINSHIP.NS", "HUDCO.NS", "OLECTRA.NS", "POONAWALLA.NS",
    "NBCC.NS", "TEJASNET.NS", "CYIENT.NS", "MANAPPURAM.NS"
]

PENNY = [
    "SUZLON.NS", "YESBANK.NS", "IDEA.NS", "RPOWER.NS", "JPPOWER.NS",
    "GTLINFRA.NS", "NHPC.NS", "IRFC.NS", "SOUTHBANK.NS", "UCOBANK.NS",
    "IOB.NS", "CENTRALBK.NS", "PNB.NS", "MOREPENLAB.NS"
]

INDICES = ["^NSEI", "^NSEBANK", "^BSESN", "^INDIAVIX"]

all_stocks = LARGECAP + MIDCAP + SMALLCAP + PENNY
all_tickers = list(dict.fromkeys(all_stocks + INDICES))
print(f"Downloading historical data for {len(all_tickers)} tickers ({len(all_stocks)} stocks + {len(INDICES)} indices)...")

data = yf.download(all_tickers, period="6mo", interval="1d", group_by="ticker", progress=False)

snapshot = {
    "generated_at": datetime.now().isoformat(),
    "pulse": {},
    "stocks": {},
    "news": []
}

# 1. Market Pulse
for idx in INDICES:
    try:
        df = data[idx].dropna()
        if len(df) >= 2:
            close = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])
            pct = round(((close - prev) / prev) * 100, 2)
            snapshot["pulse"][idx] = {"close": round(close, 2), "pct": pct}
    except Exception as e:
        print(f"Error {idx}: {e}")

# 2. Stocks
for sym in all_stocks:
    try:
        if sym not in data:
            continue
        df = data[sym].dropna()
        if len(df) < 5:
            continue
        
        close = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        pct_change = round(((close - prev) / prev) * 100, 2)
        high52 = round(float(df["High"].max()), 2)
        low52 = round(float(df["Low"].min()), 2)

        candles = []
        for dt, row in df.iterrows():
            candles.append({
                "time": dt.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if "Volume" in row and not row.isna()["Volume"] else 0
            })

        cap_tag = "largecap" if sym in LARGECAP else ("midcap" if sym in MIDCAP else ("smallcap" if sym in SMALLCAP else "penny"))

        snapshot["stocks"][sym] = {
            "symbol": sym,
            "current_price": round(close, 2),
            "prev_close": round(prev, 2),
            "pct_change": pct_change,
            "high_52w": high52,
            "low_52w": low52,
            "cap": cap_tag,
            "candles": candles[-120:]
        }
    except Exception as e:
        print(f"Error {sym}: {e}")

# 3. News
try:
    url = "https://news.google.com/rss/search?q=NSE+stocks+India+when:2d&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        xml_data = r.read().decode("utf-8", errors="ignore")
    root = ET.fromstring(xml_data)
    for item in root.findall(".//item")[:30]:
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pubDate = item.find("pubDate").text if item.find("pubDate") is not None else ""
        desc = item.find("description").text if item.find("description") is not None else ""
        snapshot["news"].append({
            "title": title,
            "link": link,
            "pubDate": pubDate,
            "description": desc,
            "source": "Google News"
        })
except Exception as e:
    print(f"Error fetching news: {e}")

print(f"Generated snapshot for {len(snapshot['stocks'])} stocks, {len(snapshot['pulse'])} indices, and {len(snapshot['news'])} headlines.")

with open("market_snapshot.json", "w", encoding="utf-8") as f:
    json.dump(snapshot, f)

with open("docs/market_snapshot.json", "w", encoding="utf-8") as f:
    json.dump(snapshot, f)

print("Saved market_snapshot.json to root and docs/")
