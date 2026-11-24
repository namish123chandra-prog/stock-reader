# ============================================================
#  MARKET DATA HELPER
#  Gets Indian stock prices (NSE - the National Stock Exchange,
#  where you buy in rupees). Uses the free "yfinance" library.
#  Every NSE symbol gets ".NS" added, e.g. RELIANCE -> RELIANCE.NS
# ============================================================

import time
import yfinance as yf

import config
from core.persistence import read_json

# Friendly names -> official NSE symbols, so you can type
# "tata motors" instead of remembering "TATAMOTORS".
ALIASES = {
    "reliance": "RELIANCE", "jio": "RELIANCE",
    "tcs": "TCS", "tata consultancy": "TCS",
    "hdfc bank": "HDFCBANK", "hdfc": "HDFCBANK",
    "icici bank": "ICICIBANK", "icici": "ICICIBANK",
    "infosys": "INFY", "infy": "INFY",
    "airtel": "BHARTIARTL", "bharti airtel": "BHARTIARTL",
    "sbi": "SBIN", "state bank": "SBIN",
    "larsen": "LT", "l&t": "LT", "lt": "LT",
    "itc": "ITC",
    "hul": "HINDUNILVR", "hindustan unilever": "HINDUNILVR",
    "kotak": "KOTAKBANK", "kotak bank": "KOTAKBANK",
    "axis bank": "AXISBANK", "axis": "AXISBANK",
    "bajaj finance": "BAJFINANCE",
    "asian paints": "ASIANPAINT", "asian paint": "ASIANPAINT",
    "maruti": "MARUTI", "maruti suzuki": "MARUTI",
    "hcl tech": "HCLTECH", "hcltech": "HCLTECH",
    "sun pharma": "SUNPHARMA",
    "titan": "TITAN",
    "ultratech": "ULTRACEMCO", "ultratech cement": "ULTRACEMCO",
    "wipro": "WIPRO",
    "ntpc": "NTPC",
    "power grid": "POWERGRID", "powergrid": "POWERGRID",
    "ongc": "ONGC",
    "tata motors": "TMPV", "tatamotors": "TMPV",
    "tata motors passenger": "TMPV", "tmpv": "TMPV",
    "tata motors commercial": "TMCV", "tmcv": "TMCV",
    "tata steel": "TATASTEEL", "tatasteel": "TATASTEEL",
    "jsw steel": "JSWSTEEL",
    "adani enterprises": "ADANIENT", "adani": "ADANIENT",
    "adani ports": "ADANIPORTS",
    "coal india": "COALINDIA",
    "bajaj finserv": "BAJAJFINSV",
    "bajaj auto": "BAJAJ-AUTO",
    "hero motocorp": "HEROMOTOCO", "hero": "HEROMOTOCO",
    "dr reddy": "DRREDDY", "dr reddys": "DRREDDY",
    "cipla": "CIPLA",
    "divis": "DIVISLAB", "divis lab": "DIVISLAB",
    "apollo hospital": "APOLLOHOSP", "apollo": "APOLLOHOSP",
    "eicher": "EICHERMOT", "royal enfield": "EICHERMOT",
    "grasim": "GRASIM",
    "hindalco": "HINDALCO",
    "indusind": "INDUSINDBK", "indusind bank": "INDUSINDBK",
    "tech mahindra": "TECHM", "techm": "TECHM",
    "nestle": "NESTLEIND",
    "britannia": "BRITANNIA",
    "tata consumer": "TATACONSUM",
    "sbi life": "SBILIFE",
    "hdfc life": "HDFCLIFE",
    "bpcl": "BPCL",
    "ltim": "LT", "ltimindtree": "LT",  # LTIMindtree merged into L&T
    "trent": "TRENT", "zudio": "TRENT",
    "bel": "BEL", "bharat electronics": "BEL",
    "zomato": "ETERNAL", "eternal": "ETERNAL",
    "paytm": "PAYTM", "one97": "PAYTM",
    "irctc": "IRCTC",
    "hal": "HAL", "hindustan aeronautics": "HAL",
    "dmart": "DMART", "avenue supermarts": "DMART",
    "jio finance": "JIOFIN", "jiofin": "JIOFIN",
    "irfc": "IRFC",
    "vedanta": "VEDL",
    "yes bank": "YESBANK", "yesbank": "YESBANK",
    "vodafone": "IDEA", "vi": "IDEA", "idea": "IDEA",
    "lic": "LICI",
    "suzlon": "SUZLON",
    "bhel": "BHEL",
    "gail": "GAIL",
    "ioc": "IOC", "indian oil": "IOC",
    "pidilite": "PIDILITIND", "fevicol": "PIDILITIND",
    "havells": "HAVELLS",
    "dabur": "DABUR",
    "godrej": "GODREJCP", "godrej consumer": "GODREJCP",
    "berger paints": "BERGEPAINT", "berger": "BERGEPAINT",
    "mrf": "MRF",
    "bosch": "BOSCHLTD",
    "siemens": "SIEMENS",
    "abb": "ABB",
    "tata power": "TATAPOWER", "tatapower": "TATAPOWER",
    "adani power": "ADANIPOWER",
    "adani green": "ADANIGREEN",
    "pnb": "PNB", "punjab national bank": "PNB",
    "bank of baroda": "BANKBARODA", "bob": "BANKBARODA",
    "canara bank": "CANBK",
    "idfc first": "IDFCFIRSTB", "idfc": "IDFCFIRSTB",
    "federal bank": "FEDERALBNK",
    "ola electric": "OLAELEC",
    "nykaa": "NYKAA", "f sn": "NYKAA",
    "policybazaar": "POLICYBZR", "pb fintech": "POLICYBZR",
    "delhivery": "DELHIVERY",
    "indigo": "INDIGO", "interglobe": "INDIGO",
    "dixon": "DIXON",
    "polycab": "POLYCAB",
    "mazagon": "MAZDOCK", "mazagon dock": "MAZDOCK",
    "cochin shipyard": "COCHINSHIP",
    "rvnl": "RVNL",
    "hudco": "HUDCO",
    "ncc": "NCC",
    "nifty": "^NSEI", "nifty 50": "^NSEI", "nifty50": "^NSEI",
}

# Simple word cache so we don't re-download prices every message.
_cache = {}


def _cached(key, minutes, fetch_function):
    now = time.time()
    if key in _cache and now - _cache[key][0] < minutes * 60:
        return _cache[key][1]
    value = fetch_function()
    # (careful: pandas Series can't be used in a plain "if value" check)
    if value is not None and len(value) > 0:
        _cache[key] = (now, value)
    return value


def user_watchlist():
    """Stocks added from the app's Watchlist button/commands."""
    return read_json("watchlist.json", [])


def all_watch_symbols():
    """Watchlist + your extra stocks + stocks you added in chat."""
    names = list(dict.fromkeys(
        config.WATCHLIST + config.EXTRA_STOCKS + user_watchlist()))
    return [n if n.endswith(".NS") else n + ".NS" for n in names if n]


def resolve_symbol(text):
    """Turn whatever the user typed into a symbol like 'TCS.NS'.
    Returns None if we truly can't guess."""
    t = text.strip().lower()
    if not t:
        return None
    if t in ALIASES:
        sym = ALIASES[t]
        return sym if sym.startswith("^") else sym + ".NS"
    # Maybe they typed the raw symbol, like "TCS" or "tcs.ns"
    word = t.upper().replace(".NS", "").replace(" ", "")
    if word.replace("-", "").replace("&", "").isalnum() and 1 < len(word) <= 20:
        return word + ".NS"
    return None


def find_symbol_in(text):
    """Look inside a sentence like 'should i buy tata motors?'
    and find the stock. Returns (symbol, matched_name) or (None, None)."""
    t = " " + text.lower().strip(" ?.!") + " "
    # Longest friendly names first so "tata motors" beats "tata"
    for name in sorted(ALIASES, key=len, reverse=True):
        if " " + name + " " in t or t.strip() == name:
            sym = ALIASES[name]
            return (sym if sym.startswith("^") else sym + ".NS"), name
    # If the whole message is just one word, treat it as a symbol
    stripped = text.strip().strip("?!.")
    if len(stripped.split()) == 1:
        sym = resolve_symbol(stripped)
        if sym:
            return sym, stripped.lower()
    return None, None


def get_daily_moves(symbols=None):
    """Today's price + % change for many stocks at once.
    Returns {symbol: {"price": float, "change_pct": float}}"""
    symbols = symbols or all_watch_symbols()

    def fetch():
        data = yf.download(symbols, period="5d", interval="1d",
                           group_by="ticker", progress=False, threads=True)
        out = {}
        for s in symbols:
            try:
                df = data[s] if len(symbols) > 1 else data
                closes = df["Close"].dropna()
                if len(closes) < 2:
                    continue
                last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
                if prev <= 0:
                    continue
                out[s] = {"price": last,
                          "change_pct": (last - prev) / prev * 100.0}
            except Exception:
                continue  # one bad stock shouldn't break the rest
        return out

    return _cached("moves:" + ",".join(symbols), config.CACHE_MINUTES, fetch)


def get_closes(symbol, period="1y"):
    """Daily closing prices for one stock (a pandas Series)."""
    def fetch():
        try:
            hist = yf.Ticker(symbol).history(period=period)
            closes = hist["Close"].dropna()
            return closes if len(closes) >= 2 else None
        except Exception:
            return None
    return _cached("closes:" + symbol + ":" + period, config.CACHE_MINUTES, fetch)


def get_bulk_closes(symbols, period="1y"):
    """Daily closing prices for many stocks in one go.
    Returns {symbol: closes Series}. Used for ranking the watchlist."""
    def fetch():
        data = yf.download(symbols, period=period, interval="1d",
                           group_by="ticker", progress=False, threads=True)
        out = {}
        for s in symbols:
            try:
                df = data[s] if len(symbols) > 1 else data
                closes = df["Close"].dropna()
                if len(closes) > 30:
                    out[s] = closes
            except Exception:
                continue
        return out
    return _cached("bulk:" + period + ":" + ",".join(symbols), 30, fetch)


def get_company_name(symbol):
    """Best-effort full company name, falls back to the symbol."""
    def fetch():
        try:
            info = yf.Ticker(symbol).info or {}
            return info.get("longName") or info.get("shortName") or symbol
        except Exception:
            return symbol
    return _cached("name:" + symbol, 24 * 60, fetch)
