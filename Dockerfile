# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY README.md LICENSE ./

# Install the package and dependencies
RUN uv sync --frozen --no-dev && uv build

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser
RUN mkdir -p /app/.uv_cache && chown -R appuser:appuser /app/.uv_cache

# Set environment variable for uv cache
ENV UV_CACHE_DIR=/app/.uv_cache
# Set the entry point to the CLI
ENTRYPOINT ["uv", "run", "openapi-to-mcp"]

# Default command shows help
CMD ["--help"]
