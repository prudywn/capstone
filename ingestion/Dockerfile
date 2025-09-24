# Use official Python slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables for production (can be overridden)
ENV MONGODB_URI=mongodb://mongo:27017
ENV POLL_INTERVAL_SECONDS=3600
ENV BACKFILL_DAYS=5

# Expose metrics port for Prometheus scraping
EXPOSE 8000

# Run the ingestion service
CMD ["python", "main.py"]
