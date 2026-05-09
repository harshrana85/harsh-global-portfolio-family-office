from __future__ import annotations
import pandas as pd
import math

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    import requests
except Exception:
    requests = None

INDEX_TICKERS = {
    "Nifty 50": "^NSEI", "Nifty Bank": "^NSEBANK", "Sensex": "^BSESN", "India VIX": "^INDIAVIX",
    "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT",
    "FTSE 100": "^FTSE", "DAX": "^GDAXI", "Nikkei 225": "^N225", "Hang Seng": "^HSI",
    "Gold USD/oz": "GC=F", "Silver USD/oz": "SI=F", "Brent Crude": "BZ=F", "WTI Crude": "CL=F",
    "USD/INR": "INR=X", "EUR/INR": "EURINR=X"
}
CURRENCY_SYMBOL = {"INR": "₹", "USD": "$", "EUR": "€", "AED": "د.إ"}

# Manual live marks from user screenshots / bond monitor. App applies as price per $1 face = clean price/100.
BOND_PRICE_BY_ID = {
    "US04686E4K56": 98.807/100.0,    # Athene 4.721 Oct 2029
    "US912810FT08": 101.766/100.0,   # US Treasury 4.5 Feb 2036
    "US91282CPE56": 99.470/100.0,    # US Treasury 3.5 Oct 2027
    "US30231GBF81": 90.756/100.0,    # Exxon 4.227 Mar 2040
}


def _empty_meta(error: str = ""):
    return {"52w_high": None, "52w_low": None, "volume": None, "day_high": None, "day_low": None, "market_cap": None, "source_status": error or "manual"}


def _history(ticker: str, period: str = "1y") -> pd.DataFrame:
    if yf is None or not ticker:
        return pd.DataFrame()
    try:
        df = yf.download(str(ticker).strip(), period=period, interval="1d", progress=False, auto_adjust=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna(how="all")
        return df.reset_index()
    except Exception:
        try:
            df = yf.Ticker(str(ticker).strip()).history(period=period, interval="1d", auto_adjust=False)
            return df.reset_index() if df is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()


def _last_yahoo_close(ticker: str):
    hist = _history(ticker, "1y")
    if hist.empty or "Close" not in hist:
        return None, _empty_meta("no live data returned")
    close = pd.to_numeric(hist["Close"], errors="coerce").dropna()
    if close.empty:
        return None, _empty_meta("no close price")
    last = float(close.iloc[-1])
    high = pd.to_numeric(hist.get("High"), errors="coerce").dropna() if "High" in hist else pd.Series(dtype=float)
    low = pd.to_numeric(hist.get("Low"), errors="coerce").dropna() if "Low" in hist else pd.Series(dtype=float)
    vol = pd.to_numeric(hist.get("Volume"), errors="coerce").dropna() if "Volume" in hist else pd.Series(dtype=float)
    prev = float(close.iloc[-2]) if len(close) > 1 else last
    day_change = last - prev
    meta = {
        "52w_high": float(high.max()) if not high.empty else None,
        "52w_low": float(low.min()) if not low.empty else None,
        "volume": float(vol.iloc[-1]) if not vol.empty else None,
        "day_change": day_change,
        "day_change_pct": (day_change / prev) if prev else None,
        "source_status": "live Yahoo fetched",
    }
    return last, meta


def _gold_inr_per_gram():
    # Best free proxy: COMEX gold futures USD/oz converted by USDINR. 1 troy oz = 31.1034768 grams.
    gold_usd_oz, gmeta = _last_yahoo_close("GC=F")
    usd_inr, _ = _last_yahoo_close("INR=X")
    if gold_usd_oz and usd_inr:
        return float(gold_usd_oz) * float(usd_inr) / 31.1034768, {"source_status": "live SGB proxy: GC=F × USDINR / 31.1035"}
    return None, _empty_meta("SGB proxy unavailable")


def get_sgb_rate():
    return _gold_inr_per_gram()


def _load_amfi_nav_table() -> pd.DataFrame:
    if requests is None:
        return pd.DataFrame()
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        r = requests.get(url, timeout=12, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        rows = []
        for line in r.text.splitlines():
            if ";" not in line or line.startswith("Scheme Code"):
                continue
            parts = line.split(";")
            if len(parts) >= 6:
                rows.append({
                    "scheme_code": parts[0].strip(),
                    "isin_payout": parts[1].strip(),
                    "isin_reinvest": parts[2].strip(),
                    "scheme_name": parts[3].strip(),
                    "nav": pd.to_numeric(parts[4].strip(), errors="coerce"),
                    "date": parts[5].strip(),
                })
        df = pd.DataFrame(rows).dropna(subset=["nav"])
        return df
    except Exception:
        return pd.DataFrame()


def _norm(s: str) -> str:
    return " ".join(str(s).lower().replace("&", "and").replace("-", " ").replace(".", " ").split())


def get_amfi_nav(identifier: str):
    """identifier format: MF:<query> or MF:<ISIN>. Returns NAV per unit in INR."""
    raw = str(identifier or "").strip()
    query = raw[3:] if raw.upper().startswith("MF:") else raw
    if not query:
        return None, _empty_meta("empty MF query")
    df = _load_amfi_nav_table()
    if df.empty:
        return None, _empty_meta("AMFI NAV unavailable")
    q = query.strip()
    q_upper = q.upper()
    # Match exact ISIN first.
    if q_upper.startswith("INF"):
        m = df[(df["isin_payout"].str.upper() == q_upper) | (df["isin_reinvest"].str.upper() == q_upper)]
        if not m.empty:
            row = m.iloc[0]
            return float(row["nav"]), {"source_status": f"live AMFI NAV {row['date']}", "scheme_name": row["scheme_name"]}
    # Otherwise token-based scheme-name match.
    nq = _norm(q)
    q_tokens = [t for t in nq.split() if len(t) > 2 and t not in {"fund","direct","plan","growth","option","dp","dir","gr"}]
    best = None
    best_score = -1
    for _, row in df.iterrows():
        name = _norm(row["scheme_name"])
        # prefer Direct Growth schemes
        score = sum(1 for t in q_tokens if t in name)
        if "direct" in name: score += 2
        if "growth" in name: score += 2
        if score > best_score:
            best_score = score; best = row
    if best is not None and best_score >= max(3, min(5, len(q_tokens))):
        return float(best["nav"]), {"source_status": f"live AMFI NAV {best['date']}", "scheme_name": best["scheme_name"]}
    return None, _empty_meta("AMFI no confident match")


def safe_price(ticker: str):
    t = str(ticker or "").strip()
    tu = t.upper()
    if not t or tu in {"NA", "N/A"}:
        return None, _empty_meta("manual/no ticker")
    if tu == "SGB":
        return get_sgb_rate()
    if tu.startswith("MF:") or tu.startswith("INF"):
        return get_amfi_nav(t)
    if tu in BOND_PRICE_BY_ID:
        return BOND_PRICE_BY_ID[tu], {"source_status": "live bond mark from broker screenshot/manual feed"}
    if yf is None:
        return None, _empty_meta("yfinance not installed")
    try:
        return _last_yahoo_close(t)
    except Exception as e:
        return None, _empty_meta(str(e)[:100])


def get_fx_rates(defaults: dict) -> dict:
    rates = dict(defaults)
    usd, _ = safe_price("INR=X")
    eur, _ = safe_price("EURINR=X")
    if usd:
        rates["USDINR"] = usd
        rates["USD_SOURCE"] = "live Yahoo/XE proxy"
    else:
        rates["USD_SOURCE"] = "fallback"
    if eur:
        rates["EURINR"] = eur
        rates["EUR_SOURCE"] = "live Yahoo/XE proxy"
    else:
        rates["EUR_SOURCE"] = "fallback"
    return rates


def get_market_dashboard(default_fx: dict) -> pd.DataFrame:
    rows = []
    for name, ticker in INDEX_TICKERS.items():
        price, meta = safe_price(ticker)
        fallback = default_fx.get("USDINR") if name == "USD/INR" else default_fx.get("EURINR") if name == "EUR/INR" else None
        chg = meta.get("day_change")
        rows.append({
            "Instrument": name,
            "Ticker": ticker,
            "Last": price if price is not None else fallback,
            "Move": "🟢 ▲" if chg and chg > 0 else ("🔴 ▼" if chg and chg < 0 else "—"),
            "Day %": meta.get("day_change_pct"),
            "52W High": meta.get("52w_high"),
            "52W Low": meta.get("52w_low"),
            "Volume": meta.get("volume"),
            "Status": meta.get("source_status", "")
        })
    return pd.DataFrame(rows)


def get_news(ticker: str, name: str = ""):
    if not ticker or yf is None or str(ticker).upper().startswith("MF:") or str(ticker).upper() == "SGB":
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


def get_history(ticker: str, period="1y") -> pd.DataFrame:
    if str(ticker or "").upper().startswith("MF:") or str(ticker or "").upper() == "SGB":
        return pd.DataFrame()
    return _history(ticker, period)
