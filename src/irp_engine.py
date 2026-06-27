"""
irp_engine.py
=============
Core IRP ceiling propagation engine.

Takes the EU market graph from markets.py and a launch sequence,
then walks the sequence left to right propagating price ceilings
through the reference network in real time.

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

from typing import Dict, List, Optional, Tuple
from src.markets import Market

class IRPCascadeEngine:
    """
    Propagates IRP price ceilings through the EU reference network
    given a launch sequence and entry prices.
    """

    def __init__(self, markets: Dict[str, Market]):
        self.markets = markets

    def compute_net_prices(
        self,
        sequence: List[str],
        entry_prices: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Walk the launch sequence and compute the IRP-constrained
        net price for each market.

        Returns:
            net_prices      : EUR net price per market
            constraints_hit : markets where IRP ceiling was binding
        """
        launched_prices: Dict[str, float] = {}
        net_prices: Dict[str, float] = {}
        constraints_hit: List[str] = []

        for mkt_code in sequence:
            mkt = self.markets[mkt_code]
            desired_price_eur = entry_prices.get(
                mkt_code, entry_prices.get("default", 100.0)
            )

            irp_ceiling = self._compute_irp_ceiling(
                mkt_code, launched_prices, mkt
            )

            if irp_ceiling is not None and irp_ceiling < desired_price_eur:
                net_price = irp_ceiling
                constraints_hit.append(mkt_code)
            else:
                net_price = desired_price_eur

            net_price_after_rebate = net_price * (1 - mkt.mandatory_rebate)

            net_prices[mkt_code] = round(net_price_after_rebate, 4)
            launched_prices[mkt_code] = net_price

        return net_prices, constraints_hit

    def _compute_irp_ceiling(
        self,
        mkt_code: str,
        launched_prices: Dict[str, float],
        mkt: Market
    ) -> Optional[float]:
        """
        Compute the IRP price ceiling for a single market.
        Returns None if no ceiling applies.
        """
        if not mkt.references:
            return None

        available_refs = [
            launched_prices[ref]
            for ref in mkt.references
            if ref in launched_prices
        ]

        if not available_refs:
            return None

        basket_price = min(available_refs)
        return basket_price * (1 - mkt.reference_discount)

    def compute_revenue(
        self,
        net_prices: Dict[str, float],
        access_days: Dict[str, int]
    ) -> float:
        """
        Compute 3-year cumulative revenue across all launched markets.
        """
        total = 0.0
        for mkt_code, net_price in net_prices.items():
            mkt = self.markets[mkt_code]
            days = access_days.get(mkt_code, mkt.avg_access_days)
            yr1_fraction = max(0, (365 - days) / 365)
            # FIXED: attribute spelling corrected to iqvia_volume_units
            revenue = net_price * mkt.iqvia_volume_units * (yr1_fraction + 1.0 + 1.1)
            total += revenue
        return round(total, 0)


if __name__ == "__main__":
    from src.markets import build_eu_market_graph

    markets = build_eu_market_graph()
    engine = IRPCascadeEngine(markets)

    sequence = ["CH", "DE", "FR", "IT"]
    entry_prices = {m: 100.0 for m in sequence}

    net_prices, constraints = engine.compute_net_prices(sequence, entry_prices)

    print("Launch sequence:", " -> ".join(sequence))
    print()
    print(f"{'Market':<10} {'Net Price EUR':<20} {'Constrained'}")
    print("-" * 45)
    for mkt in sequence:
        constrained = "YES - IRP ceiling hit" if mkt in constraints else "No"
        print(f"{mkt:<10} {net_prices[mkt]:<20} {constrained}")

    print()
    access_days = {m: markets[m].avg_access_days for m in sequence}
    revenue = engine.compute_revenue(net_prices, access_days)
    print(f"3-year revenue: EUR {revenue:,.0f}")
