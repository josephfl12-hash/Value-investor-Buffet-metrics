from __future__ import annotations

from pathlib import Path


def generate_strike_price_deck(snapshot: dict, output_dir: Path = Path("decks")) -> Path:
    """Generate a lightweight deck artifact with a Strike Price Matrix slide payload."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{snapshot['ticker']}_deck.pptx"

    rows = [
        ("Conservative", snapshot["intrinsic_conservative"]),
        ("Base", snapshot["intrinsic_base"]),
        ("Optimistic", snapshot["intrinsic_optimistic"]),
    ]

    lines = [
        f"{snapshot['ticker']} Strike Price Matrix",
        "Case | Intrinsic | MOS25 | MOS15 | MOS10",
        "---|---:|---:|---:|---:",
    ]

    for case, intrinsic in rows:
        lines.append(
            f"{case} | ${intrinsic:,.2f} | ${intrinsic * 0.75:,.2f} | ${intrinsic * 0.85:,.2f} | ${intrinsic * 0.90:,.2f}"
        )

    lines.append("")
    lines.append(f"Current price: ${snapshot['price']:,.2f} | Status: {snapshot['status']}")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
