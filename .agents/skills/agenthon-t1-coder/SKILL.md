---
name: agenthon-t1-coder
description: Architecture, requirements, and instructions for building the T1 Quantitative Finance Coding Agent.
---

# T1: Quantitative Finance Coding Agent

## Objective
Build a Dockerized agent that solves quantitative-finance coding tasks programmatically.

## Evaluation Criteria
- **Unit Tests (`pytest`):** Generated code must run correctly without syntax or runtime errors.
- **Financial Invariants (g0-g3 gates):** The output must satisfy domain-specific constraints (e.g., $\sum weights = 1.0$).
- **Metric:** `pass@1`. The agent must output the correct file on its first attempt.

## Architecture Paradigm: Multi-Agent System
To achieve a high `pass@1` score, the agent must perform an internal retry loop before final submission.
Implement the following sub-agents in the solution:
1. **Planner Agent:** Extracts mathematical requirements and financial invariants from the prompt.
2. **Coder Agent:** Generates Python code using the permitted LLMs.
3. **Local Executor (Sandbox):** Executes `pytest` against generated edge cases. If financial invariant assertions fail, it feeds the stack trace back to the Coder Agent for iterative refinement.

## Execution Rules
- Always mock the financial invariants locally.
- Do not output the final solution until the local executor verifies the invariants.
