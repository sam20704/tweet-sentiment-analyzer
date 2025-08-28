.PHONY: help install test lint run-backend run-frontend run-docker clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx black

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run code formatting
	black backend/ frontend/ tests/

run-backend:  ## Run backend server
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:  ## Run frontend app
	cd frontend && streamlit run app.py --server.port 8501

run-docker:  ## Run with Docker Compose
	docker-compose up --build

stop-docker:  ## Stop Docker services
	docker-compose down

clean:  ## Clean up containers and images
	docker-compose down -v --rmi all --remove-orphans

logs:  ## Show Docker logs
	docker-compose logs -f

health:  ## Check service health
	curl -f http://localhost:8000/health
	curl -f http://localhost:8501/_stcore/health
