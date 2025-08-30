import streamlit as st
import requests
import json
import plotly.graph_objects as go
import time
from typing import Dict, Any
import os  # <-- ADDED THIS LINE

# Page configuration
st.set_page_config(
    page_title="Tweet Sentiment Analyzer",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- REMOVED THE HARDCODED BACKEND_URL FROM HERE ---

def check_backend_health() -> bool:
    """Check if backend service is healthy"""
    # Get backend URL from environment variable, with a default for local development
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Send text to backend for sentiment analysis"""
    # Get backend URL from environment variable, with a default for local development
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    try:
        payload = {"text": text}
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend service. Please ensure the backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def create_sentiment_gauge(sentiment: str, confidence: float):
    """Create a gauge chart for sentiment visualization"""
    
    # Color mapping
    color_map = {
        "positive": "#00C851",
        "negative": "#FF4444", 
        "neutral": "#FFBB33"
    }
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Confidence ({sentiment.title()})"},
        delta = {'reference': 0.5},
        gauge = {
            'axis': {'range': [None, 1]},
            'bar': {'color': color_map.get(sentiment, "#CCCCCC")},
            'steps': [
                {'range': [0, 0.3], 'color': "#F0F0F0"},
                {'range': [0.3, 0.7], 'color': "#E0E0E0"},
                {'range': [0.7, 1], 'color': "#D0D0D0"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_scores_bar_chart(scores: Dict[str, float]):
    """Create bar chart for detailed sentiment scores"""
    
    # Remove compound score for cleaner visualization
    display_scores = {k: v for k, v in scores.items() if k != 'compound'}
    
    colors = ['#00C851', '#FF4444', '#FFBB33']  # green, red, yellow
    
    fig = go.Figure([
        go.Bar(
            x=list(display_scores.keys()),
            y=list(display_scores.values()),
            marker_color=colors,
            text=[f"{v:.3f}" for v in display_scores.values()],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Detailed Sentiment Scores",
        xaxis_title="Sentiment Type",
        yaxis_title="Score",
        height=400,
        showlegend=False
    )
    
    return fig

def main():
    # Header
    st.title("🐦 Tweet Sentiment Analysis")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This application analyzes the sentiment of tweet-like text using 
        VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis.
        
        **Sentiment Categories:**
        - 🟢 **Positive**: Happy, excited, satisfied
        - 🔴 **Negative**: Angry, sad, disappointed  
        - 🟡 **Neutral**: Factual, balanced, indifferent
        """)
        
        st.header("🔧 System Status")
        if check_backend_health():
            st.success("✅ Backend Service: Online")
        else:
            st.error("❌ Backend Service: Offline")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Enter Tweet Text")
        
        # Text input
        tweet_text = st.text_area(
            "Write your tweet here:",
            placeholder="Enter the tweet text you want to analyze...",
            height=150,
            max_chars=280,  # Twitter character limit
            help="Maximum 280 characters (Twitter limit)"
        )
        
        # Character counter
        char_count = len(tweet_text)
        if char_count > 0:
            color = "red" if char_count > 280 else "green"
            st.markdown(f"<p style='color: {color}; font-size: 12px;'>Characters: {char_count}/280</p>", 
                       unsafe_allow_html=True)
        
        # Analyze button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            analyze_btn = st.button("🔍 Analyze Sentiment", type="primary")
        
        with col_btn2:
            clear_btn = st.button("🗑️ Clear")
            if clear_btn:
                st.experimental_rerun()
    
    with col2:
        st.subheader("Quick Examples")
        
        examples = [
            "I love this new product! It's amazing! 😍",
            "This is the worst service ever. Very disappointed. 😠",
            "The weather is sunny today. Temperature is 75°F.",
            "Just finished my morning workout! Feeling great! 💪",
            "Traffic is terrible. Going to be late for work again. 😤"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"Example {i+1}", key=f"example_{i}", help=example):
                st.session_state.example_text = example
                
        # Load example if button was clicked
        if 'example_text' in st.session_state:
            tweet_text = st.session_state.example_text
            del st.session_state.example_text
            st.experimental_rerun()
    
    # Analysis section
    if analyze_btn and tweet_text.strip():
        with st.spinner("Analyzing sentiment..."):
            result = analyze_sentiment(tweet_text.strip())
            
        if result:
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            # Main result display
            sentiment = result['sentiment']
            confidence = result['confidence']
            scores = result['scores']
            
            # Emoji mapping
            emoji_map = {
                "positive": "🟢",
                "negative": "🔴", 
                "neutral": "🟡"
            }
            
            # Results columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Sentiment",
                    f"{emoji_map.get(sentiment, '⚪')} {sentiment.title()}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Confidence",
                    f"{confidence:.1%}",
                    delta=f"{confidence:.3f}"
                )
            
            with col3:
                compound_score = scores.get('compound', 0)
                st.metric(
                    "Compound Score", 
                    f"{compound_score:.3f}",
                    delta=None
                )
            
            # Visualizations
            st.markdown("### 📈 Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                gauge_fig = create_sentiment_gauge(sentiment, confidence)
                st.plotly_chart(gauge_fig, use_container_width=True)
            
            with viz_col2:
                bar_fig = create_scores_bar_chart(scores)
                st.plotly_chart(bar_fig, use_container_width=True)
            
            # Detailed scores
            st.markdown("### 📋 Detailed Scores")
            
            scores_df_data = []
            for score_type, value in scores.items():
                scores_df_data.append({
                    "Score Type": score_type.title(),
                    "Value": f"{value:.4f}",
                    "Percentage": f"{value:.1%}" if score_type != 'compound' else f"{((value + 1) / 2):.1%}"
                })
            
            st.table(scores_df_data)
            
            # Interpretation
            st.markdown("### 🔍 Interpretation")
            
            if sentiment == "positive":
                st.success(f"""
                **Positive Sentiment Detected** 🟢  
                The text expresses positive emotions with {confidence:.1%} confidence.
                This indicates satisfaction, happiness, or approval.
                """)
            elif sentiment == "negative":
                st.error(f"""
                **Negative Sentiment Detected** 🔴  
                The text expresses negative emotions with {confidence:.1%} confidence.
                This indicates dissatisfaction, sadness, or disapproval.
                """)
            else:
                st.info(f"""
                **Neutral Sentiment Detected** 🟡  
                The text appears neutral with {confidence:.1%} confidence.
                This indicates factual, balanced, or indifferent content.
                """)
    
    elif analyze_btn and not tweet_text.strip():
        st.warning("⚠️ Please enter some text to analyze!")

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666666;'>Built with FastAPI, Streamlit & Docker | Powered by VADER Sentiment Analysis</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()