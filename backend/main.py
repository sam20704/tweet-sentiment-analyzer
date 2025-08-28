from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models import Tweet, SentimentResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tweet Sentiment Analysis API",
    description="A REST API for analyzing tweet sentiment using VADER sentiment analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of given text using VADER sentiment analyzer.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment analysis results
    """
    try:
        # Get sentiment scores
        scores = analyzer.polarity_scores(text)
        
        # Determine overall sentiment based on compound score
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Calculate confidence (absolute value of compound score)
        confidence = abs(compound)
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": scores
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing sentiment")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Tweet Sentiment Analysis API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "sentiment-analysis-api",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_tweet_sentiment(tweet: Tweet):
    """
    Analyze sentiment of a tweet.
    
    Args:
        tweet (Tweet): Tweet object containing text to analyze
        
    Returns:
        SentimentResponse: Sentiment analysis results
    """
    try:
        # Validate input
        if not tweet.text or not tweet.text.strip():
            raise HTTPException(status_code=400, detail="Tweet text cannot be empty")
        
        # Analyze sentiment
        result = analyze_sentiment(tweet.text.strip())
        
        # Create response
        response = SentimentResponse(
            text=tweet.text,
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=result["scores"]
        )
        
        logger.info(f"Analyzed sentiment for text: {tweet.text[:50]}...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
