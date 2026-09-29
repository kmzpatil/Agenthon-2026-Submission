---
name: agenthon-t3-simulator
description: Architecture and optimization strategies for the T3 Accelerated Market Simulation track.
---

# T3: Accelerated Market Simulation

## Objective
Submit an ABIDES-compatible simulator that maximizes `events/sec` while strictly preserving financial semantics and ABIDES API compatibility.

## The Bottleneck
ABIDES is a Python-based Discrete Event Simulator (DES). It scales poorly due to the Global Interpreter Lock (GIL) and event loop overhead.

## Selected Pathway: C++ Pybind11 Integration
We will leverage the existing *Multithreaded Order Book* project to rewrite the core matching engine in C++.

### Implementation Details
1. **C++ Core:** Rewrite `ABIDES-Core` (priority queue) and `ExchangeAgent` (limit order book) in C++.
2. **"Share-Nothing, Lock-Nothing":** Pin the engine to a single core and avoid `std::mutex`.
3. **Zero-Allocation:** Ban dynamic allocation (`new`, `malloc`) on the hot path. Use pre-allocated `std::vector` pools.
4. **O(1) Data Structures:** Use flat arrays or custom intrusive linked lists to manage price levels instead of $O(\log n)$ maps.
5. **Lock-Free SPSC Queues:** Use Single-Producer Single-Consumer ring buffers for C++ <-> Python communication.
6. **Pybind11 Bridge:** Expose the C++ engine to Python. Use `py::gil_scoped_release` to prevent Python from blocking the C++ threads.

## Alternative/Complementary Pathway
- **Event Batching:** Batch independent messages (e.g., limit orders on different tickers) and process them concurrently.
