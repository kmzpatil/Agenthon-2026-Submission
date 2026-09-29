# Sandbox environment for executing generated code
FROM python:3.11-slim

# Create a non-root user for safe execution
RUN useradd -m -s /bin/bash sandboxuser
WORKDIR /sandbox

# Install pytest
RUN pip install --no-cache-dir pytest

# Copy everything into sandbox and fix permissions
COPY --chown=sandboxuser:sandboxuser . /sandbox/

USER sandboxuser

# Default command just runs pytest
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
