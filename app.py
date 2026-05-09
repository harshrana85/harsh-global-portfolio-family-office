from __future__ import annotations
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from db import init_db, get_holdings, save_holdings, add_snapshot, get_snapshots
from market_data import safe_price, get_fx_rates, get_market_dashboard, get_news, get_history, CURRENCY_SYMBOL
from analytics import enrich, totals, fmt_money, arrow
from portfolio_seed import DEFAULT_FX

st.set_page_config(page_title="Harsh Global Portfolio - Family Office", page_icon="◆", layout="wide")

CSS = """
<style>
:root { --bg:#f5f6f7; --card:#ffffff; --ink:#172033; --muted:#657084; --green:#16834a; --red:#c9342f; --gold:#b98b2f; --line:#e3e7ee; }
.stApp { background: linear-gradient(180deg,#f7f8fa 0%,#eef1f5 100%); color: var(--ink); }
.block-container { padding-top: 1.25rem; }
[data-testid="stSidebar"] { background: #f0f2f5; border-right:1px solid var(--line); }
.fo-watermark:before { content:"HARSH GLOBAL PORTFOLIO · FAMILY OFFICE"; position:fixed; top:45%; left:24%; font-size:42px; color:rgba(20,31,49,0.035); transform:rotate(-22deg); z-index:0; pointer-events:none; font-weight:800; letter-spacing:3px; }
.card { background:white; border:1px solid var(--line); border-radius:18px; padding:18px 20px; box-shadow:0 10px 26px rgba(20,31,49,.06); }
.metric-title { color:var(--muted); font-size:13px; text-transform:uppercase; letter-spacing:.08em; }
.metric-value { font-size:24px; font-weight:800; color:var(--ink); margin-top:4px; }
.good { color:var(--green); font-weight:800; } .bad { color:var(--red); font-weight:800; }
.news-card { background:#fff; border-left:4px solid #27364a; padding:12px 14px; margin-bottom:10px; border-radius:12px; box-shadow:0 5px 16px rgba(20,31,49,.05); }
.small-muted { color:var(--muted); font-size:12px; }
thead tr th { background-color:#eef2f6 !important; font-size:11px !important; }
[data-testid="stDataFrame"] { font-size:11px !important; }
.small-table {font-size:11px;}
</style>
<div class="fo-watermark"></div>
"""
st.markdown(CSS, unsafe_allow_html=True)

PASSWORD = st.secrets.get("APP_PASSWORD", os.environ.get("APP_PASSWORD", "Harsh@1985"))

def login():
    if st.session_state.get("auth"):
        return True
    st.markdown("## Harsh Global Portfolio - Family Office")
    st.caption("Private password-controlled dashboard")
    pw = st.text_input("Password", type="password")
    if st.button("Enter", use_container_width=True):
        if pw == PASSWORD:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Incorrect password")
    return False

if not login():
    st.stop()

init_db()

@st.cache_data(ttl=600, show_spinner=False)
def live_price_map(tickers):
    d = {}
    meta = {}
    for t in tickers:
        if not t:
            continue
        p, m = safe_price(str(t).strip())
        if p:
            d[str(t).strip()] = p
        meta[str(t).strip()] = m
    return d, meta

@st.cache_data(ttl=900, show_spinner=False)
def fx_cached():
    return get_fx_rates(DEFAULT_FX)

raw = get_holdings()
live_fx = fx_cached()
# Live FX and live MTM are automatic now; no confusing sidebar toggles.
fx = live_fx
mark_to_market = True

# Fetch all meaningful identifiers: Yahoo tickers, MF: AMFI queries, SGB proxy, ISIN bond marks.
def valid_fetch_ticker(t):
    t = str(t or "").strip()
    if not t or t.upper() in {"NA", "N/A"}:
        return False
    return True
fetchable = [t for t in raw["ticker"].dropna().unique() if valid_fetch_ticker(t)]
prices, meta_map = live_price_map(tuple(fetchable))
df = enrich(raw, prices, fx, mark_to_market=mark_to_market)
T = totals(df)
add_snapshot(T["current_value_inr"], T["invested_value_inr"], T["current_value_inr"], T["pnl_inr"])

st.sidebar.title("◆ Family Office")
st.sidebar.caption("Harsh Global Portfolio")
page = st.sidebar.radio("Navigation", [
    "Dashboard", "Indian Portfolio", "US Portfolio", "Returns & Yield", "Consolidated Portfolio", "Holding Intelligence", "Net Worth Growth", "Admin / Edit Holdings"
])
st.sidebar.divider()
st.sidebar.metric("Net Worth", fmt_money(T["current_value_inr"]))
st.sidebar.metric("P/L", fmt_money(T["pnl_inr"]), f"{T['pnl_inr']/max(abs(T['invested_value_inr']),1):.1%}")
st.sidebar.caption(f"Live FX: $1 = ₹{live_fx.get('USDINR', DEFAULT_FX['USDINR']):.1f} | €1 = ₹{live_fx.get('EURINR', DEFAULT_FX['EURINR']):.1f}")
st.sidebar.caption("Live MTM: automatic for stocks, ETFs, MF NAV, SGB proxy and marked US bonds")

DISPLAY_COLS = ["move_arrow", "portfolio", "asset_class", "sub_class", "name", "ticker", "currency", "quantity", "invested_rate", "live_rate", "current_rate", "invested_value", "current_value", "current_value_usd", "current_value_inr", "pnl_usd", "pnl_inr", "pnl_pct", "live_move_pct", "expected_return_pct", "yield_dividend_pct", "total_return_yield_inr", "price_status", "valuation_status"]

MONEY_NATIVE_COLS = ["invested_rate", "live_rate", "current_rate", "invested_value", "current_value"]
MONEY_INR_COLS = ["current_value_inr", "pnl_inr", "total_return_yield_inr", "expected_return_amount_inr", "yield_dividend_amount_inr"]
MONEY_USD_COLS = ["current_value_usd", "invested_value_usd", "pnl_usd"]
PCT_COLS = ["pnl_pct", "live_move_pct", "expected_return_pct", "yield_dividend_pct"]
NUM_COLS = ["quantity"]

def _sym(ccy: str) -> str:
    return {"INR":"₹", "USD":"$", "EUR":"€", "AED":"د.إ"}.get(str(ccy).upper(), "")

def fmt_native(value, ccy):
    try:
        if pd.isna(value):
            return ""
        return f"{_sym(ccy)}{float(value):,.1f}"
    except Exception:
        return "" if value is None else str(value)

def fmt_inr(value):
    try:
        if pd.isna(value):
            return ""
        return f"₹{float(value):,.1f}"
    except Exception:
        return "" if value is None else str(value)

def fmt_usd(value):
    try:
        if pd.isna(value):
            return ""
        return f"${float(value):,.1f}"
    except Exception:
        return "" if value is None else str(value)

def fmt_pct1(value):
    try:
        if pd.isna(value):
            return ""
        return f"{float(value)*100:.1f}%"
    except Exception:
        return ""

def fmt_num1(value):
    try:
        if pd.isna(value):
            return ""
        return f"{float(value):,.1f}"
    except Exception:
        return "" if value is None else str(value)

def display_table(data: pd.DataFrame, cols=None, add_total=True) -> pd.DataFrame:
    cols = cols or DISPLAY_COLS
    show = data[[c for c in cols if c in data.columns]].copy()
    if add_total and not show.empty:
        total_row = {c:"" for c in show.columns}
        total_row["name"] = "TOTAL"
        total_row["move_arrow"] = "🟢 ▲" if data.get("pnl_inr", pd.Series([0])).sum() >= 0 else "🔴 ▼"
        total_row["currency"] = "INR"
        for c in ["invested_value", "current_value", "current_value_inr", "current_value_usd", "invested_value_usd", "pnl_usd", "pnl_inr", "total_return_yield_inr", "expected_return_amount_inr", "yield_dividend_amount_inr"]:
            if c in data.columns and c in total_row:
                total_row[c] = data[c].sum()
        show = pd.concat([show, pd.DataFrame([total_row])], ignore_index=True)
    # Format native currency columns row-by-row so ₹/$/€/د.إ always show correctly.
    if "currency" in show.columns:
        for c in MONEY_NATIVE_COLS:
            if c in show.columns:
                show[c] = [fmt_native(v, ccy) for v, ccy in zip(show[c], show["currency"])]
    for c in MONEY_INR_COLS:
        if c in show.columns:
            show[c] = show[c].apply(fmt_inr)
    for c in MONEY_USD_COLS:
        if c in show.columns:
            show[c] = show[c].apply(fmt_usd)
    for c in PCT_COLS:
        if c in show.columns:
            show[c] = show[c].apply(fmt_pct1)
    for c in NUM_COLS:
        if c in show.columns:
            show[c] = show[c].apply(fmt_num1)
    # Shorten long status text for dense table fit.
    rename = {
        "move_arrow":"Move", "portfolio":"Portfolio", "asset_class":"Asset", "sub_class":"Type", "name":"Holding",
        "ticker":"Ticker", "currency":"Ccy", "quantity":"Qty", "invested_rate":"Invested Rate",
        "live_rate":"Live Rate", "current_rate":"Current Rate", "invested_value":"Invested",
        "current_value":"Current", "current_value_usd":"Current USD", "invested_value_usd":"Invested USD", "pnl_usd":"P/L USD", "current_value_inr":"Current INR", "pnl_inr":"P/L INR",
        "pnl_pct":"P/L %", "live_move_pct":"Live Move", "expected_return_pct":"Return %",
        "yield_dividend_pct":"Yield/Div %", "total_return_yield_inr":"Return+Yield INR",
        "price_status":"Price", "valuation_status":"Valuation"
    }
    return show.rename(columns={k:v for k,v in rename.items() if k in show.columns})

def styled_table(data: pd.DataFrame, title: str):
    st.subheader(title)
    st.dataframe(display_table(data), use_container_width=True, height=470, hide_index=True)

def format_market_table(md: pd.DataFrame) -> pd.DataFrame:
    out = md.copy()
    for c in ["Last", "52W High", "52W Low", "Volume"]:
        if c in out.columns:
            out[c] = out[c].apply(fmt_num1)
    if "Day %" in out.columns:
        out["Day %"] = out["Day %"].apply(fmt_pct1)
    return out

def format_currency_exposure(by_ccy: pd.DataFrame) -> pd.DataFrame:
    out = by_ccy.copy()
    if "currency" in out.columns and "current_native" in out.columns:
        out["current_native"] = [fmt_native(v, c) for v, c in zip(out["current_native"], out["currency"])]
    if "current_inr" in out.columns:
        out["current_inr"] = out["current_inr"].apply(fmt_inr)
    return out.rename(columns={"currency":"Currency", "current_native":"Native Current", "current_inr":"Current INR"})

if page == "Dashboard":
    st.title("Harsh Global Portfolio - Family Office")
    st.caption("Professional consolidated dashboard · live NAV/prices · INR base with USD equivalents · no manual FX/MTM toggles")
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f"<div class='card'><div class='metric-title'>Net Worth Today</div><div class='metric-value'>{fmt_money(T['current_value_inr'])}</div><div class='small-muted'>≈ ${T.get('current_value_usd',0):,.1f}</div></div>", unsafe_allow_html=True)
    pnl_cls = "good" if T["pnl_inr"] >= 0 else "bad"
    c2.markdown(f"<div class='card'><div class='metric-title'>Current Profit / Loss</div><div class='metric-value {pnl_cls}'>{arrow(T['pnl_inr'])} {fmt_money(T['pnl_inr'])}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><div class='metric-title'>Invested Value</div><div class='metric-value'>{fmt_money(T['invested_value_inr'])}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><div class='metric-title'>Expected Income + Yield</div><div class='metric-value'>{fmt_money(T['total_return_yield_inr'])}</div></div>", unsafe_allow_html=True)

    left,right = st.columns([1.05,1])
    with left:
        by_asset = df.groupby("asset_class", as_index=False)["current_value_inr"].sum().sort_values("current_value_inr", ascending=False)
        fig = px.pie(by_asset, values="current_value_inr", names="asset_class", hole=.55, title="Portfolio Allocation by Asset Class")
        fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Market Watch")
        md = get_market_dashboard(live_fx)
        st.dataframe(format_market_table(md), use_container_width=True, height=430, hide_index=True)
    st.subheader("Top Positions")
    top = df.sort_values("current_value_inr", ascending=False).head(12)
    st.dataframe(display_table(top, ["move_arrow","name","asset_class","currency","current_value","current_value_inr","pnl_inr","live_rate","live_move_pct","yield_dividend_pct","price_status"], add_total=False), use_container_width=True, hide_index=True)
    with st.expander("Data fetch status / why some prices are manual"):
        st.write("Live prices are fetched automatically. Mutual funds use AMFI NAV × units, SGB uses live gold INR/gram proxy × 160 units, listed shares/ETFs use Yahoo Finance, and the four USD bonds use your latest broker marks. Fixed assets, FDs, bank balances, Oman/GASCBM and real estate stay constant.")
        st.dataframe(df[["name","ticker","portfolio","asset_class","quantity","live_rate","move_arrow","live_move_pct","price_status","valuation_status","data_source"]], use_container_width=True)

elif page == "Indian Portfolio":
    st.title("Indian Portfolio")
    ind = df[df["portfolio"].eq("INDIA")]
    tabs = st.tabs(["All", "Fixed Income", "Mutual Funds", "Gold", "Real Estate", "Equity", "Cash"])
    filters = [None, "Fixed Income", "Mutual Fund", "Gold", "Real Estate", "Equity", "Cash"]
    for tab, filt in zip(tabs, filters):
        with tab:
            data = ind if filt is None else ind[ind["asset_class"].eq(filt)]
            styled_table(data, filt or "All Indian Assets")

elif page == "US Portfolio":
    st.title("US / Global Portfolio")
    us = df[df["portfolio"].eq("US/GLOBAL")]
    tabs = st.tabs(["All", "Equity", "ETF", "Fixed Income", "Cash", "Real Estate", "Liability"])
    filters = [None, "Equity", "ETF", "Fixed Income", "Cash", "Real Estate", "Liability"]
    for tab, filt in zip(tabs, filters):
        with tab:
            data = us if filt is None else us[us["asset_class"].eq(filt)]
            st.subheader(filt or "All US / Global Assets")
            us_cols = ["move_arrow","portfolio","asset_class","sub_class","name","ticker","currency","quantity","current_value_usd","current_value_inr","pnl_usd","pnl_inr","yield_dividend_pct","total_return_yield_inr","price_status","valuation_status"]
            st.dataframe(display_table(data, us_cols), use_container_width=True, height=470, hide_index=True)

elif page == "Returns & Yield":
    st.title("Returns & Yield")
    st.caption("Returns and yield/dividends are separate. Total combines expected capital return plus dividend/yield income.")
    ret = df.copy()
    ret["Expected Return ₹"] = ret["expected_return_amount_inr"]
    ret["Dividend / Yield ₹"] = ret["yield_dividend_amount_inr"]
    ret["Total Return + Yield ₹"] = ret["total_return_yield_inr"]
    ret_display = ret[["portfolio","asset_class","name","currency","current_value_inr","expected_return_pct","Expected Return ₹","yield_dividend_pct","Dividend / Yield ₹","Total Return + Yield ₹"]].copy()
    ret_display["current_value_inr"] = ret_display["current_value_inr"].apply(fmt_inr)
    ret_display["Expected Return ₹"] = ret_display["Expected Return ₹"].apply(fmt_inr)
    ret_display["Dividend / Yield ₹"] = ret_display["Dividend / Yield ₹"].apply(fmt_inr)
    ret_display["Total Return + Yield ₹"] = ret_display["Total Return + Yield ₹"].apply(fmt_inr)
    ret_display["expected_return_pct"] = ret_display["expected_return_pct"].apply(fmt_pct1)
    ret_display["yield_dividend_pct"] = ret_display["yield_dividend_pct"].apply(fmt_pct1)
    st.dataframe(ret_display.rename(columns={"portfolio":"Portfolio","asset_class":"Asset","name":"Holding","currency":"Ccy","current_value_inr":"Current INR","expected_return_pct":"Return %","yield_dividend_pct":"Yield/Div %"}), use_container_width=True, height=620, hide_index=True)
    st.metric("Total Expected Return + Yield", fmt_money(T["total_return_yield_inr"]))

elif page == "Consolidated Portfolio":
    st.title("Consolidated Portfolio")
    st.caption("Merged portfolio view with native currencies and final INR conversion.")
    styled_table(df, "All Holdings - Multi-Currency converted to INR")
    by_ccy = df.groupby("currency", as_index=False).agg(current_native=("current_value","sum"), current_inr=("current_value_inr","sum"))
    st.subheader("Currency Exposure")
    st.dataframe(format_currency_exposure(by_ccy), use_container_width=True, hide_index=True)

elif page == "Holding Intelligence":
    st.title("Holding Intelligence")
    st.caption("Technicals, chart, 52-week high/low, volume, news flashes, results/dividends where available from free feeds.")
    choices = df[df["ticker"].fillna("").ne("")][["name","ticker"]].drop_duplicates()
    label = st.selectbox("Select holding", choices.apply(lambda r: f"{r['name']} · {r['ticker']}", axis=1))
    ticker = label.split("·")[-1].strip()
    name = label.split("·")[0].strip()
    price, meta = safe_price(ticker)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Current Rate", f"{price:,.2f}" if price else "Fallback only")
    c2.metric("52W High", f"{meta.get('52w_high',0):,.2f}" if meta.get('52w_high') else "n/a")
    c3.metric("52W Low", f"{meta.get('52w_low',0):,.2f}" if meta.get('52w_low') else "n/a")
    c4.metric("Volume", f"{meta.get('volume',0):,.0f}" if meta.get('volume') else "n/a")
    hist = get_history(ticker, "2y")
    if not hist.empty:
        fig = go.Figure(data=[go.Candlestick(x=hist["Date"], open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"])])
        fig.update_layout(title=f"{name} Price Chart", height=480, xaxis_rangeslider_visible=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("News Flashes")
    news = get_news(ticker, name)
    if news:
        for n in news:
            st.markdown(f"<div class='news-card'><b>{n.get('title','News')}</b><br><span class='small-muted'>{n.get('publisher','')}</span><br><a href='{n.get('link','#')}' target='_blank'>Open news</a></div>", unsafe_allow_html=True)
    else:
        st.info("No free news returned for this ticker right now.")
    st.subheader("AI Portfolio Chat")
    q = st.text_input("Ask about this holding or your portfolio")
    if st.button("Ask AI") and q:
        api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        context = df[["name","asset_class","currency","current_value_inr","pnl_inr","expected_return_pct","yield_dividend_pct"]].to_string(max_rows=80)
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":"You are a concise family office portfolio assistant. Use INR values. No personalized financial advice; provide analytical commentary."},{"role":"user","content":f"Portfolio context:\n{context}\n\nQuestion: {q}"}])
                st.write(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"AI unavailable: {e}")
        else:
            st.info("Add OPENAI_API_KEY in Streamlit secrets to enable full AI chat. Basic view: ask about allocation, P/L, yields, and concentration based on the dashboard tables.")

elif page == "Net Worth Growth":
    st.title("Net Worth Growth")
    snaps = get_snapshots()
    if len(snaps) > 0:
        fig = px.line(snaps, x="snapshot_date", y="net_worth_inr", markers=True, title="Daily Net Worth Growth")
        fig.update_layout(height=500, yaxis_tickprefix="₹", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(snaps, use_container_width=True)
    else:
        st.info("Snapshots begin after the first daily app run.")

elif page == "Admin / Edit Holdings":
    st.title("Admin / Edit Holdings")
    st.caption("Edit, add, delete or replace holdings here. This is software data stored in SQLite, not Excel.")
    editable = get_holdings(active_only=False)
    edited = st.data_editor(editable, num_rows="dynamic", use_container_width=True, height=620, key="holdings_editor")
    c1,c2 = st.columns([1,4])
    if c1.button("Save Changes", type="primary"):
        save_holdings(edited)
        st.success("Saved. All pages will recalculate from the updated software database.")
        st.cache_data.clear()
        st.rerun()
    if c2.button("Reset to Seed Data"):
        init_db(force=True)
        st.success("Reset to the starting portfolio data.")
        st.cache_data.clear()
        st.rerun()
