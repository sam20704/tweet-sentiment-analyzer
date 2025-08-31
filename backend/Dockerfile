FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data during build
RUN python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]