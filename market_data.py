
from __future__ import annotations
import pandas as pd
import requests
from io import StringIO

try:
    import yfinance as yf
except Exception:
    yf = None

DEFAULT_FX = {"USDINR": 94.44, "EURINR": 111.28, "AEDINR": 25.71}

INDEX_TICKERS = {
    "Nifty 50": "^NSEI", "Nifty Bank": "^NSEBANK", "Sensex": "^BSESN", "India VIX": "^INDIAVIX",
    "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT",
    "FTSE 100": "^FTSE", "DAX": "^GDAXI", "Nikkei 225": "^N225", "Hang Seng": "^HSI",
    "Gold USD/oz": "GC=F", "Silver USD/oz": "SI=F", "Brent Crude": "BZ=F", "WTI Crude": "CL=F",
    "USD/INR": "INR=X", "EUR/INR": "EURINR=X"
}

# Manual/live broker marks supplied by user. Clean price per 100 face.
BOND_MARKS = {
    "US04686E4K56": 0.988070,   # ATH 4.721 2029
    "US912810FT08": 1.017660,  # US T 4.5 2036
    "US91282CPE56": 0.9946995,  # US T 3.5 2027
    "US30231GBF81": 0.907560,   # XOM 4.227 2040
}


_AMFI_CACHE = None

def _norm_text(s: str) -> str:
    import re
    s = str(s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _amfi_table() -> pd.DataFrame:
    global _AMFI_CACHE
    if _AMFI_CACHE is not None:
        return _AMFI_CACHE
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        txt = requests.get(url, timeout=12, headers={"User-Agent":"Mozilla/5.0"}).text
        rows = []
        for line in txt.splitlines():
            parts = line.split(";")
            if len(parts) >= 6 and parts[0].strip().isdigit():
                try:
                    nav = float(parts[4])
                except Exception:
                    nav = None
                rows.append({
                    "scheme_code": parts[0].strip(),
                    "scheme_name": parts[3].strip(),
                    "nav": nav,
                    "date": parts[5].strip(),
                })
        _AMFI_CACHE = pd.DataFrame(rows)
        if not _AMFI_CACHE.empty:
            _AMFI_CACHE["norm"] = _AMFI_CACHE["scheme_name"].map(_norm_text)
        return _AMFI_CACHE
    except Exception:
        _AMFI_CACHE = pd.DataFrame()
        return _AMFI_CACHE

def _amfi_nav(query: str):
    q = _norm_text(query)
    table = _amfi_table()
    if table.empty or not q:
        return None, _empty_meta("AMFI unavailable")
    hits = table[table["norm"].str.contains(q, regex=False, na=False)].copy()
    if hits.empty:
        tokens = [t for t in q.split() if len(t) > 2 and t not in {"fund","direct","plan","growth","option"}]
        if tokens:
            hits = table[table["norm"].apply(lambda x: all(t in x for t in tokens[:8]))].copy()
    if hits.empty:
        return None, _empty_meta("AMFI no match")
    hits["score"] = hits["norm"].apply(lambda x: (5 if " direct " in f" {x} " else 0) + (5 if " growth " in f" {x} " else 0) + (2 if "regular" not in x else 0))
    row = hits.sort_values("score", ascending=False).iloc[0]
    if pd.isna(row["nav"]):
        return None, _empty_meta("AMFI NAV blank")
    return float(row["nav"]), {
        "source_status": f"AMFI NAV {row['date']}",
        "52w_high": None, "52w_low": None, "volume": None,
        "day_change": None, "day_change_pct": None,
    }


def _empty_meta(error: str = ""):
    return {"52w_high": None, "52w_low": None, "volume": None, "day_change": None, "day_change_pct": None, "source_status": error or "fallback"}

def _history(ticker: str, period: str = "1y") -> pd.DataFrame:
    if yf is None or not ticker:
        return pd.DataFrame()
    try:
        df = yf.download(str(ticker).strip(), period=period, interval="1d", progress=False, auto_adjust=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna(how="all").reset_index()
    except Exception:
        return pd.DataFrame()

def safe_price(ticker: str):
    t = str(ticker or "").strip()
    if not t:
        return None, _empty_meta("no ticker")
    if t.upper().startswith("MF:"):
        return _amfi_nav(t[3:])
    if t in BOND_MARKS:
        return BOND_MARKS[t], {"source_status":"broker bond mark /100", "day_change":None, "day_change_pct":None, "52w_high":None, "52w_low":None, "volume":None}
    if t.upper() == "SGB_PROXY":
        # SGB redemption is linked to grams of gold. Fallback proxy: India gold price per gram.
        # Try Yahoo gold futures USD/oz converted to INR/g; fallback keeps base value.
        gold, _ = safe_price("GC=F")
        if gold:
            inr_per_gram = gold * DEFAULT_FX["USDINR"] / 31.1035
            return inr_per_gram, {"source_status":"gold proxy USD/oz -> INR/g", "day_change":None, "day_change_pct":None}
        return None, _empty_meta("gold proxy fallback")
    if yf is None:
        return None, _empty_meta("yfinance missing")
    hist = _history(t, "1y")
    try:
        if hist.empty or "Close" not in hist:
            return None, _empty_meta("no data")
        close = pd.to_numeric(hist["Close"], errors="coerce").dropna()
        if close.empty:
            return None, _empty_meta("no close")
        last = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else last
        high = pd.to_numeric(hist.get("High"), errors="coerce").dropna() if "High" in hist else pd.Series(dtype=float)
        low = pd.to_numeric(hist.get("Low"), errors="coerce").dropna() if "Low" in hist else pd.Series(dtype=float)
        vol = pd.to_numeric(hist.get("Volume"), errors="coerce").dropna() if "Volume" in hist else pd.Series(dtype=float)
        return last, {
            "52w_high": float(high.max()) if not high.empty else None,
            "52w_low": float(low.min()) if not low.empty else None,
            "volume": float(vol.iloc[-1]) if not vol.empty else None,
            "day_change": last - prev,
            "day_change_pct": (last - prev)/prev if prev else None,
            "source_status":"live fetched"
        }
    except Exception as e:
        return None, _empty_meta(str(e)[:80])

def get_fx_rates(defaults: dict | None = None) -> dict:
    # User approved USDINR = 94.44 as base. Keep stable to match structure.
    rates = dict(defaults or DEFAULT_FX)
    rates["USDINR"] = 94.44
    rates["USD_SOURCE"] = "approved base rate"
    # EUR can be live/fallback; not used materially unless EUR assets added.
    eur, _ = safe_price("EURINR=X")
    rates["EURINR"] = eur if eur else rates.get("EURINR", DEFAULT_FX["EURINR"])
    rates["EUR_SOURCE"] = "live Yahoo" if eur else "fallback"
    return rates

def get_market_dashboard(default_fx: dict | None = None) -> pd.DataFrame:
    rows = []
    default_fx = default_fx or DEFAULT_FX
    for name, ticker in INDEX_TICKERS.items():
        price, meta = safe_price(ticker)
        fallback = default_fx.get("USDINR") if name == "USD/INR" else default_fx.get("EURINR") if name == "EUR/INR" else None
        chg = meta.get("day_change")
        rows.append({
            "Instrument": name, "Ticker": ticker, "Last": price if price is not None else fallback,
            "Move": "🟢 ▲" if chg and chg > 0 else ("🔴 ▼" if chg and chg < 0 else "—"),
            "Day %": meta.get("day_change_pct"), "52W High": meta.get("52w_high"),
            "52W Low": meta.get("52w_low"), "Volume": meta.get("volume"),
            "Status": meta.get("source_status", "")
        })
    return pd.DataFrame(rows)

def get_history(ticker: str, period="1y") -> pd.DataFrame:
    return _history(ticker, period)

def get_news(ticker: str, name: str = ""):
    if not ticker or yf is None:
        return []
    try:
        raw = yf.Ticker(ticker).news or []
        out = []
        for n in raw[:8]:
            content = n.get("content", n) if isinstance(n, dict) else {}
            provider = content.get("provider") or {}
            canon = content.get("canonicalUrl") or {}
            out.append({
                "title": content.get("title") or n.get("title"),
                "publisher": provider.get("displayName") if isinstance(provider, dict) else n.get("publisher", "Yahoo Finance"),
                "link": canon.get("url") if isinstance(canon, dict) else n.get("link", "#"),
            })
        return [x for x in out if x.get("title")]
    except Exception:
        return []
