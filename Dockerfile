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

# Install system dependencies (C++ compilers & OCR dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend & frontend files
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env /app/.env

# Create persistent storage directories
RUN mkdir -p /app/backend/uploads /app/backend/chroma_db /app/backend/logs

# Expose port
EXPOSE 8000

# Start production server using uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
