#!/bin/bash

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
pip install -r requirements.txt
cd ..

# Install test dependencies
pip install pytest pytest-asyncio httpx

echo "Development environment setup complete!"
echo "To activate: source venv/bin/activate"
echo "To run backend: cd backend && uvicorn main:app --reload"
echo "To run frontend: cd frontend && streamlit run app.py"
echo "To run tests: pytest tests/"
