#pragma once

#include "spsc_queue.hpp"
#include <thread>
#include <atomic>
#include <string>
#include <vector>

namespace agenthon {

enum class OrderSide { BUY, SELL };

// Plain Old Data (POD) struct for high performance. 
// No std::string allowed to prevent heap allocation.
struct Order {
    uint64_t order_id;
    char symbol[8]; 
    OrderSide side;
    uint64_t price;
    uint64_t quantity;
};

struct FillEvent {
    uint64_t order_id;
    uint64_t matched_price;
    uint64_t matched_quantity;
};

class MatchingEngine {
private:
    SpscRingBuffer<Order, 262144> incoming_orders;
    SpscRingBuffer<FillEvent, 262144> outgoing_fills;
    
    std::atomic<bool> is_running;
    std::thread engine_thread;

    void run_fast_loop();
    void pin_thread_to_core();

public:
    MatchingEngine(size_t queue_size = 262144);
    ~MatchingEngine();

    void start();
    void stop();

    // Called by Python (Producer)
    bool submit_order(uint64_t order_id, const std::string& symbol, int side, uint64_t price, uint64_t quantity);
    
    // Called by Python (Consumer)
    bool poll_fill(FillEvent& fill);
};

} // namespace agenthon
