from __future__ import annotations
import pandas as pd
import numpy as np
from portfolio_seed import DEFAULT_FX

CURRENCY_SYMBOLS = {"INR":"₹", "USD":"$", "EUR":"€", "AED":"د.إ"}

def fx_to_inr(currency: str, fx: dict) -> float:
    c = str(currency).upper()
    if c == "INR": return 1.0
    if c == "USD": return float(fx.get("USDINR", DEFAULT_FX["USDINR"]))
    if c == "EUR": return float(fx.get("EURINR", DEFAULT_FX["EURINR"]))
    if c == "AED": return float(fx.get("AEDINR", DEFAULT_FX["AEDINR"]))
    return 1.0

def enrich(df: pd.DataFrame, live_prices: dict | None = None, fx: dict | None = None, mark_to_market: bool = True) -> pd.DataFrame:
    fx = fx or DEFAULT_FX
    live_prices = live_prices or {}
    out = df.copy()
    out["ticker"] = out["ticker"].fillna("").astype(str).str.strip()
    out["live_rate"] = out["ticker"].map(live_prices)
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce").fillna(0)
    out["invested_rate"] = pd.to_numeric(out["invested_rate"], errors="coerce").fillna(0)
    out["fallback_current_rate"] = pd.to_numeric(out["fallback_current_rate"], errors="coerce").fillna(0)
    out["expected_return_pct"] = pd.to_numeric(out["expected_return_pct"], errors="coerce").fillna(0)
    out["yield_dividend_pct"] = pd.to_numeric(out["yield_dividend_pct"], errors="coerce").fillna(0)

    asset = out["asset_class"].astype(str).str.lower()
    sub = out["sub_class"].astype(str).str.lower()
    tick = out["ticker"].astype(str).str.upper()

    # Live valuation rules:
    # - Indian & US listed equities/ETFs update when valid live price is fetched and quantity is meaningful.
    # - Mutual funds update automatically from AMFI NAV using units.
    # - SGB updates automatically from live gold INR/gram proxy using 160 units.
    # - Broker-marked US bonds update from price/100 feed if identifier is present.
    is_mf = asset.eq("mutual fund")
    is_sgb = tick.eq("SGB") | sub.str.contains("sovereign gold", na=False)
    is_listed = asset.isin(["equity", "etf"])
    is_bond_mark = asset.eq("fixed income") & out["live_rate"].notna() & out["ticker"].str.upper().str.startswith("US")
    allowed = out["live_rate"].notna() & (
        is_mf | is_sgb | is_bond_mark | (is_listed & (out["quantity"] > 0))
    )
    out["live_valuation_allowed"] = allowed if mark_to_market else (is_mf | is_sgb | is_bond_mark) & out["live_rate"].notna()
    out["current_rate"] = np.where(out["live_valuation_allowed"], out["live_rate"], out["fallback_current_rate"])
    out["invested_value"] = out["quantity"] * out["invested_rate"]
    out["current_value"] = out["quantity"] * out["current_rate"]
    out["fx_to_inr"] = out["currency"].apply(lambda c: fx_to_inr(c, fx))
    out["invested_value_inr"] = out["invested_value"] * out["fx_to_inr"]
    out["current_value_inr"] = out["current_value"] * out["fx_to_inr"]
    usd_inr = float(fx.get("USDINR", DEFAULT_FX["USDINR"])) or DEFAULT_FX["USDINR"]
    out["invested_value_usd"] = out["invested_value_inr"] / usd_inr
    out["current_value_usd"] = out["current_value_inr"] / usd_inr
    out["pnl_usd"] = (out["current_value_inr"] - out["invested_value_inr"]) / usd_inr
    out["pnl_inr"] = out["current_value_inr"] - out["invested_value_inr"]
    out["pnl_pct"] = np.where(out["invested_value_inr"].abs() > 0, out["pnl_inr"] / out["invested_value_inr"], 0)
    out["live_move"] = out["live_rate"] - out["fallback_current_rate"]
    out["live_move_pct"] = np.where(out["fallback_current_rate"].abs() > 0, out["live_move"] / out["fallback_current_rate"], np.nan)
    out["move_arrow"] = np.where(out["live_move"].fillna(0) > 0, "🟢 ▲", np.where(out["live_move"].fillna(0) < 0, "🔴 ▼", "—"))
    out["expected_return_amount_inr"] = out["current_value_inr"] * out["expected_return_pct"]
    out["yield_dividend_amount_inr"] = out["current_value_inr"] * out["yield_dividend_pct"]
    out["total_return_yield_inr"] = out["expected_return_amount_inr"] + out["yield_dividend_amount_inr"]
    out["price_status"] = np.where(out["live_rate"].notna(), "Live fetched", "Manual/constant")
    out["valuation_status"] = np.where(out["live_valuation_allowed"], "Live applied", "Manual value")
    return out

def totals(df: pd.DataFrame):
    keys = ["invested_value_inr", "current_value_inr", "pnl_inr", "expected_return_amount_inr", "yield_dividend_amount_inr", "total_return_yield_inr"]
    out = {k: float(df[k].sum()) for k in keys}
    if "current_value_usd" in df.columns:
        out["current_value_usd"] = float(df["current_value_usd"].sum())
    if "invested_value_usd" in df.columns:
        out["invested_value_usd"] = float(df["invested_value_usd"].sum())
    return out

def fmt_money(x, currency="INR", decimals=1):
    s = CURRENCY_SYMBOLS.get(str(currency).upper(), "")
    try: return f"{s}{float(x):,.{decimals}f}"
    except Exception: return f"{s}{x}"

def fmt_pct(x, decimals=1):
    try: return f"{float(x)*100:.{decimals}f}%"
    except Exception: return ""

def arrow(x):
    try: return "🟢 ▲" if float(x) >= 0 else "🔴 ▼"
    except Exception: return ""
