FROM python:3.11-slim

WORKDIR /app

# Install system dependencies untuk mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Development: Flask dev server dengan hot reload
# Production: ganti CMD ke waitress/gunicorn
CMD ["python", "run.py"]
