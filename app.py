
from __future__ import annotations
import os, pandas as pd, streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from db import init_db, get_holdings, save_holdings, add_snapshot, get_snapshots
from market_data import safe_price, get_fx_rates, get_market_dashboard, get_news, get_history
from analytics import enrich, totals, fmt_money, fmt_pct, arrow
from portfolio_seed import DEFAULT_FX

st.set_page_config(page_title="Harsh Global Portfolio - Family Office", page_icon="◆", layout="wide")

CSS = """
<style>
:root{--bg:#f5f6f7;--card:#fff;--ink:#172033;--muted:#647085;--green:#16834a;--red:#c9342f;--gold:#b98b2f;--line:#e3e7ee;}
.stApp{background:linear-gradient(135deg,#f8fafc 0%,#eef2f6 48%,#f5f2e8 100%);color:var(--ink);}
.block-container{padding-top:1rem;max-width:1500px;}
[data-testid="stSidebar"]{background:#eaf0f4;border-right:1px solid var(--line);}
.fo-watermark:before{content:"HARSH GLOBAL PORTFOLIO · FAMILY OFFICE";position:fixed;top:45%;left:20%;font-size:46px;color:rgba(20,31,49,0.035);transform:rotate(-22deg);z-index:0;pointer-events:none;font-weight:900;letter-spacing:3px;}
.card{background:white;border:1px solid var(--line);border-radius:20px;padding:16px 18px;box-shadow:0 12px 28px rgba(20,31,49,.07);transition:all .25s ease;}
.card:hover{transform:translateY(-3px);box-shadow:0 18px 34px rgba(20,31,49,.10);}
.metric-title{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.09em;}
.metric-value{font-size:24px;font-weight:850;color:var(--ink);margin-top:4px;}
.good{color:var(--green);font-weight:850}.bad{color:var(--red);font-weight:850}
.bullbear{font-size:34px;animation:floaty 3.2s ease-in-out infinite;}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.tape{background:#152033;color:white;border-radius:14px;padding:10px 14px;margin-bottom:12px;overflow:hidden;white-space:nowrap;}
.tape span{display:inline-block;padding-right:38px;animation:marquee 35s linear infinite;}
@keyframes marquee{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}
.news-card{background:#fff;border-left:4px solid #27364a;padding:12px 14px;margin-bottom:10px;border-radius:12px;box-shadow:0 5px 16px rgba(20,31,49,.05);}
.small-muted{color:var(--muted);font-size:12px}
[data-testid="stDataFrame"]{font-size:11px!important}
thead tr th{font-size:11px!important;background-color:#eef2f6!important}
</style><div class="fo-watermark"></div>
"""
st.markdown(CSS, unsafe_allow_html=True)

PASSWORD = st.secrets.get("APP_PASSWORD", os.environ.get("APP_PASSWORD", "Harsh@1985"))
if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("## Harsh Global Portfolio - Family Office")
    st.caption("Private password-controlled terminal")
    pw = st.text_input("Password", type="password")
    if st.button("Enter", use_container_width=True):
        if pw == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        st.error("Incorrect password")
    st.stop()

init_db()

@st.cache_data(ttl=900, show_spinner=False)
def fx_cached():
    return get_fx_rates(DEFAULT_FX)

@st.cache_data(ttl=900, show_spinner=False)
def price_map(tickers):
    d, meta = {}, {}
    for t in tickers:
        p, m = safe_price(t)
        if p is not None:
            d[t] = p
        meta[t] = m
    return d, meta

raw = get_holdings()
fetchable = [str(t).strip() for t in raw["ticker"].dropna().unique() if str(t).strip()]
fx = fx_cached()
prices, meta_map = price_map(tuple(fetchable))
df = enrich(raw, prices, fx)
T = totals(df)
add_snapshot(T["current_value_inr"], T["invested_value_inr"], T["current_value_inr"], T["pnl_inr"])

def _sym(ccy): return {"INR":"₹","USD":"$","EUR":"€","AED":"د.إ"}.get(str(ccy).upper(),"")
def fmt_native(v, ccy):
    try: return f"{_sym(ccy)}{float(v):,.1f}"
    except Exception: return ""
def fmt_inr(v):
    try: return f"₹{float(v):,.1f}"
    except Exception: return ""
def fmt_usd(v):
    try: return f"${float(v):,.1f}"
    except Exception: return ""

DISPLAY = ["move_arrow","portfolio","asset_class","sub_class","name","ticker","currency","quantity","invested_rate","live_rate","current_rate","invested_value","current_value","current_value_inr","usd_equivalent","pnl_inr","pnl_pct","expected_return_pct","yield_dividend_pct","total_return_yield_inr","price_status","data_source"]

def display_table(data, cols=None, total=True):
    cols = cols or DISPLAY
    show = data[[c for c in cols if c in data.columns]].copy()
    if total and not show.empty:
        row = {c:"" for c in show.columns}
        row["name"] = "TOTAL"
        row["move_arrow"] = "🟢 ▲" if data["pnl_inr"].sum() >= 0 else "🔴 ▼"
        row["currency"] = "INR"
        for c in ["invested_value","current_value","current_value_inr","pnl_inr","total_return_yield_inr"]:
            if c in row: row[c] = data[c].sum()
        show = pd.concat([show, pd.DataFrame([row])], ignore_index=True)
    for c in ["invested_rate","live_rate","current_rate","invested_value","current_value"]:
        if c in show.columns and "currency" in show.columns:
            show[c] = [fmt_native(v, cc) for v, cc in zip(show[c], show["currency"])]
    for c in ["current_value_inr","pnl_inr","total_return_yield_inr"]:
        if c in show.columns: show[c] = show[c].apply(fmt_inr)
    if "usd_equivalent" in show.columns: show["usd_equivalent"] = show["usd_equivalent"].apply(lambda x: "" if pd.isna(x) else fmt_usd(x))
    for c in ["pnl_pct","expected_return_pct","yield_dividend_pct"]:
        if c in show.columns: show[c] = show[c].apply(fmt_pct)
    if "quantity" in show.columns:
        show["quantity"] = show["quantity"].apply(lambda x: f"{float(x):,.4f}" if str(x) != "" else "")
    rename = {"move_arrow":"P/L","portfolio":"Portfolio","asset_class":"Asset","sub_class":"Type","name":"Holding","ticker":"Ticker","currency":"Ccy","quantity":"Qty","invested_rate":"Avg Cost","live_rate":"Live","current_rate":"Current Rate","invested_value":"Invested","current_value":"Current Native","current_value_inr":"Current INR","usd_equivalent":"USD Eq.","pnl_inr":"P/L INR","pnl_pct":"P/L %","expected_return_pct":"Return %","yield_dividend_pct":"Yield/Div %","total_return_yield_inr":"Return+Yield INR","price_status":"Price","data_source":"Source"}
    return show.rename(columns={k:v for k,v in rename.items() if k in show.columns})

def table(title, data):
    st.subheader(title)
    st.dataframe(display_table(data), use_container_width=True, hide_index=True, height=470)

st.sidebar.title("◆ Family Office")
page = st.sidebar.radio("Navigation", ["Dashboard","Indian Portfolio","US Portfolio","Returns & Yield","Consolidated Portfolio","Holding Intelligence","Net Worth Growth","Admin / Edit Holdings"])
st.sidebar.divider()
st.sidebar.metric("Current Net Worth", fmt_inr(T["current_value_inr"]))
st.sidebar.metric("Invested / Base", fmt_inr(T["invested_value_inr"]))
st.sidebar.metric("P/L", fmt_inr(T["pnl_inr"]), f"{T['pnl_inr']/max(abs(T['invested_value_inr']),1):.1%}")
st.sidebar.caption("USD/INR base: ₹94.44")

if page == "Dashboard":
    st.title("Harsh Global Portfolio - Family Office")
    st.caption("Cost basis separated from live current value · USD/INR ₹94.44 · no manual toggles")
    mood = "Bullish" if T["pnl_inr"] >= 0 else "Bearish"
    st.markdown(f"<div class='tape'><span>🐂 NIFTY · S&P 500 · NASDAQ · DOW · GOLD · BRENT · USD/INR ₹94.44 · AMFI NAV · PORTFOLIO MOOD: {mood} 🐻</span></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f"<div class='card'><div class='metric-title'>Current Net Worth</div><div class='metric-value'>{fmt_inr(T['current_value_inr'])}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><div class='metric-title'>Invested / Base</div><div class='metric-value'>{fmt_inr(T['invested_value_inr'])}</div></div>", unsafe_allow_html=True)
    cls = "good" if T["pnl_inr"] >= 0 else "bad"
    c3.markdown(f"<div class='card'><div class='metric-title'>Unrealized P/L</div><div class='metric-value {cls}'>{arrow(T['pnl_inr'])} {fmt_inr(T['pnl_inr'])}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><div class='metric-title'>Return + Yield</div><div class='metric-value'>{fmt_inr(T['total_return_yield_inr'])}</div></div>", unsafe_allow_html=True)
    left,right = st.columns([1.05,1])
    with left:
        fig = px.pie(df.groupby("asset_class", as_index=False)["current_value_inr"].sum(), names="asset_class", values="current_value_inr", hole=.55, title="Current Allocation")
        fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        md = get_market_dashboard(fx)
        for col in ["Last","52W High","52W Low","Volume"]:
            if col in md: md[col] = md[col].apply(lambda x: "" if pd.isna(x) else f"{float(x):,.1f}")
        if "Day %" in md: md["Day %"] = md["Day %"].apply(lambda x: "" if pd.isna(x) else f"{float(x)*100:.1f}%")
        st.subheader("Market Watch")
        st.dataframe(md, use_container_width=True, height=430, hide_index=True)
    table("Top Holdings", df.sort_values("current_value_inr", ascending=False).head(15))

elif page == "Indian Portfolio":
    st.title("Indian Portfolio")
    ind = df[df["portfolio"].eq("INDIA")]
    for label, filt in [("All",None),("Equity","Equity"),("Mutual Funds","Mutual Fund"),("Fixed Income","Fixed Income"),("Gold","Gold"),("Real Estate","Real Estate"),("Cash","Cash")]:
        with st.expander(label, expanded=(label=="All")):
            table(label, ind if filt is None else ind[ind["asset_class"].eq(filt)])

elif page == "US Portfolio":
    st.title("US / Global Portfolio")
    us = df[df["portfolio"].eq("US/GLOBAL")]
    for label, filt in [("All",None),("Equity","Equity"),("ETF","ETF"),("Fixed Income","Fixed Income"),("Cash","Cash"),("Mixed Asset","Mixed Asset"),("Real Estate","Real Estate"),("Liability","Liability")]:
        with st.expander(label, expanded=(label=="All")):
            table(label, us if filt is None else us[us["asset_class"].eq(filt)])

elif page == "Returns & Yield":
    st.title("Returns & Yield")
    cols = ["portfolio","asset_class","name","current_value_inr","expected_return_pct","expected_return_amount_inr","yield_dividend_pct","yield_dividend_amount_inr","total_return_yield_inr"]
    ret = df[cols].copy()
    for c in ["current_value_inr","expected_return_amount_inr","yield_dividend_amount_inr","total_return_yield_inr"]:
        ret[c] = ret[c].apply(fmt_inr)
    for c in ["expected_return_pct","yield_dividend_pct"]:
        ret[c] = ret[c].apply(fmt_pct)
    total_row = {
        "portfolio": "TOTAL",
        "asset_class": "",
        "name": "Portfolio Total",
        "current_value_inr": fmt_inr(df["current_value_inr"].sum()),
        "expected_return_pct": "",
        "expected_return_amount_inr": fmt_inr(df["expected_return_amount_inr"].sum()),
        "yield_dividend_pct": "",
        "yield_dividend_amount_inr": fmt_inr(df["yield_dividend_amount_inr"].sum()),
        "total_return_yield_inr": fmt_inr(df["total_return_yield_inr"].sum()),
    }
    ret = pd.concat([ret, pd.DataFrame([total_row])], ignore_index=True)
    st.dataframe(ret.rename(columns={"portfolio":"Portfolio","asset_class":"Asset","name":"Holding","current_value_inr":"Current INR","expected_return_pct":"Return %","expected_return_amount_inr":"Return ₹","yield_dividend_pct":"Yield/Div %","yield_dividend_amount_inr":"Yield/Div ₹","total_return_yield_inr":"Total ₹"}), use_container_width=True, hide_index=True, height=650)
    c1, c2, c3 = st.columns(3)
    c1.metric("Expected Return Total", fmt_inr(df["expected_return_amount_inr"].sum()))
    c2.metric("Dividend / Yield Total", fmt_inr(df["yield_dividend_amount_inr"].sum()))
    c3.metric("Return + Yield Total", fmt_inr(df["total_return_yield_inr"].sum()))

elif page == "Consolidated Portfolio":
    st.title("Consolidated Portfolio")
    table("All Holdings", df)
    st.subheader("Currency Exposure")
    ccy = df.groupby("currency", as_index=False).agg(Native=("current_value","sum"), INR=("current_value_inr","sum"))
    ccy["Native"] = [fmt_native(v,c) for v,c in zip(ccy["Native"], ccy["currency"])]
    ccy["INR"] = ccy["INR"].apply(fmt_inr)
    st.dataframe(ccy.rename(columns={"currency":"Currency"}), use_container_width=True, hide_index=True)

elif page == "Holding Intelligence":
    st.title("Holding Intelligence")
    choices = df[df["ticker"].astype(str).str.len().gt(0)][["name","ticker"]].drop_duplicates()
    label = st.selectbox("Select holding", choices.apply(lambda r: f"{r['name']} · {r['ticker']}", axis=1))
    ticker = label.split("·")[-1].strip()
    price, meta = safe_price(ticker)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Current", "" if price is None else f"{price:,.2f}")
    c2.metric("52W High", "" if not meta.get("52w_high") else f"{meta['52w_high']:,.1f}")
    c3.metric("52W Low", "" if not meta.get("52w_low") else f"{meta['52w_low']:,.1f}")
    c4.metric("Volume", "" if not meta.get("volume") else f"{meta['volume']:,.0f}")
    hist = get_history(ticker, "2y")
    if not hist.empty:
        fig = go.Figure(data=[go.Candlestick(x=hist["Date"], open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"])])
        fig.update_layout(height=480, xaxis_rangeslider_visible=False, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    news = get_news(ticker)
    for n in news:
        st.markdown(f"<div class='news-card'><b>{n.get('title','')}</b><br><span class='small-muted'>{n.get('publisher','')}</span><br><a href='{n.get('link','#')}' target='_blank'>Open</a></div>", unsafe_allow_html=True)

elif page == "Net Worth Growth":
    st.title("Net Worth Growth")
    snaps = get_snapshots()
    if not snaps.empty:
        fig = px.line(snaps, x="snapshot_date", y="net_worth_inr", markers=True, title="Daily Net Worth")
        fig.update_traces(hovertemplate="Date: %{x}<br>Net Worth: ₹%{y:,.1f}<extra></extra>")
        fig.update_layout(height=500, yaxis_tickprefix="₹", yaxis_tickformat=",.1f", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        snap_show = snaps.copy()
        for c in ["net_worth_inr","invested_value_inr","current_value_inr","pnl_inr"]:
            if c in snap_show.columns:
                snap_show[c] = snap_show[c].apply(fmt_inr)
        st.dataframe(snap_show, use_container_width=True, hide_index=True)
    else:
        st.info("Snapshots begin after first run.")

elif page == "Admin / Edit Holdings":
    st.title("Admin / Edit Holdings")
    st.warning("Cost basis = quantity × invested_rate. Current value = quantity × live/fallback current_rate. Do not overwrite cost with live price.")
    edited = st.data_editor(get_holdings(active_only=False), num_rows="dynamic", use_container_width=True, height=650)
    c1,c2 = st.columns([1,3])
    if c1.button("Save Changes", type="primary"):
        save_holdings(edited)
        st.cache_data.clear()
        st.success("Saved")
        st.rerun()
    if c2.button("Reset to Corrected Seed Data"):
        init_db(force=True)
        st.cache_data.clear()
        st.success("Reset")
        st.rerun()
