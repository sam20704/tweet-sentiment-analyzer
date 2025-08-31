from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models import Tweet, SentimentResponse
import logging
import nltk
import ssl
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix SSL certificate issues for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Initialize FastAPI app
app = FastAPI(
    title="Tweet Sentiment Analysis API",
    description="A REST API for analyzing tweet sentiment using VADER sentiment analysis",
    version="1.0.0"
)

# Configure CORS - Updated to include both localhost and container hostnames
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501", "*"],  # Added frontend container hostname
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Download NLTK data on startup
@app.on_event("startup")
async def startup_event():
    """Download required NLTK data on application startup"""
    try:
        # Set NLTK data path if running in container
        nltk_data_dir = os.environ.get('NLTK_DATA', '/usr/local/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir, exist_ok=True)
        
        # Download required NLTK data
        nltk.download('vader_lexicon', quiet=True, download_dir=nltk_data_dir)
        nltk.download('punkt', quiet=True, download_dir=nltk_data_dir)
        
        # Add to NLTK path
        if nltk_data_dir not in nltk.data.path:
            nltk.data.path.append(nltk_data_dir)
            
        logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.warning(f"NLTK download warning: {e}")
        # Don't fail startup if download fails - may already be present

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
    """Root endpoint with API information"""
    return {
        "message": "Tweet Sentiment Analysis API",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint for container orchestration"""
    try:
        # Test VADER analyzer
        test_result = analyzer.polarity_scores("test")
        analyzer_status = "healthy" if test_result else "unhealthy"
    except Exception as e:
        analyzer_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "sentiment-analysis-api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "vader_analyzer": analyzer_status,
            "nltk_data": "loaded" if nltk.data.path else "not loaded"
        }
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
        
        # Check text length (Twitter's max is 280 characters, but we'll be flexible)
        if len(tweet.text) > 1000:
            raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
        
        # Analyze sentiment
        result = analyze_sentiment(tweet.text.strip())
        
        # Create response
        response = SentimentResponse(
            text=tweet.text,
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=result["scores"]
        )
        
        logger.info(f"Analyzed sentiment for text: {tweet.text[:50]}... - Result: {result['sentiment']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Tweet Sentiment Analysis API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=bool(os.getenv("DEBUG", False))
    )