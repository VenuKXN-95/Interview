FROM python:3.12-slim

# Set working directory
WORKDIR /app

# System dependencies (curl needed for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer cache)
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore .

# Copy application code
COPY . .

# Create reports directory
RUN mkdir -p /app/generated_reports

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application (log-config null = use our structured JSON logger)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
