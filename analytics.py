
from __future__ import annotations
import pandas as pd
import numpy as np

DEFAULT_FX = {"USDINR": 94.44, "EURINR": 111.28, "AEDINR": 25.71}
CURRENCY_SYMBOLS = {"INR":"₹", "USD":"$", "EUR":"€", "AED":"د.إ"}

def fx_to_inr(currency: str, fx: dict | None = None) -> float:
    fx = fx or DEFAULT_FX
    c = str(currency).upper()
    if c == "INR": return 1.0
    if c == "USD": return float(fx.get("USDINR", DEFAULT_FX["USDINR"]))
    if c == "EUR": return float(fx.get("EURINR", DEFAULT_FX["EURINR"]))
    if c == "AED": return float(fx.get("AEDINR", DEFAULT_FX["AEDINR"]))
    return 1.0

def enrich(df: pd.DataFrame, live_prices: dict | None = None, fx: dict | None = None) -> pd.DataFrame:
    """
    Correct accounting separation:
    - invested_rate / quantity = cost basis
    - current_rate = live price when available, otherwise fallback_current_rate
    - invested value NEVER gets overwritten by live price
    - current value is allowed to move with live prices
    - constants remain fixed by pricing_mode='constant'
    """
    fx = fx or DEFAULT_FX
    live_prices = live_prices or {}
    out = df.copy()
    for c in ["ticker","pricing_mode","currency","asset_class","portfolio","name"]:
        if c in out.columns:
            out[c] = out[c].fillna("").astype(str)
    for c in ["quantity","invested_rate","fallback_current_rate","expected_return_pct","yield_dividend_pct"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    out["live_rate"] = out["ticker"].map(live_prices)
    out["is_constant"] = out["pricing_mode"].str.lower().eq("constant")

    # Current rate logic
    # constants stay at fallback; live/proxy use fetched when available; manual fallback otherwise
    out["current_rate"] = np.where(
        (~out["is_constant"]) & out["live_rate"].notna(),
        out["live_rate"],
        out["fallback_current_rate"]
    )

    # Bonds are entered as face value quantity and price per 100.
    # Regular securities are quantity x rate.
    out["invested_value"] = out["quantity"] * out["invested_rate"]
    out["current_value"] = out["quantity"] * out["current_rate"]

    out["fx_to_inr"] = out["currency"].apply(lambda c: fx_to_inr(c, fx))
    out["invested_value_inr"] = out["invested_value"] * out["fx_to_inr"]
    out["current_value_inr"] = out["current_value"] * out["fx_to_inr"]
    out["pnl_inr"] = out["current_value_inr"] - out["invested_value_inr"]
    out["pnl_pct"] = np.where(out["invested_value_inr"].abs() > 0, out["pnl_inr"] / out["invested_value_inr"], 0.0)

    # USD equivalent display for INR assets like UAE real estate if requested
    out["usd_equivalent"] = np.where(
        out.get("show_usd_equivalent", 0).astype(float).fillna(0).eq(1),
        out["current_value_inr"] / float(fx.get("USDINR", DEFAULT_FX["USDINR"])),
        np.nan
    )

    out["expected_return_amount_inr"] = out["current_value_inr"] * out["expected_return_pct"]
    out["yield_dividend_amount_inr"] = out["current_value_inr"] * out["yield_dividend_pct"]
    out["total_return_yield_inr"] = out["expected_return_amount_inr"] + out["yield_dividend_amount_inr"]

    out["move_arrow"] = np.where(out["pnl_inr"] > 0, "🟢 ▲", np.where(out["pnl_inr"] < 0, "🔴 ▼", "—"))
    out["price_status"] = np.where(out["is_constant"], "Constant", np.where(out["live_rate"].notna(), "Live/Proxy", "Fallback"))
    return out

def totals(df: pd.DataFrame):
    keys = ["invested_value_inr","current_value_inr","pnl_inr","expected_return_amount_inr","yield_dividend_amount_inr","total_return_yield_inr"]
    return {k: float(df[k].sum()) for k in keys}

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
