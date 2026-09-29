#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Enables conversion for std::optional and std::string
#include <optional>
#include "matching_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(matching_engine, m) {
    m.doc() = "C++17 Bare-Metal Matching Engine for ABIDES (Agenthon T3)";

    py::enum_<agenthon::OrderSide>(m, "OrderSide")
        .value("BUY", agenthon::OrderSide::BUY)
        .value("SELL", agenthon::OrderSide::SELL)
        .export_values();

    py::class_<agenthon::FillEvent>(m, "FillEvent")
        .def_readonly("order_id", &agenthon::FillEvent::order_id)
        .def_readonly("matched_price", &agenthon::FillEvent::matched_price)
        .def_readonly("matched_quantity", &agenthon::FillEvent::matched_quantity);

    py::class_<agenthon::MatchingEngine>(m, "MatchingEngine")
        .def(py::init<size_t>(), py::arg("queue_size") = 1000000)
        
        .def("start", &agenthon::MatchingEngine::start)
        .def("stop", &agenthon::MatchingEngine::stop)
        
        // Use gil_scoped_release to ensure Python's Global Interpreter Lock (GIL)
        // is released while pushing to the lock-free queue, enabling true concurrency.
        .def("submit_order", &agenthon::MatchingEngine::submit_order, 
             py::call_guard<py::gil_scoped_release>(),
             py::arg("order_id"), py::arg("symbol"), py::arg("side"), py::arg("price"), py::arg("quantity"))
        
        .def("poll_fill", [](agenthon::MatchingEngine& self) -> std::optional<agenthon::FillEvent> {
            agenthon::FillEvent fill;
            // Explicitly release GIL while polling the atomic buffer.
            py::gil_scoped_release release;
            if (self.poll_fill(fill)) {
                return fill;
            }
            return std::nullopt;
        }, "Polls for the next filled order from the C++ Fast Loop.");
}
