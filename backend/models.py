from pydantic import BaseModel
from typing import Optional

class Tweet(BaseModel):
    text: str
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "text": "I love this new product! It's amazing!"
            }
        }

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    scores: dict
    
    class Config:
        schema_extra = {
            "example": {
                "text": "I love this new product!",
                "sentiment": "positive",
                "confidence": 0.85,
                "scores": {
                    "positive": 0.85,
                    "negative": 0.05,
                    "neutral": 0.10,
                    "compound": 0.7269
                }
            }
        }
