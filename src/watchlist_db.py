from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path("data/watchlist.db")


def get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS valuation_snapshot (
            ticker TEXT NOT NULL,
            as_of_date TEXT NOT NULL,
            price REAL,
            intrinsic_conservative REAL,
            intrinsic_base REAL,
            intrinsic_optimistic REAL,
            strike_mos_25 REAL,
            strike_mos_15 REAL,
            strike_mos_10 REAL,
            pct_to_mos25 REAL,
            usd_to_mos25 REAL,
            status TEXT,
            updated_at TEXT,
            PRIMARY KEY (ticker, as_of_date)
        )
        """
    )
    conn.commit()


def upsert_valuation_snapshot(conn: sqlite3.Connection, snapshot: dict) -> None:
    conn.execute(
        """
        INSERT INTO valuation_snapshot (
            ticker,
            as_of_date,
            price,
            intrinsic_conservative,
            intrinsic_base,
            intrinsic_optimistic,
            strike_mos_25,
            strike_mos_15,
            strike_mos_10,
            pct_to_mos25,
            usd_to_mos25,
            status,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker, as_of_date) DO UPDATE SET
            price=excluded.price,
            intrinsic_conservative=excluded.intrinsic_conservative,
            intrinsic_base=excluded.intrinsic_base,
            intrinsic_optimistic=excluded.intrinsic_optimistic,
            strike_mos_25=excluded.strike_mos_25,
            strike_mos_15=excluded.strike_mos_15,
            strike_mos_10=excluded.strike_mos_10,
            pct_to_mos25=excluded.pct_to_mos25,
            usd_to_mos25=excluded.usd_to_mos25,
            status=excluded.status,
            updated_at=excluded.updated_at
        """,
        (
            snapshot["ticker"],
            snapshot["as_of_date"],
            snapshot["price"],
            snapshot["intrinsic_conservative"],
            snapshot["intrinsic_base"],
            snapshot["intrinsic_optimistic"],
            snapshot["strike_mos_25"],
            snapshot["strike_mos_15"],
            snapshot["strike_mos_10"],
            snapshot["pct_to_mos25"],
            snapshot["usd_to_mos25"],
            snapshot["status"],
            snapshot["updated_at"],
        ),
    )
    conn.commit()


def fetch_latest_snapshots(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute(
        """
        SELECT v.*
        FROM valuation_snapshot v
        INNER JOIN (
            SELECT ticker, MAX(as_of_date) AS max_date
            FROM valuation_snapshot
            GROUP BY ticker
        ) latest ON latest.ticker = v.ticker AND latest.max_date = v.as_of_date
        ORDER BY v.ticker
        """
    ).fetchall()
