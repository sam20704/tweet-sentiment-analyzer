FROM python:3.11-slim

# Set environment variables first (these rarely change, so it helps cache)
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

WORKDIR /app

# Install system dependencies and set timezone
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
  && echo $TZ > /etc/timezone \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Create non-root user and switch to that user (for security)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit app. Update "app.py" to your main streamlit script if different!
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.fileWatcherType=none"]