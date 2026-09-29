import time
import timeit

# Try to import our C++ wrapper, but provide a graceful fallback message
try:
    from abides_wrapper import CppExchangeAgent
except ImportError:
    CppExchangeAgent = None

class NativePythonLOB:
    """A naive Python dictionary-based Limit Order Book for baseline comparison."""
    def __init__(self):
        self.bids = {}
        self.asks = {}
    
    def add_order(self, order_id, side, price, qty):
        book = self.bids if side == 'BUY' else self.asks
        if price not in book:
            book[price] = []
        book[price].append((order_id, qty))

def run_benchmarks():
    orders = 100_000
    print(f"--- Agenthon T3 LOB Benchmark ---")
    print(f"Routing {orders:,} consecutive limit orders...\n")
    
    # 1. Native Python Baseline
    native_lob = NativePythonLOB()
    start = time.perf_counter_ns()
    for i in range(orders):
        native_lob.add_order(i, 'BUY', 1000 + (i % 10), 100)
    end = time.perf_counter_ns()
    native_ns_per_order = (end - start) / orders
    print(f"Native Python LOB (ABIDES legacy): {native_ns_per_order:,.0f} ns / order")
    
    if not CppExchangeAgent:
        print("\n[!] Cannot run C++ benchmarks. matching_engine module not built.")
        print("Please compile the C++ pybind11 extension via CMake first.")
        return

    # 2. C++ Fast Loop (Pybind11 + SPSC)
    cpp_agent = CppExchangeAgent(1, "FastCppAgent", 262144) # Power of 2 queue
    cpp_agent.start()
    
    # Give the thread a moment to spin up and pin to core
    time.sleep(0.1)
    
    start = time.perf_counter_ns()
    for i in range(orders):
        # This crosses the pybind11 FFI boundary, pushes to SPSC, and yields the GIL
        cpp_agent.place_order(i, "AAPL", 'BUY', 1000 + (i % 10), 100)
    end = time.perf_counter_ns()
    cpp_ns_per_order = (end - start) / orders
    
    print(f"C++ Fast Loop LOB (Dual-Loop):     {cpp_ns_per_order:,.0f} ns / order")
    
    if cpp_ns_per_order > 0:
        print(f"\n=> Estimated Speedup: {native_ns_per_order / cpp_ns_per_order:.1f}x")
    
    cpp_agent.stop()

if __name__ == "__main__":
    run_benchmarks()
