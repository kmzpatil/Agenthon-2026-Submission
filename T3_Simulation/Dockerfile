FROM python:3.13-slim

# Install C++ build tools required for Pybind11
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy CMake configuration and source code
COPY CMakeLists.txt .
COPY src/ ./src/
COPY abides_wrapper.py .
COPY benchmark.py .

# Build the C++ Fast Loop Extension
RUN mkdir build && cd build && \
    cmake .. && \
    cmake --build . --config Release

# Move the compiled shared object (.so) out of build directory so Python can import it
RUN cp build/*.so .

# Command for the evaluation container
CMD ["python", "benchmark.py"]
