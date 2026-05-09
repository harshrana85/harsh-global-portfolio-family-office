from __future__ import annotations
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

INDEX_TICKERS = {
    "Nifty 50": "^NSEI", "Nifty Bank": "^NSEBANK", "Sensex": "^BSESN", "India VIX": "^INDIAVIX",
    "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT",
    "FTSE 100": "^FTSE", "DAX": "^GDAXI", "Nikkei 225": "^N225", "Hang Seng": "^HSI",
    "Gold USD/oz": "GC=F", "Silver USD/oz": "SI=F", "Brent Crude": "BZ=F", "WTI Crude": "CL=F",
    "USD/INR": "INR=X", "EUR/INR": "EURINR=X"
}
CURRENCY_SYMBOL = {"INR": "₹", "USD": "$", "EUR": "€", "AED": "د.إ"}

# Manual live bond marks from user's broker screenshot / IBKR-style statement.
# Stored as clean price per 100 face; returned as rate = price / 100 for valuation.
BOND_PRICE_TABLE = {
    "US04686E4K56": {"price": 98.8070, "name": "Athene Global Funding 4.721 Oct 2029"},
    "US912810FT08": {"price": 101.7660, "name": "US Treasury 4.5 Feb 2036"},
    "US91282CPE56": {"price": 99.46995, "name": "US Treasury 3.5 Oct 2027"},
    "US30231GBF81": {"price": 90.7560, "name": "Exxon Mobil 4.227 Mar 2040"},
}


def _empty_meta(error: str = ""):
    return {"52w_high": None, "52w_low": None, "volume": None, "day_high": None, "day_low": None, "market_cap": None, "source_status": error or "manual"}


def _history(ticker: str, period: str = "1y") -> pd.DataFrame:
    if yf is None or not ticker:
        return pd.DataFrame()
    try:
        # yf.download is more reliable on Streamlit Cloud than Ticker.history for many NSE/LSE symbols.
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


def safe_price(ticker: str):
    t = str(ticker or "").strip().upper()
    if t in BOND_PRICE_TABLE:
        px = float(BOND_PRICE_TABLE[t]["price"])
        return px / 100.0, {
            "52w_high": None, "52w_low": None, "volume": None,
            "day_change": None, "day_change_pct": None,
            "source_status": "live bond mark",
            "clean_price_100": px,
        }
    if not ticker or str(ticker).strip().upper() in {"SGB", "NA", "N/A"}:
        return None, _empty_meta("manual/no ticker")
    if yf is None:
        return None, _empty_meta("yfinance not installed")
    try:
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
            "source_status": "live fetched",
        }
        return last, meta
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


def get_history(ticker: str, period="1y") -> pd.DataFrame:
    return _history(ticker, period)
