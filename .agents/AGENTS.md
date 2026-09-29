# Agenthon 2026 AI Assistant Instructions

Welcome to the Agenthon 2026 repository. When working in this workspace, you must adhere to the following rules and utilize the specialized skills.

## Core Directives
1. **No Papers:** We are NOT submitting a paper. Do not write LaTeX or Markdown for publication. All effort goes into code and technical research.
2. **Tracks:** Focus strictly on `T1` (Coding) and `T3` (Simulation).

## Skills Directory
The `.agents/skills/` directory contains detailed architectural blueprints for the tracks:
- Use `agenthon-t1-coder` when writing the multi-agent code-generation system.
- Use `agenthon-t3-simulator` when writing the C++ ABIDES matching engine via Pybind11.
- Use `agenthon-master` for high-level strategy overview.

## Repository Setup
All raw research and scraping output is stored in `.agents/research/`.
All skills and rules for AI agents are defined here in the `.agents/` folder.

## Tools and Scrapers
- Use `github-scraper` for automated GitHub research.
- Use `web-scraper` for URL content extraction.

---

## Detailed Implementation Plan

### T1: Quant-Finance Coding Agent (Multi-Agent System)
**Goal:** Build a stateful, LangGraph-orchestrated system designed for high `pass@1` execution of quantitative finance tasks through a robust "Plan-Execute-Verify" cycle.

**Architecture & Execution Steps:**
1. **Environment & Sandbox Setup**: 
   - *How:* Scaffold a strict Python project. Configure an isolated, deterministic `venv` sandbox for the executor. Create a Dockerfile for reproducible deployment.
2. **Graph State Management**: 
   - *How:* Define a `TypedDict` Graph State that tracks `messages`, `generated_code`, `test_results`, `retry_count`, and `max_retries`. This provides the agent with persistent memory across iteration cycles.
3. **Planner/Research Node**: 
   - *How:* Implement an LLM node that ingests the Agenthon competition prompts, extracts the rigid mathematical invariants, and outputs a step-by-step logic plan (Chain-of-Thought) before writing code.
4. **Coder Node**: 
   - *How:* Implement an LLM node that reads the logic plan and generates the Python implementation (targeting House Nemotron or fallback models via API).
5. **Sandbox Executor Node (The Pytest Loop)**: 
   - *How:* Implement a sub-process execution node. It writes the generated code to the sandbox and runs a `pytest` suite against financial invariants (e.g., G0 gate). It captures the `stdout`/`stderr` tracebacks without crashing the agent.
6. **Review & Reflection Node (Logic Retries)**:
   - *How:* Evaluate the `pytest` output. If tests pass, route to `END`. If tests fail, increment `retry_count`. If `retry_count < max_retries`, attach the specific error traceback to the state and route back to the Coder Node for self-correction. If the budget is exhausted, terminate safely.

### T3: Accelerated Market Simulation (C++ Matching Engine)
**Goal:** Implement a "Dual-Loop Architecture" to achieve nanosecond-tier execution latency for the core Limit Order Book (LOB) while maintaining Python compatibility for the ABIDES orchestrator.

**Architecture & Execution Steps:**
1. **Fast Loop: C++17 Core Data Structures**:
   - *How:* Write a bare-metal C++ matching engine. Avoid all dynamic memory allocation (`malloc`/`new`) on the hot path by pre-allocating `std::vector` pools at startup. Implement the LOB using flat arrays for O(1) price-level lookups.
2. **Fast Loop: Hardware Sympathy & Matching Logic**:
   - *How:* Write single-threaded, lock-free strict price-time priority matching logic. Use thread-pinning (`pthread_setaffinity_np`) to bind the execution thread to a physical CPU core, completely bypassing the OS scheduler context switches.
3. **Lock-Free Memory Bridge (SPSC)**:
   - *How:* Bridge the C++ Fast Loop and the Python Slow Loop using a Zero-Copy Foreign Function Interface (FFI). Implement a Single-Producer Single-Consumer (SPSC) Ring Buffer. Use `std::atomic` with `memory_order_acquire` / `memory_order_release` and strict cache-line padding (`alignas(64)`) to prevent false sharing and cache invalidations.
4. **Slow Loop: Pybind11 Integration**:
   - *How:* Expose the SPSC queue and the C++ `OrderBook` to Python via `pybind11`. Critically, use `py::gil_scoped_release` to ensure the C++ execution does not block or wait on the Python Global Interpreter Lock (GIL).
5. **ABIDES Agent Wrapper**:
   - *How:* Wrap the Pybind11 engine in a standard `ExchangeAgent` class compatible with the `ABIDES-Core` event-driven priority queue, allowing unmodified Python trading agents to interact with the hyper-fast C++ LOB.
6. **Performance Profiling**:
   - *How:* Write a benchmarking suite comparing the throughput (events processed per second) and latency (p50, p99) of the new C++ integration against the legacy pure Python ABIDES implementation.

---

## Tasks List
- [x] **T1:** Initialize Python project, Dockerfile, and isolated venv sandbox.
- [x] **T1:** Define LangGraph `TypedDict` state structure.
- [x] **T1:** Implement Planner and Coder LLM nodes.
- [x] **T1:** Build Local Sandbox Executor Node for `pytest` isolation.
- [x] **T1:** Implement Review/Reflection Node and wire conditional edges.
- [x] **T1:** Test LangGraph pipeline against Agenthon G0 gate to evaluate pass@1.
- [x] **T3:** Scaffold C++ project (CMake) and Pybind11 dependencies.
- [x] **T3:** Implement zero-allocation `std::vector` pools and Array-based LOB.
- [x] **T3:** Implement single-threaded matching logic and OS thread-pinning.
- [x] **T3:** Implement `alignas(64)` SPSC Ring Buffer and Atomic Memory Bridge.
- [x] **T3:** Expose C++ Engine via Pybind11 with GIL-release wrappers.
- [x] **T3:** Integrate with Python `ExchangeAgent` in ABIDES.
- [x] **T3:** Run end-to-end performance benchmarking vs. native Python.
