from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from src.ppt_builder import generate_strike_price_deck
from src.reporting import generate_company_report_html
from src.valuation import Fundamentals, compute_valuation
from src.watchlist_db import fetch_latest_snapshots, get_conn, init_db, upsert_valuation_snapshot

PRICE_PROVIDER = {
    "AMZN": 188.0,
    "MSFT": 410.0,
}

FUNDAMENTALS_CSV = Path("data/fundamentals_latest.csv")
DASHBOARD_HTML = Path("reports/watchlist_dashboard.html")


def get_price(ticker: str) -> float:
    return PRICE_PROVIDER[ticker]


def load_fundamentals() -> Dict[str, Fundamentals]:
    fundamentals = {}
    with FUNDAMENTALS_CSV.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            fundamentals[row["ticker"]] = Fundamentals(
                ticker=row["ticker"],
                eps=float(row["eps"]),
                growth_rate=float(row["growth_rate"]),
                pe_multiple=float(row["pe_multiple"]),
                years=int(row.get("years", 5)),
            )
    return fundamentals


def _row_html(row: dict) -> str:
    ticker = row["ticker"]
    return (
        "<tr>"
        f"<td>{ticker}</td>"
        f"<td>${row['price']:.2f}</td>"
        f"<td>${row['intrinsic_base']:.2f}</td>"
        f"<td>${row['strike_mos_25']:.2f}</td>"
        f"<td>${row['strike_mos_15']:.2f}</td>"
        f"<td>${row['strike_mos_10']:.2f}</td>"
        f"<td>{row['pct_to_mos25'] * 100:.2f}%</td>"
        f"<td><span class='status-pill {row['status']}'>{row['status']}</span></td>"
        f"<td><a href='{ticker}_report.html'>Open</a></td>"
        f"<td><a href='{ticker}_report.html'>Regenerate</a></td>"
        f"<td><a href='../decks/{ticker}_deck.pptx'>Regenerate</a></td>"
        "</tr>"
    )


def render_dashboard(rows: List[dict], output: Path = DASHBOARD_HTML) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    table_rows = "\n".join(_row_html(row) for row in rows)
    html = f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <title>Watchlist Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; }}
    th {{ background: #f6f7fb; text-align: left; }}
    .status-pill {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
    .FAT\ PITCH {{ background: #d1fae5; color: #065f46; }}
    .BUY\ ZONE {{ background: #dbeafe; color: #1d4ed8; }}
    .WATCH {{ background: #fef3c7; color: #92400e; }}
    .FAIR {{ background: #e5e7eb; color: #374151; }}
    .EXPENSIVE {{ background: #fee2e2; color: #b91c1c; }}
  </style>
</head>
<body>
  <h1>Watchlist Dashboard</h1>
  <table>
    <thead>
      <tr>
        <th>Ticker</th><th>Price</th><th>Intrinsic (Base)</th><th>MOS25</th><th>MOS15</th><th>MOS10</th>
        <th>% to MOS25</th><th>Status</th><th>Open Report</th><th>Regen Report</th><th>Regen Deck</th>
      </tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
</body>
</html>"""
    output.write_text(html, encoding="utf-8")
    return output


def refresh_watchlist(tickers: Iterable[str]) -> List[dict]:
    conn = get_conn()
    init_db(conn)

    fundamentals_map = load_fundamentals()
    as_of_date = date.today().isoformat()
    updated_at = datetime.now(timezone.utc).isoformat()

    snapshots: List[dict] = []
    for ticker in tickers:
        price = get_price(ticker)
        valuation = compute_valuation(price, fundamentals_map[ticker])
        snapshot = {
            "ticker": ticker,
            "as_of_date": as_of_date,
            "price": price,
            **valuation,
            "updated_at": updated_at,
        }
        upsert_valuation_snapshot(conn, snapshot)
        generate_company_report_html(snapshot)
        generate_strike_price_deck(snapshot)
        snapshots.append(snapshot)

    db_rows = [dict(row) for row in fetch_latest_snapshots(conn)]
    render_dashboard(db_rows)
    conn.close()
    return snapshots


if __name__ == "__main__":
    refresh_watchlist(["AMZN", "MSFT"])
    print(f"Dashboard generated at {DASHBOARD_HTML}")
