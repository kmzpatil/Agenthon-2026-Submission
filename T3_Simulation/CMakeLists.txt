cmake_minimum_required(VERSION 3.20)
project(AgenthonT3 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Fetch Pybind11
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.12.0
)
FetchContent_MakeAvailable(pybind11)

# Main matching engine module
pybind11_add_module(matching_engine 
    src/bindings.cpp 
    src/matching_engine.cpp
)

# High-frequency trading optimizations
target_compile_options(matching_engine PRIVATE -O3 -march=native -Wall -Wextra -Wno-unused-parameter)

# Platform specific optimizations
if(UNIX)
    target_link_libraries(matching_engine PRIVATE pthread)
endif()
