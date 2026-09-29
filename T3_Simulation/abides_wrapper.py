import time
import threading
from typing import Any, Dict, List

# This module is built via CMake/Pybind11
try:
    import matching_engine 
except ImportError:
    matching_engine = None
    print("WARNING: C++ matching_engine not compiled yet. Run CMake build first.")

class CppExchangeAgent:
    """
    ABIDES-compatible ExchangeAgent wrapper.
    Routes orders from the Python Slow Loop to the C++ Fast Loop via the SPSC Ring Buffer.
    """
    def __init__(self, agent_id: int, name: str, queue_size: int = 1048576):
        self.id = agent_id
        self.name = name
        
        if matching_engine:
            # Initialize the Pybind11 C++ Matching Engine (capacity must be power of 2 for bitmask)
            self.engine = matching_engine.MatchingEngine(queue_size)
        else:
            self.engine = None
            
        self.running = False
        self._poll_thread = None
        
        # Central history of all fills received from the C++ engine
        self.fills_received: List[Dict[str, Any]] = []

    def start(self):
        """Starts the C++ hardware-pinned fast loop and the Python polling consumer."""
        if not self.engine:
            return
            
        self.engine.start()
        self.running = True
        self._poll_thread = threading.Thread(target=self._poll_fills, daemon=True)
        self._poll_thread.start()
        print(f"[{self.name}] C++ Matching Engine and Python Consumer Thread Started.")

    def stop(self):
        """Stops the engine and joins threads safely."""
        self.running = False
        if self.engine:
            self.engine.stop()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join()
        print(f"[{self.name}] C++ Matching Engine Stopped.")

    def place_order(self, order_id: int, symbol: str, side: str, price: int, quantity: int) -> bool:
        """
        Routes an order to the C++ Fast Loop via the lock-free SPSC Ring Buffer.
        Because the C++ binding uses py::gil_scoped_release, this immediately yields 
        the GIL and returns almost instantly.
        """
        if not self.engine:
            return False
            
        cpp_side = matching_engine.OrderSide.BUY if side.upper() == 'BUY' else matching_engine.OrderSide.SELL
        
        # Push to the lock-free queue
        success = self.engine.submit_order(order_id, symbol, cpp_side, price, quantity)
        
        if not success:
            print(f"[{self.name}] WARNING: SPSC Queue is full. Dropping order {order_id}!")
            
        return success

    def _poll_fills(self):
        """
        Continuous background loop polling the outgoing SPSC queue for FillEvents.
        """
        while self.running:
            # poll_fill explicitly releases the GIL inside C++ to prevent blocking
            fill = self.engine.poll_fill()
            
            if fill is not None:
                # We received a fill from the C++ Fast Loop
                fill_data = {
                    "order_id": fill.order_id,
                    "matched_price": fill.matched_price,
                    "matched_quantity": fill.matched_quantity,
                    "timestamp_ns": time.time_ns()
                }
                self.fills_received.append(fill_data)
                
                # In the full ABIDES architecture, we would dispatch a Message 
                # into the main ABIDES event priority queue here.
            else:
                # If the queue is empty, we yield to avoid burning the Python GIL thread
                # (The C++ Fast Loop never sleeps, but Python can)
                pass
