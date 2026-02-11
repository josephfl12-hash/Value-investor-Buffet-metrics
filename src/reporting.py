from __future__ import annotations

from pathlib import Path


def generate_company_report_html(snapshot: dict, output_dir: Path = Path("reports")) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{snapshot['ticker']}_report.html"

    current_price = snapshot["price"]
    intrinsic_base = snapshot["intrinsic_base"]
    relation = "below" if current_price <= intrinsic_base else "above"

    output_path.write_text(
        f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><title>{snapshot['ticker']} Report</title></head>
<body>
  <h1>{snapshot['ticker']} Company Report</h1>
  <section>
    <h2>Valuation</h2>
    <ul>
      <li>Intrinsic (Base): ${intrinsic_base:,.2f}</li>
      <li>MOS25 Strike: ${snapshot['strike_mos_25']:,.2f}</li>
      <li>MOS15 Strike: ${snapshot['strike_mos_15']:,.2f}</li>
      <li>MOS10 Strike: ${snapshot['strike_mos_10']:,.2f}</li>
      <li>Current Price: ${current_price:,.2f} ({relation} intrinsic base)</li>
    </ul>
  </section>
</body>
</html>
""",
        encoding="utf-8",
    )
    return output_path
