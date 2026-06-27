"""
markets.py
==========
EU market definitions and the International Reference Pricing (IRP) graph.

Every EU market has three pricing-relevant properties:
    1. Which countries it references when setting a reimbursement ceiling
    2. How deep a discount it applies to those referenced prices
    3. What mandatory statutory rebates apply on top

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Market:
    name: str
    currency: str
    fx_to_eur: float
    iqvia_voume_units: int
    references: List[str]
    reference_discount: float
    mandatory_rebate: float
    avg_access_days: int

def build_eu_market_graph() -> Dict[str, Market]:
    return {
        "DE": Market("Germany",     "EUR", 1.00, 800_000, [],                0.00, 0.07,  90),
        "FR": Market("France",      "EUR", 1.00, 700_000, ["DE"],            0.05, 0.05, 180),
        "IT": Market("Italy",       "EUR", 1.00, 600_000, ["DE", "FR"],      0.05, 0.05, 270),
        "ES": Market("Spain",       "EUR", 1.00, 500_000, ["DE", "FR"],      0.10, 0.075,270),
        "UK": Market("UK",          "GBP", 0.87, 650_000, ["DE"],            0.05, 0.00, 180),
        "CH": Market("Switzerland", "CHF", 0.98, 150_000, [],                0.00, 0.00,  45),
        "AT": Market("Austria",     "EUR", 1.00, 120_000, ["DE"],            0.00, 0.05, 120),
        "BE": Market("Belgium",     "EUR", 1.00, 130_000, ["DE", "FR"],      0.05, 0.00, 180),
        "NL": Market("Netherlands", "EUR", 1.00, 200_000, ["DE", "BE"],      0.05, 0.00, 240),
        "SE": Market("Sweden",      "SEK", 0.088,180_000, ["DE", "UK"],      0.05, 0.00, 180),
        "PL": Market("Poland",      "PLN", 0.23, 300_000, ["DE", "FR","ES"], 0.15, 0.00, 365),
        "RO": Market("Romania",     "RON", 0.20, 150_000, ["PL", "ES"],      0.20, 0.00, 365),
    }
if __name__ == "__main__":
    markets = build_eu_market_graph()
    print(f"Total markets loaded: {len(markets)}")
    print()
    for code, market in markets.items():
        print(f"{code} | {market.name} | Currency: {market.currency} | "
              f"References: {market.references} | "
              f"Rebate: {market.mandatory_rebate*100:.0f}% | "
              f"Access days: {market.avg_access_days}")
        
        