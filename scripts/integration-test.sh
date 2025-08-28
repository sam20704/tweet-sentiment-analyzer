#!/bin/bash

echo "Running integration tests..."

# Start services
docker-compose up -d

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

# Test frontend
echo "Testing frontend..."
frontend_response=$(curl -s -w "%{http_code}" http://localhost:8501/_stcore/health)
if [[ "${frontend_response: -3}" == "200" ]]; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "✅ All integration tests passed!"

# Cleanup
docker-compose down
