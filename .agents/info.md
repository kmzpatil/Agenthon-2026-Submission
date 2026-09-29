# Agenthon 2026: Verifiable AI for Quantitative Finance

A four-track competition testing whether AI agents can produce finance outputs that survive automated, leakage-controlled, cheat-resistant evaluation. The competition closes with a workshop at NeurIPS 2026 in Atlanta, Georgia.

## Key Dates
- **Aug 28 – Oct 12:** Registration & Development phase (closes at 23:59 AoE).
- **Sep 30:** Paper submissions deadline (23:59 AoE).
- **Oct 13 – Oct 25:** Final + Verification phase. One submission per entered track evaluated on sealed held-out units.
- **Dec 12:** NeurIPS Workshop in Atlanta for final presentations.

## Protocol
1. **Submit:** Upload toolkit-generated ZIP. Agents run in Docker containers (no internet, but House Nemotron allowed for T1, T2, T4; T3 has no network).
2. **Check:** g0-g3 gates verify integrity, schema, resource rules, and domain semantics.
3. **Score:** Track-specific scoring.

## Tracks
* **T1: Coding (Quant-finance coding agents)**
  * **Objective:** Build a Docker agent that solves quantitative finance coding tasks.
  * **Gate:** `pytest` + financial invariants.
  * **Metric:** `pass@1` (No confidence interval).
  * **Lead:** Zhikang Dong.

* **T2: Forecasting (Reasoning-augmented time series)**
  * **Objective:** Forecast future panels using time-series and text.
  * **Gate:** as-of cutoff + calibration.
  * **Metric:** CRPS composite.
  * **Lead:** Ruolan Sun.

* **T3: Simulation (Accelerated market simulation)**
  * **Objective:** Submit an ABIDES-compatible simulator that is faster while preserving semantics.
  * **Gate:** semantic regression.
  * **Metric:** `events/sec`.
  * **Lead:** Haohan Xu.

* **T4: Explainability (Evidence-grounded prediction)**
  * **Objective:** Predict values supported by a frozen evidence corpus.
  * **Gate:** faithfulness + embargo.
  * **Metric:** Track 4 composite.
  * **Lead:** Mathew Thiel.

## Awards
Total $12,000 cash prizes:
- 1st Place: $1,500 per track
- 2nd Place: $1,000 per track
- 3rd Place: $500 per track

## Organizing Committee
- **Lead Organizers:** Pawel Polak (Stony Brook, SQA), Christos Koutsoyannis (Atlas Ridge Capital)
- **Industry Co-Organizers:** David Rosenberg & Gary Kazantsev (Bloomberg), Ioana Boier (NVIDIA)
- **Sponsors:** NVIDIA, Bloomberg, AllianceBernstein, Nebius
