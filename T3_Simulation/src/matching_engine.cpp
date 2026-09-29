#include "matching_engine.hpp"
#include <iostream>
#include <cstring>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#else
#include <pthread.h>
#endif

namespace agenthon {

MatchingEngine::MatchingEngine(size_t queue_size) 
    : is_running(false) {}

MatchingEngine::~MatchingEngine() {
    stop();
}

void MatchingEngine::start() {
    if (!is_running.exchange(true)) {
        engine_thread = std::thread(&MatchingEngine::run_fast_loop, this);
    }
}

void MatchingEngine::stop() {
    if (is_running.exchange(false)) {
        if (engine_thread.joinable()) {
            engine_thread.join();
        }
    }
}

void MatchingEngine::pin_thread_to_core() {
#ifdef _WIN32
    // Windows: Pin to logical core 1 (bitmask 0x02)
    SetThreadAffinityMask(GetCurrentThread(), 2);
#else
    // Linux/Unix: Pin to core 1
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(1, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
#endif
}

void MatchingEngine::run_fast_loop() {
    // Hardware Sympathy: Bypass OS scheduler context switches
    pin_thread_to_core();

    while (is_running.load(std::memory_order_relaxed)) {
        Order order;
        if (incoming_orders.try_pop(order)) {
            // [TODO] Implement flat-array Limit Order Book logic here.
            // For now, this is a fast stub that auto-matches everything 
            // instantly to test the SPSC queue throughput overhead.
            
            FillEvent fill;
            fill.order_id = order.order_id;
            fill.matched_price = order.price;
            fill.matched_quantity = order.quantity;
            
            // Push to output queue (wait if full)
            while (!outgoing_fills.try_push(fill) && is_running.load(std::memory_order_relaxed)) {
                // Spin-wait (lock-free)
            }
        }
    }
}

bool MatchingEngine::submit_order(uint64_t order_id, const std::string& symbol, int side, uint64_t price, uint64_t quantity) {
    Order order;
    order.order_id = order_id;
    order.side = static_cast<OrderSide>(side);
    order.price = price;
    order.quantity = quantity;
    
    // Securely copy the symbol into the static char array
    std::strncpy(order.symbol, symbol.c_str(), sizeof(order.symbol) - 1);
    order.symbol[sizeof(order.symbol) - 1] = '\0';

    return incoming_orders.try_push(order);
}

bool MatchingEngine::poll_fill(FillEvent& fill) {
    return outgoing_fills.try_pop(fill);
}

} // namespace agenthon
