import streamlit as st
import requests
import json
import plotly.graph_objects as go
import time
from typing import Dict, Any
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Page configuration
st.set_page_config(
    page_title="Tweet Sentiment Analyzer",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create session with retry logic
def create_session():
    """Create a requests session with retry logic for resilient connections"""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]  # Fixed: Added missing list
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Get backend URL with validation
def get_backend_url():
    """Get and validate backend URL from environment variable"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    if not backend_url.startswith(('http://', 'https://')):
        backend_url = f"http://{backend_url}"
    return backend_url.rstrip('/')

# Initialize global session and backend URL
session = create_session()
BACKEND_URL = get_backend_url()

@st.cache_data(ttl=60)
def check_backend_health() -> bool:
    """Check if backend service is healthy using session with retries"""
    try:
        response = session.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        st.warning(f"Backend health check failed: {str(e)}")
        return False

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Send text to backend for sentiment analysis using session with retries"""
    try:
        payload = {"text": text}
        response = session.post(
            f"{BACKEND_URL}/analyze",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            st.error(f"Invalid request: {response.json().get('detail', 'Bad request')}")
            return None
        else:
            st.error(f"Backend error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend service. Please ensure the backend is running.")
        st.info(f"Trying to connect to: {BACKEND_URL}")
        return None
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
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
        domain = {'x': [0, 1], 'y': [0, 1]},  # Fixed: Added missing values
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
    display_scores = {k.title(): v for k, v in scores.items() if k != 'compound'}
    
    colors = ['#00C851', '#FF4444', '#FFBB33']  # Fixed: Added missing list (green, red, yellow)
    
    fig = go.Figure([  # Fixed: Completed the Figure creation
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
        backend_status = check_backend_health()
        if backend_status:
            st.success("✅ Backend Service: Online")
        else:
            st.error("❌ Backend Service: Offline")
            st.info(f"Backend URL: {BACKEND_URL}")
        
        # Debug info (optional - remove in production)
        with st.expander("🔍 Debug Info"):
            st.code(f"""
Backend URL: {BACKEND_URL}
Environment: {os.getenv('ENVIRONMENT', 'development')}
Session Retries: 5
Timeout: 10s
            """)
    
    # Main content
    col1, col2 = st.columns([2, 1])  # Fixed: Added missing column ratio
    
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
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])  # Fixed: Added missing column ratio
        
        with col_btn1:
            analyze_btn = st.button("🔍 Analyze Sentiment", type="primary", disabled=not backend_status)
        
        with col_btn2:
            if st.button("🗑️ Clear"):
                st.rerun()
    
    with col2:
        st.subheader("Quick Examples")
        
        examples = [  # Fixed: Added missing list
            "I love this new product! It's amazing! 😍",
            "This is the worst service ever. Very disappointed. 😠",
            "The weather is sunny today. Temperature is 75°F.",
            "Just finished my morning workout! Feeling great! 💪",
            "Traffic is terrible. Going to be late for work again. 😤"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"Example {i+1}", key=f"example_{i}", help=example):
                st.session_state.example_text = example
                st.rerun()
                
        # Load example if button was clicked
        if 'example_text' in st.session_state:
            tweet_text = st.session_state.example_text
            del st.session_state.example_text
            st.rerun()
    
    # Analysis section
    if 'result' not in st.session_state:
        st.session_state.result = None

    if analyze_btn and tweet_text.strip():
        if not backend_status:
            st.error("⚠️ Cannot analyze - Backend service is offline!")
        else:
            with st.spinner("Analyzing sentiment..."):
                # Add small delay for better UX
                time.sleep(0.5)
                st.session_state.result = analyze_sentiment(tweet_text.strip())
    
    elif analyze_btn and not tweet_text.strip():
        st.warning("⚠️ Please enter some text to analyze!")

    if st.session_state.result:
        result = st.session_state.result
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
        
        scores_df_data = []  # Fixed: Added missing list initialization
        for score_type, value in scores.items():
            scores_df_data.append({
                "Score Type": score_type.title(),
                "Value": f"{value:.4f}",
                "Percentage": f"{value:.1%}" if score_type != 'compound' else f"{((value + 1) / 2):.1%}"  # Fixed: spacing
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
        
        # Export results button
        st.markdown("### 💾 Export Results")
        
        export_data = {
            "text": tweet_text,
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": scores,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            st.download_button(
                label="📄 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"sentiment_analysis_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col_export2:
            # Create CSV format
            csv_data = f"""Text,Sentiment,Confidence,Positive,Negative,Neutral,Compound,Timestamp
"{tweet_text.replace('"', '""')}",{sentiment},{confidence:.4f},{scores['positive']:.4f},{scores['negative']:.4f},{scores['neutral']:.4f},{scores['compound']:.4f},{export_data['timestamp']}"""
            
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"sentiment_analysis_{int(time.time())}.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.markdown(
        """<p style='text-align: center; color: #666666;'>
        Built with FastAPI, Streamlit & Docker | Powered by VADER Sentiment Analysis
        </p>""",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()