# ==========================================
# OmniAgent AI - Production Multi-Agent Dockerfile
# ==========================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .

# Install dependencies without heavy cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend & frontend files
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env /app/.env

# Create persistent storage directories
RUN mkdir -p /app/backend/uploads /app/backend/chroma_db /app/backend/logs

# Expose port
EXPOSE 8000

# Start production server binding to dynamic Render PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
