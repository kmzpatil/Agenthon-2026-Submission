#pragma once

#include <array>
#include <cstdint>
#include <bit> // for std::countl_zero

namespace agenthon {

// Preallocated pool size constraints
constexpr int MAX_TICKS = 131072;
constexpr int MAX_ORDERS = (1 << 20);

// Intrusive linked list node for O(1) queue management at a price level
struct OrderNode {
    uint64_t order_id;
    int64_t quantity;
    int32_t prev_idx;
    int32_t next_idx;
};

// Represents a price level (time-priority queue)
struct PriceLevel {
    int32_t head_idx = -1;
    int32_t tail_idx = -1;
};

class FlatOrderBook {
private:
    struct BookSide {
        std::array<PriceLevel, MAX_TICKS> levels{}; 
        std::array<uint64_t, MAX_TICKS/64> bits{}; // Occupancy bitboard for fast iteration
    };

    // Preallocated memory pool for all orders to guarantee zero allocations (no malloc/new)
    std::array<OrderNode, MAX_ORDERS> pool_; 
    std::array<int32_t, MAX_ORDERS> free_; 
    int32_t free_top_;

    BookSide bids_{};
    BookSide asks_{};

    int32_t alloc_node(uint64_t id, int64_t qty) {
        if (free_top_ == 0) return -1; // Pool exhausted policy
        const int32_t idx = free_[--free_top_];
        pool_[idx] = OrderNode{id, qty, -1, -1};
        return idx;
    }

    void free_node(int32_t idx) {
        free_[free_top_++] = idx;
    }

public:
    FlatOrderBook() : free_top_(MAX_ORDERS) {
        for (int32_t i = 0; i < MAX_ORDERS; ++i) {
            free_[i] = i;
        }
    }

    // Add an order to a given BookSide at a specific tick (price offset)
    void add(BookSide& s, int tick, uint64_t order_id, int64_t qty) {
        if (tick < 0 || tick >= MAX_TICKS) return; // Out of bounds safety
        
        int32_t node_idx = alloc_node(order_id, qty);
        if (node_idx == -1) return;

        PriceLevel& lv = s.levels[tick];
        bool was_empty = (lv.head_idx == -1);

        // Intrusive FIFO push_back
        if (was_empty) {
            lv.head_idx = node_idx;
            lv.tail_idx = node_idx;
        } else {
            pool_[node_idx].prev_idx = lv.tail_idx;
            pool_[lv.tail_idx].next_idx = node_idx;
            lv.tail_idx = node_idx;
        }

        if (was_empty) {
            s.bits[tick / 64] |= (1ULL << (tick % 64));
        }
    }

    // Single-cycle jump to the best bid using countl_zero on the bitboard
    int best_bid_tick() const {
        for (int w = (MAX_TICKS / 64) - 1; w >= 0; --w) {
            if (auto word = bids_.bits[w]; word != 0) {
                return w * 64 + 63 - std::countl_zero(word);
            }
        }
        return -1;
    }

    // Single-cycle jump to the best ask
    int best_ask_tick() const {
        for (int w = 0; w < (MAX_TICKS / 64); ++w) {
            if (auto word = asks_.bits[w]; word != 0) {
                // For asks, we want the lowest set bit
                return w * 64 + std::countr_zero(word);
            }
        }
        return -1;
    }
    
    BookSide& get_bids() { return bids_; }
    BookSide& get_asks() { return asks_; }
};

} // namespace agenthon
