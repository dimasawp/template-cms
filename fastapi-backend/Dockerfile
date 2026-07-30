FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for mysqlclient and weasyprint
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY . /app/

# Expose backend port
EXPOSE 8000

# Start server (run migrations, then uvicorn)
CMD ["sh", "-c", "alembic upgrade head || echo 'Migrations failed or not configured'; python -m db.seeds.seed --sync || echo 'Seeding failed or not configured'; uvicorn main:app --host 0.0.0.0 --port 8000"]
