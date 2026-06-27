"""
main.py
=======
Single entry point for the IRP Cascade Simulator.

Runs three analyses:
    1. Deterministic scenario comparison - which sequence wins
    2. Monte Carlo optimization - which sequence is most robust
    3. Price sensitivity sweep - where do constraints become binding

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

import os
import itertools
import numpy as np
import pandas as pd
from src.markets import build_eu_market_graph
from src.irp_engine import IRPCascadeEngine

os.makedirs("outputs", exist_ok=True)


def compare_scenarios(engine, markets, target_price=100.0):
    """
    ANALYSIS 1 - DETERMINISTIC SCENARIO COMPARISON
    Compares named launch sequences at a fixed price.
    Used for board presentations - single traceable number per scenario.
    """
    scenarios = {
        "CH-first (original)": ["CH", "DE", "FR", "IT", "ES", "UK"],
        "DE-first (recommended)": ["DE", "FR", "IT", "ES", "UK", "CH"],
        "FR-first": ["FR", "DE", "IT", "ES", "UK", "CH"],
        "UK-first": ["UK", "DE", "FR", "IT", "ES", "CH"],
    }

    rows = []
    for label, sequence in scenarios.items():
        entry_prices = {m: target_price for m in sequence}
        net_prices, constraints = engine.compute_net_prices(
            sequence, entry_prices
        )
        access_days = {m: markets[m].avg_access_days for m in sequence}
        revenue = engine.compute_revenue(net_prices, access_days)
        rows.append({
            "scenario": label,
            "first_market": sequence[0],
            "net_revenue_eur": revenue,
            "n_constraints": len(constraints),
            "constraints": ", ".join(constraints) if constraints else "None",
        })

    df = pd.DataFrame(rows).sort_values("net_revenue_eur", ascending=False)
    df["revenue_gap"] = df["net_revenue_eur"] - df["net_revenue_eur"].iloc[0]
    df["gap_pct"] = (df["revenue_gap"] / df["net_revenue_eur"].iloc[0] * 100).round(1)
    return df.reset_index(drop=True)


def monte_carlo(engine, markets, target_price=100.0, n_sim=500):
    """
    ANALYSIS 2 - MONTE CARLO OPTIMIZATION
    Tests 20 random sequences across 500 simulations each.
    Prices sampled from lognormal - stays positive, multiplicative.
    Output shows P10/P90 range - downside and upside scenarios.
    """
    candidate_markets = ["DE", "FR", "IT", "ES", "UK", "CH"]
    all_perms = list(itertools.permutations(candidate_markets))
    rng = np.random.default_rng(42)
    idxs = rng.choice(len(all_perms), 20, replace=False)
    sequences = [all_perms[i] for i in idxs]

    results = []
    for seq in sequences:
        rev_samples = []
        constraints_count = 0
        for _ in range(n_sim):
            entry_prices = {
                m: float(rng.lognormal(np.log(target_price), 0.05))
                for m in seq
            }
            access_days = {
                m: max(30, int(rng.normal(
                    markets[m].avg_access_days,
                    markets[m].avg_access_days * 0.20
                )))
                for m in seq
            }
            net_prices, constraints = engine.compute_net_prices(seq, entry_prices)
            rev = engine.compute_revenue(net_prices, access_days)
            rev_samples.append(rev)
            constraints_count += len(constraints)

        arr = np.array(rev_samples)
        results.append({
            "sequence": " -> ".join(seq),
            "first_market": seq[0],
            "mean_revenue": round(arr.mean(), 0),
            "p10_revenue": round(np.percentile(arr, 10), 0),
            "p90_revenue": round(np.percentile(arr, 90), 0),
            "avg_constraints": round(constraints_count / n_sim, 2),
            "cv_pct": round(arr.std() / arr.mean() * 100, 1),
        })

    df = pd.DataFrame(results).sort_values("mean_revenue", ascending=False)
    df["rank"] = range(1, len(df) + 1)
    df["vs_best_pct"] = (
        (df["mean_revenue"] / df["mean_revenue"].iloc[0]) - 1
    ).mul(100).round(1)
    return df.reset_index(drop=True)


def sensitivity(engine, markets):
    """
    ANALYSIS 3 - PRICE SENSITIVITY SWEEP
    Sweeps entry price from 70 to 130 for DE-first sequence.
    Shows where IRP constraints become binding.
    """
    sequence = ["DE", "FR", "IT", "ES", "UK", "CH"]
    rows = []
    for price in np.linspace(70, 130, 7):
        entry_prices = {m: price for m in sequence}
        net_prices, constraints = engine.compute_net_prices(
            sequence, entry_prices
        )
        access_days = {m: markets[m].avg_access_days for m in sequence}
        rev = engine.compute_revenue(net_prices, access_days)
        rows.append({
            "entry_price": round(price, 0),
            "DE_net": round(net_prices.get("DE", 0), 2),
            "FR_net": round(net_prices.get("FR", 0), 2),
            "IT_net": round(net_prices.get("IT", 0), 2),
            "CH_net": round(net_prices.get("CH", 0), 2),
            "constraints": len(constraints),
            "revenue": round(rev, 0),
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 65)
    print("IRP CASCADE SIMULATOR")
    print("Author: Siva Annapareddy | Amrak Pharma Analytics")
    print("=" * 65)

    markets = build_eu_market_graph()
    engine = IRPCascadeEngine(markets)

    print("\n[1] SCENARIO COMPARISON\n")
    det_df = compare_scenarios(engine, markets)
    print(det_df.to_string(index=False))
    gap = abs(det_df["revenue_gap"].iloc[-1])
    print(f"\n>>> Margin at risk: EUR {gap:,.0f}")
    print(f">>> Optimal first market: {det_df['first_market'].iloc[0]}")

    print("\n[2] MONTE CARLO OPTIMIZATION — Top 5 sequences\n")
    mc_df = monte_carlo(engine, markets)
    print(mc_df[[
        "rank", "sequence", "mean_revenue",
        "p10_revenue", "p90_revenue",
        "avg_constraints", "vs_best_pct"
    ]].head(5).to_string(index=False))

    print("\n[3] PRICE SENSITIVITY — DE-first sequence\n")
    sens_df = sensitivity(engine, markets)
    print(sens_df.to_string(index=False))

    det_df.to_csv("outputs/scenario_comparison.csv", index=False)
    mc_df.to_csv("outputs/monte_carlo_results.csv", index=False)
    sens_df.to_csv("outputs/sensitivity_table.csv", index=False)

    print("\n[OK] Results saved to outputs/")
    print("=" * 65)


if __name__ == "__main__":
    main()