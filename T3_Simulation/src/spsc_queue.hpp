#pragma once

#include <atomic>
#include <cstddef>
#include <type_traits>

#ifdef __cpp_lib_hardware_interference_size
    #include <new>
    constexpr size_t cache_line_size = std::hardware_destructive_interference_size;
#else
    constexpr size_t cache_line_size = 64; // Standard assumption
#endif

namespace agenthon {

template <typename T, std::size_t Capacity>
class SpscRingBuffer {
    // Bitwise optimizations require Capacity to be a power of two
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
    static_assert(std::is_trivially_copyable_v<T>, "T must be trivially copyable for zero-allocation performance");
    
    static constexpr std::size_t kMask = Capacity - 1;

public:
    bool try_push(const T& v) noexcept { // producer only
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (tail - head_.load(std::memory_order_acquire) == Capacity) {
            return false; // Full
        }
        buffer_[tail & kMask] = v;
        tail_.store(tail + 1, std::memory_order_release); // publishes slot write
        return true;
    }

    bool try_pop(T& out) noexcept { // consumer only
        const auto head = head_.load(std::memory_order_relaxed);
        if (head == tail_.load(std::memory_order_acquire)) {
            return false; // Empty
        }
        out = buffer_[head & kMask];
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

private:
    // Padded to prevent false sharing between producer and consumer cores
    alignas(cache_line_size) std::atomic<std::size_t> head_{0}; // consumer-owned
    alignas(cache_line_size) std::atomic<std::size_t> tail_{0}; // producer-owned
    alignas(cache_line_size) T buffer_[Capacity];
};

} // namespace agenthon
