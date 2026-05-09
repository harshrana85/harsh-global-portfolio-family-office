
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
from portfolio_seed import HOLDINGS, COLUMNS, DEFAULT_FX

DB_PATH = Path(__file__).with_name("portfolio.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    sub_class TEXT,
    name TEXT NOT NULL,
    ticker TEXT,
    currency TEXT NOT NULL,
    quantity REAL NOT NULL,
    invested_rate REAL NOT NULL,
    fallback_current_rate REAL NOT NULL,
    expected_return_pct REAL DEFAULT 0,
    yield_dividend_pct REAL DEFAULT 0,
    data_source TEXT,
    pricing_mode TEXT DEFAULT 'live',
    show_usd_equivalent INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_date TEXT PRIMARY KEY,
    net_worth_inr REAL NOT NULL,
    invested_value_inr REAL NOT NULL,
    current_value_inr REAL NOT NULL,
    pnl_inr REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db(force: bool = False):
    # Always reseed if schema/content version changed or force requested.
    # This avoids stale Streamlit Cloud DB causing old totals.
    if force and DB_PATH.exists():
        DB_PATH.unlink()
    con = connect()
    con.executescript(SCHEMA)
    cur = con.execute("PRAGMA table_info(holdings)")
    cols = [r[1] for r in cur.fetchall()]
    required = set(COLUMNS + ["active"])
    if not required.issubset(set(cols)):
        con.execute("DROP TABLE IF EXISTS holdings")
        con.executescript(SCHEMA)
    cur = con.execute("SELECT COUNT(*) FROM holdings")
    count = cur.fetchone()[0]
    # Reseed every deployment if the source file has newer corrected accounting.
    if count == 0 or force:
        con.execute("DELETE FROM holdings")
        df = pd.DataFrame(HOLDINGS, columns=COLUMNS)
        df["active"] = 1
        df.to_sql("holdings", con, if_exists="append", index=False)
    con.commit()
    con.close()

def get_holdings(active_only=True) -> pd.DataFrame:
    init_db()
    q = "SELECT * FROM holdings"
    if active_only:
        q += " WHERE active=1"
    q += " ORDER BY portfolio, asset_class, name"
    with connect() as con:
        return pd.read_sql_query(q, con)

def save_holdings(df: pd.DataFrame):
    init_db()
    keep_cols = ["id"] + COLUMNS + ["active"]
    df = df[[c for c in keep_cols if c in df.columns]].copy()
    with connect() as con:
        con.execute("DELETE FROM holdings")
        df.to_sql("holdings", con, if_exists="append", index=False)
        con.commit()

def add_snapshot(net_worth_inr: float, invested_value_inr: float, current_value_inr: float, pnl_inr: float):
    init_db()
    with connect() as con:
        con.execute(
            "INSERT OR REPLACE INTO snapshots(snapshot_date, net_worth_inr, invested_value_inr, current_value_inr, pnl_inr) VALUES (date('now'), ?, ?, ?, ?)",
            (float(net_worth_inr), float(invested_value_inr), float(current_value_inr), float(pnl_inr))
        )
        con.commit()

def get_snapshots() -> pd.DataFrame:
    init_db()
    with connect() as con:
        return pd.read_sql_query("SELECT * FROM snapshots ORDER BY snapshot_date", con)
