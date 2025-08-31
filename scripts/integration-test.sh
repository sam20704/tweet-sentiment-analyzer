#!/bin/bash

echo "Running integration tests..."

# Start services
docker compose up -d

# Wait for services
sleep 30

# Test backend
echo "Testing backend..."
response=$(curl -s -w "%{http_code}" http://localhost:8000/health)
if [[ "${response: -3}" == "200" ]]; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Test sentiment analysis
echo "Testing sentiment analysis..."
result=$(curl -s -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this test!"}')

if echo "$result" | grep -q "positive"; then
    echo "✅ Sentiment analysis working"
else
    echo "❌ Sentiment analysis failed"
    exit 1
fi

# --- Updated frontend health wait and test below ---

# Wait for frontend (Docker health status, NOT curl)
echo "Waiting for frontend to be healthy (docker healthcheck)..."
timeout 120s bash -c '
  frontend_id=$(docker compose ps -q frontend)
  while [ "$(docker inspect -f "{{.State.Health.Status}}" "$frontend_id")" != "healthy" ]; do
    echo "Frontend not healthy yet..."
    sleep 2
  done
'
echo "✅ Frontend is healthy!"

# Test frontend (via HTTP GET to /, should return 200 if Streamlit is up)
echo "Testing frontend response..."
frontend_http_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/)
if [[ "$frontend_http_response" == "200" ]]; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "✅ All integration tests passed!"

# Cleanup
docker compose down