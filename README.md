# IRP Cascade Simulator

**EU International Reference Pricing — Launch Sequence Optimizer**

---

## The Problem

When a pharma company sets a drug price in Germany, France is legally 
required to use that price as its ceiling. Italy references Germany AND 
France and takes the lowest one. Spain does the same. One pricing 
decision in one country cascades into 12 countries automatically.

This is called International Reference Pricing — IRP.

Getting the launch sequence wrong can destroy $10-15M in margin before 
a single patient is treated.

---

## What This Simulator Does

- Maps the EU reference network — who references whom and at what discount
- Takes your launch sequence and propagates price ceilings in real time
- Runs 500 Monte Carlo simulations to find the most robust sequence
- Ranks every sequence by 3-year revenue with P10/P90 uncertainty range
- Exports scenario comparison, ranked sequences, and price sensitivity table

---

## Real-World Proof Point

A re-sequencing of Switzerland first then Germany protected $10-15M in 
cross-market margin by anchoring price in a non-IRP market before 
triggering the cascade. This simulator replicates that exact decision.

---

## Project Structure

irp-cascade-simulator/

├── src/

│   ├── markets.py        # EU market definitions and reference graph

│   ├── irp_engine.py     # Core IRP ceiling propagation logic

│   ├── optimizer.py      # Monte Carlo launch sequence optimizer

│   └── analysis.py       # Deterministic scenarios and sensitivity

├── tests/

│   └── test_irp_engine.py

├── outputs/

├── main.py

└── requirements.txt

---

## Quick Start

```bash
git clone https://github.com/sannapa2016/irp-cascade-simulator.git
cd irp-cascade-simulator
pip install -r requirements.txt
python main.py
```

---

## Tech Stack

- Python 3.9+
- NumPy — Monte Carlo simulation and lognormal price sampling
- Pandas — scenario output tables

---

## Author

**Siva Annapareddy**
Founder and AVP, Amrak Pharma
18 years in pharma commercial analytics

*Part of a 36-project public pharma analytics portfolio*
