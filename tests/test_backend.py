import pytest
import sys
import os
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Add backend to path for import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Synchronous test client for non-async tests
client = TestClient(app)

class TestSentimentAPI:
    """Test suite for sentiment analysis API"""
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sentiment-analysis-api"
    
    def test_analyze_positive_sentiment(self):
        tweet_data = {"text": "I love this product! It's amazing and wonderful!"}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "text" in data
        assert "sentiment" in data
        assert "confidence" in data
        assert "scores" in data
        
        assert data["sentiment"] == "positive"
        assert data["text"] == tweet_data["text"]
        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
        
        scores = data["scores"]
        # VADER keys are pos, neg, neu, compound
        assert "pos" in scores
        assert "neg" in scores
        assert "neu" in scores
        assert "compound" in scores
    
    def test_analyze_negative_sentiment(self):
        tweet_data = {"text": "I hate this product! It's terrible and awful!"}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "negative"
        assert data["text"] == tweet_data["text"]
        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
    
    def test_analyze_neutral_sentiment(self):
        tweet_data = {"text": "The weather is 75 degrees today."}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "neutral"
        assert data["text"] == tweet_data["text"]
    
    def test_empty_text_error(self):
        tweet_data = {"text": ""}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_whitespace_only_text_error(self):
        tweet_data = {"text": "   "}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 400
    
    def test_missing_text_field_error(self):
        response = client.post("/analyze", json={})
        assert response.status_code == 422  # Validation error
    
    def test_invalid_json_error(self):
        response = client.post("/analyze", data="invalid json")
        assert response.status_code == 422
    
    def test_long_text_analysis(self):
        long_text = "This is a very long positive message. " * 10 + "I love it!"
        tweet_data = {"text": long_text}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
    
    def test_special_characters_handling(self):
        tweet_data = {"text": "I love this! 😍❤️🎉 #awesome @company"}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] == "positive"
    
    def test_mixed_sentiment_text(self):
        tweet_data = {"text": "I love the design but hate the price. It's good but expensive."}
        response = client.post("/analyze", json=tweet_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sentiment"] in ["positive", "negative", "neutral"]


@pytest.mark.asyncio
class TestAsyncSentimentAPI:
    """Async test cases for performance testing"""
    
    async def test_concurrent_requests(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            tasks = [ac.post("/analyze", json={"text": f"Test message {i}"}) for i in range(10)]
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert "sentiment" in data


if __name__ == "__main__":
    pytest.main(["-v", __file__])
