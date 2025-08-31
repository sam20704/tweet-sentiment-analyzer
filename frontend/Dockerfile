FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Fix for M1/M2 Macs and file watcher issues
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.fileWatcherType", "none"]