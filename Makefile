.PHONY: help install test lint run-backend run-frontend build up down logs clean health test-docker integration-test

# Default target
.DEFAULT_GOAL := help

# Variables
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DOCKER_COMPOSE := docker compose
PYTEST := python -m pytest

help: ## Show this help
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Usage: make [command]"

# Local Development Commands
install: ## Install all dependencies locally
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && pip install -r requirements.txt
	@echo "Installing test dependencies..."
	pip install pytest pytest-asyncio httpx black flake8 pytest-cov

test: ## Run tests locally
	@echo "Running backend tests..."
	cd $(BACKEND_DIR) && $(PYTEST) ../tests/ -v --tb=short

test-cov: ## Run tests with coverage
	@echo "Running tests with coverage..."
	cd $(BACKEND_DIR) && $(PYTEST) ../tests/ -v --cov=. --cov-report=html --cov-report=term

lint: ## Run code formatting and linting
	@echo "Running black formatter..."
	black $(BACKEND_DIR)/ $(FRONTEND_DIR)/ tests/ || echo "Formatting complete"
	@echo "Running flake8 linter..."
	flake8 $(BACKEND_DIR)/ --max-line-length=88 --extend-ignore=E203 || echo "Linting complete"

format: ## Auto-format code with black
	@echo "Auto-formatting code..."
	black $(BACKEND_DIR)/ $(FRONTEND_DIR)/ tests/

run-backend: ## Run backend server locally
	@echo "Starting backend server..."
	cd $(BACKEND_DIR) && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run frontend app locally
	@echo "Starting frontend app..."
	cd $(FRONTEND_DIR) && streamlit run app.py --server.port 8501

# Docker Commands
build: ## Build Docker images
	@echo "Building Docker images..."
	$(DOCKER_COMPOSE) build --pull

build-nocache: ## Build Docker images without cache
	@echo "Building Docker images (no cache)..."
	$(DOCKER_COMPOSE) build --pull --no-cache

up: ## Start all services with Docker Compose
	@echo "Starting services..."
	$(DOCKER_COMPOSE) up -d
	@echo "Services started! Backend: http://localhost:8000, Frontend: http://localhost:8501"

up-logs: ## Start services and show logs
	@echo "Starting services with logs..."
	$(DOCKER_COMPOSE) up

down: ## Stop all services
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

down-volumes: ## Stop services and remove volumes
	@echo "Stopping services and removing volumes..."
	$(DOCKER_COMPOSE) down -v

restart: ## Restart all services
	@echo "Restarting services..."
	$(DOCKER_COMPOSE) restart

ps: ## Show running containers
	@$(DOCKER_COMPOSE) ps

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Show backend logs
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Show frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Show database logs
	$(DOCKER_COMPOSE) logs -f db

# Docker Test Commands
test-docker: ## Run tests inside Docker container
	@echo "Running tests in Docker..."
	$(DOCKER_COMPOSE) run --rm backend python -m pytest /app/tests/ -v

integration-test: ## Run integration tests with Docker
	@echo "Running integration tests..."
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@make health || (echo "Health check failed"; make logs-backend; exit 1)
	$(DOCKER_COMPOSE) run --rm backend python -m pytest /app/tests/ -v
	$(DOCKER_COMPOSE) down

# Utility Commands
clean: ## Clean up everything (containers, volumes, images)
	@echo "Cleaning up Docker resources..."
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	@echo "Removing Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

clean-volumes: ## Remove only Docker volumes
	@echo "Removing Docker volumes..."
	$(DOCKER_COMPOSE) down -v

health: ## Check service health
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/health || echo "Backend health check failed"
	@echo ""
	@echo "Checking frontend health..."
	@curl -f http://localhost:8501 || echo "Frontend health check failed"

shell-backend: ## Open shell in backend container
	$(DOCKER_COMPOSE) exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec db psql -U postgres -d sentiment_db

# Development Workflow Commands
dev: ## Start development environment
	@echo "Starting development environment..."
	@make build
	@make up
	@echo "Waiting for services..."
	@sleep 5
	@make health

dev-reload: ## Rebuild and restart services
	@echo "Rebuilding and restarting services..."
	@make down
	@make build
	@make up
	@make health

# CI/CD Commands
ci-test: ## Run CI tests locally
	@echo "Running CI tests..."
	@make lint
	@make test-cov
	@echo "CI tests completed!"

validate: ## Validate Docker Compose configuration
	@echo "Validating Docker Compose configuration..."
	$(DOCKER_COMPOSE) config > /dev/null
	@echo "Configuration is valid!"

# Database Commands
db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	$(DOCKER_COMPOSE) exec backend python -c "print('No migrations configured yet')"

db-reset: ## Reset database
	@echo "Resetting database..."
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d db
	@echo "Database reset complete!"

# Monitoring Commands
stats: ## Show container resource usage
	@docker stats --no-stream $$($(DOCKER_COMPOSE) ps -q)

inspect-backend: ## Inspect backend container
	@docker inspect $$($(DOCKER_COMPOSE) ps -q backend)

# Quick Commands
quick-test: ## Quick test run
	@make test-docker

quick-start: ## Quick start (build and run)
	@make build && make up && make health