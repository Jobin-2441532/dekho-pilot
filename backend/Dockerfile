# ──────────────────────────────────────────────────────────────────────────────
# Dekho Backend — FastAPI + Uvicorn
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed by pdfplumber, psycopg2, and faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" dekhouser \
 && chown -R dekhouser:dekhouser /app
USER dekhouser

# Expose the API port
EXPOSE 8000

# Healthcheck — lets docker-compose know the API is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint — init DB tables then start uvicorn
CMD ["sh", "-c", "python -c 'from app.core.database import init_db; init_db()' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
