from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Fundamentals:
    ticker: str
    eps: float
    growth_rate: float
    pe_multiple: float
    years: int = 5


def _status_from_price(
    price: float,
    strike_mos_25: float,
    strike_mos_15: float,
    strike_mos_10: float,
    intrinsic_base: float,
) -> str:
    if price <= strike_mos_25:
        return "FAT PITCH"
    if price <= strike_mos_15:
        return "BUY ZONE"
    if price <= strike_mos_10:
        return "WATCH"
    if price <= intrinsic_base:
        return "FAIR"
    return "EXPENSIVE"


def compute_valuation(price: float, fundamentals: Fundamentals) -> Dict[str, float | str]:
    """Compute intrinsic values, strike prices, and watchlist status."""
    base_terminal_eps = fundamentals.eps * ((1 + fundamentals.growth_rate) ** fundamentals.years)
    intrinsic_base = base_terminal_eps * fundamentals.pe_multiple
    intrinsic_conservative = intrinsic_base * 0.85
    intrinsic_optimistic = intrinsic_base * 1.15

    strike_mos_25 = intrinsic_base * 0.75
    strike_mos_15 = intrinsic_base * 0.85
    strike_mos_10 = intrinsic_base * 0.90

    pct_to_mos25 = (price / strike_mos_25) - 1 if strike_mos_25 else 0.0
    usd_to_mos25 = price - strike_mos_25

    status = _status_from_price(
        price,
        strike_mos_25=strike_mos_25,
        strike_mos_15=strike_mos_15,
        strike_mos_10=strike_mos_10,
        intrinsic_base=intrinsic_base,
    )

    return {
        "intrinsic_conservative": intrinsic_conservative,
        "intrinsic_base": intrinsic_base,
        "intrinsic_optimistic": intrinsic_optimistic,
        "strike_mos_25": strike_mos_25,
        "strike_mos_15": strike_mos_15,
        "strike_mos_10": strike_mos_10,
        "pct_to_mos25": pct_to_mos25,
        "usd_to_mos25": usd_to_mos25,
        "status": status,
    }
