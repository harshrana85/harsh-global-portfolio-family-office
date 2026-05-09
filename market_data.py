
from __future__ import annotations
import pandas as pd
import requests
from functools import lru_cache
from io import StringIO

try:
    import yfinance as yf
except Exception:
    yf = None

DEFAULT_FX = {"USDINR": 94.44, "EURINR": 111.28, "AEDINR": 25.71, "GBPINR": 126.30}

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

MF_SEARCH_ALIASES = {
    # canonical keys from portfolio_seed.py -> official AMFI scheme names/search text
    # These exact names are used before fuzzy search so HDFC/Kotak/Parag do not miss live NAV mapping.
    "HDFC Hybrid Equity Fund": "HDFC Hybrid Equity Fund - Regular Plan - Growth",
    "HDFC Large Cap Fund": "HDFC Top 100 Fund - Regular Plan - Growth",
    "HDFC Mid Cap Opportunities Fund": "HDFC Mid-Cap Opportunities Fund - Regular Plan - Growth",
    "HDFC Small Cap Fund": "HDFC Small Cap Fund - Regular Plan - Growth Option",
    "HDFC Corporate Bond Fund": "HDFC Corporate Bond Fund - Regular Plan - Growth Option",
    "HDFC Short Term Debt Fund": "HDFC Short Term Debt Fund - Growth Option",
    "HDFC Dynamic Bond Fund": "HDFC Dynamic Debt Fund - Regular Plan - Growth Option",
    "HDFC PSU Banking Debt Fund": "HDFC Banking and PSU Debt Fund - Regular Plan - Growth Option",
    "Parag Parikh Flexi Cap Fund": "Parag Parikh Flexi Cap Fund - Regular Plan - Growth",
    "Kotak Banking & PSU Fund": "Kotak Banking and PSU Debt Fund - Regular Plan - Growth",
    "Kotak Corporate Bond Fund": "Kotak Corporate Bond Fund - Regular Plan - Growth",
    "Kotak Short Term Debt Fund": "Kotak Bond Short Term Fund - Regular Plan - Growth",
}

MF_NAME_SYNONYMS = {
    "HDFC PSU Banking Debt Fund": [
        "HDFC Banking and PSU Debt Fund - Regular Plan - Growth Option",
        "HDFC Banking & PSU Debt Fund - Regular Plan - Growth Option",
    ],
    "HDFC Short Term Debt Fund": [
        "HDFC Short Term Debt Fund - Growth Option",
        "HDFC Short Term Debt Fund - Regular Plan - Growth Option",
    ],
    "HDFC Dynamic Bond Fund": [
        "HDFC Dynamic Debt Fund - Regular Plan - Growth Option",
        "HDFC Dynamic Bond Fund - Regular Plan - Growth Option",
    ],
    "Kotak Banking & PSU Fund": [
        "Kotak Banking and PSU Debt Fund - Regular Plan - Growth",
        "Kotak Banking & PSU Debt Fund - Regular Plan - Growth",
        "Kotak Banking and PSU Fund - Regular Plan - Growth",
    ],
    "Kotak Corporate Bond Fund": [
        "Kotak Corporate Bond Fund - Regular Plan - Growth",
        "Kotak Corporate Bond Fund - Standard Plan - Growth",
    ],
    "Kotak Short Term Debt Fund": [
        "Kotak Bond Short Term Fund - Regular Plan - Growth",
        "Kotak Bond Short Term Plan - Regular Plan - Growth",
        "Kotak Short Term Debt Fund - Regular Plan - Growth",
    ],
}

_AMFI_NAV_URLS = [
    "https://www.amfiindia.com/spages/NAVAll.txt",
    "https://www.amfiindia.com/spages/NAVOpen.txt",
]

def _mf_clean_name(x: str) -> str:
    import re
    x = str(x or "").lower()
    x = x.replace("&", " and ")
    x = x.replace("regular-growth", "regular plan growth")
    x = x.replace("reg gr", "regular growth")
    x = re.sub(r"[^a-z0-9]+", " ", x)
    x = x.replace("growth option", "growth")
    x = x.replace("regular plan", "regular")
    x = re.sub(r"\b(fund|plan|option|scheme)\b", " ", x)
    return re.sub(r"\s+", " ", x).strip()

def _normalise_mf_query(query: str) -> str:
    q = str(query or "").strip()
    q = q.replace("MF:", "")
    q = q.replace("HDFC Mutual Fund ", "HDFC ").replace("Kotak Mutual Fund ", "Kotak ")
    q = q.replace("Parag Parikh Flexi Cap Fund Parikh Flexi Cap Fund", "Parag Parikh Flexi Cap Fund")
    q = q.split(" - ")[0].strip()
    return MF_SEARCH_ALIASES.get(q, q)

def _mf_query_candidates(query: str) -> list[str]:
    q0 = str(query or "").replace("MF:", "").split(" - ")[0].strip()
    primary = _normalise_mf_query(query)
    candidates = [primary]
    candidates.extend(MF_NAME_SYNONYMS.get(q0, []))
    candidates.extend(MF_NAME_SYNONYMS.get(primary, []))
    if q0 and q0 not in candidates:
        candidates.append(q0)
    out = []
    for c in candidates:
        if c and c not in out:
            out.append(c)
    return out

@lru_cache(maxsize=4)
def _amfi_nav_rows() -> list[dict]:
    for url in _AMFI_NAV_URLS:
        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            rows = []
            for line in r.text.splitlines():
                parts = line.split(";")
                if len(parts) >= 6 and parts[0].strip().isdigit():
                    try:
                        rows.append({"code": parts[0].strip(), "name": parts[3].strip(), "nav": float(parts[4]), "date": parts[5].strip()})
                    except Exception:
                        pass
            if rows:
                return rows
        except Exception:
            continue
    return []

def _amfi_latest_nav_by_name(query: str):
    rows = _amfi_nav_rows()
    if not rows:
        return None, _empty_meta("AMFI NAVAll unavailable")
    candidates = _mf_query_candidates(query)
    wanted = [_mf_clean_name(c) for c in candidates]
    # exact clean match first
    for w, raw in zip(wanted, candidates):
        for row in rows:
            if _mf_clean_name(row["name"]) == w:
                return row["nav"], {"source_status": f"live AMFI NAVAll ({row['code']}) {row['date']}", "day_change": None, "day_change_pct": None, "52w_high": None, "52w_low": None, "volume": None}
    # token scored fallback, explicitly prefer regular + growth and avoid direct/idcw/dividend.
    best, best_score = None, -999
    for raw, w in zip(candidates, wanted):
        words = [x for x in w.split() if len(x) > 2 and x not in {"regular", "growth"}]
        for row in rows:
            nm = _mf_clean_name(row["name"])
            score = sum(5 for token in words if token in nm)
            low = row["name"].lower()
            if "regular" in low: score += 5
            if "growth" in low: score += 5
            if "direct" in low: score -= 20
            if any(x in low for x in ["idcw", "dividend", "payout", "reinvestment"]): score -= 10
            if score > best_score:
                best, best_score = row, score
    if best and best_score > 0:
        return best["nav"], {"source_status": f"live AMFI NAVAll ({best['code']}) {best['date']}", "day_change": None, "day_change_pct": None, "52w_high": None, "52w_low": None, "volume": None}
    return None, _empty_meta("AMFI scheme not found")

@lru_cache(maxsize=128)
def _mf_search_code(query: str) -> str | None:
    for q in _mf_query_candidates(query):
        try:
            r = requests.get("https://api.mfapi.in/mf/search", params={"q": q}, timeout=8)
            r.raise_for_status()
            matches = r.json() or []
            q_words = [w.lower() for w in q.replace("&", "and").replace("-", " ").split() if len(w) > 2 and w.lower() not in {"fund", "growth", "direct", "plan", "regular", "option"}]
            best = None
            best_score = -1
            for m in matches:
                name = str(m.get("schemeName", ""))
                lname = name.lower().replace("&", "and")
                score = sum(2 for w in q_words if w in lname)
                if "growth" in lname:
                    score += 3
                if "regular" in lname:
                    score += 3
                if "direct" in lname:
                    score -= 10
                if any(x in lname for x in ["idcw", "dividend", "payout", "reinvestment"]):
                    score -= 5
                if score > best_score:
                    best, best_score = m, score
            if best and best_score > 0:
                return str(best.get("schemeCode"))
        except Exception:
            continue
    return None

def _mf_latest_nav(query_or_code: str):
    code_or_query = str(query_or_code).strip()
    if not code_or_query:
        return None, _empty_meta("missing MF query")
    if not code_or_query.isdigit():
        # Use official AMFI NAVAll exact/name match first. mfapi search is kept as backup.
        nav, meta = _amfi_latest_nav_by_name(code_or_query)
        if nav is not None:
            return nav, meta
        code = _mf_search_code(code_or_query) or ""
    else:
        code = code_or_query
    if not code:
        return None, _empty_meta("MF scheme not found")
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{code}/latest", timeout=8)
        r.raise_for_status()
        payload = r.json() or {}
        data = payload.get("data") or []
        if not data:
            return None, _empty_meta("MF latest NAV missing")
        nav = float(data[0].get("nav"))
        return nav, {
            "source_status": f"live AMFI NAV via mfapi.in ({code})",
            "day_change": None, "day_change_pct": None,
            "52w_high": None, "52w_low": None, "volume": None
        }
    except Exception as e:
        return None, _empty_meta(f"MF NAV fallback: {str(e)[:60]}")

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
    if t in BOND_MARKS:
        return BOND_MARKS[t], {"source_status":"broker bond mark /100", "day_change":None, "day_change_pct":None, "52w_high":None, "52w_low":None, "volume":None}
    if t.upper().startswith("MF:"):
        return _mf_latest_nav(t.split(":", 1)[1])
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
    # EUR/GBP can be live/fallback; GBP is required for DFND.L.
    eur, _ = safe_price("EURINR=X")
    gbp, _ = safe_price("GBPINR=X")
    rates["EURINR"] = eur if eur else rates.get("EURINR", DEFAULT_FX["EURINR"])
    rates["GBPINR"] = gbp if gbp else rates.get("GBPINR", DEFAULT_FX["GBPINR"])
    rates["EUR_SOURCE"] = "live Yahoo" if eur else "fallback"
    rates["GBP_SOURCE"] = "live Yahoo" if gbp else "fallback"
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
