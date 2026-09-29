---
name: agenthon-master
description: Master skill for Agenthon 2026 project overview and strategy. Consolidates all planning and execution.
---

# Agenthon 2026 Master Strategy

You are acting as an AI assistant to build winning solutions for the NeurIPS 2026 Agenthon competition.
The competition involves "Verifiable AI for Quantitative Finance".

## Active Tracks
We are participating in:
- **T1: Coding** - Quantitative Finance Coding Agents evaluated via pytest and financial-invariant checks. (Metric: pass@1)
- **T3: Simulation** - Accelerated Market Simulation, optimizing ABIDES discrete event simulator. (Metric: events/sec)

## Global Constraints & Rules
- Do NOT focus on the paper submission. The user has explicitly stated that we are skipping the paper to rigorously focus on the technical implementation of T1 and T3.
- Write highly optimized, low-latency code for T3.
- Write robust, multi-agent retry loops for T1.

## Related Skills
- `agenthon-t1-coder`: Instructions and architecture for the T1 Coding track.
- `agenthon-t3-simulator`: Instructions and architecture for the T3 Simulation track.

Use these skills whenever working on their respective tracks.
