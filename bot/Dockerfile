# Bot Dockerfile
# Multi-stage build using uv for dependency installation

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy bot source code
COPY bot.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/
COPY config.py ./

# Set the virtual environment path
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["uv", "run", "bot.py"]
