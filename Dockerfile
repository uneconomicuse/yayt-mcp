FROM python:3.11-slim

WORKDIR /app

# Copy project definition
COPY pyproject.toml README.md ./
COPY src ./src

# Install dependencies and project
RUN pip install --no-cache-dir .

# Entrypoint for MCP stdio
CMD ["yt-mcp"]
