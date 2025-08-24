.PHONY: install test lint format type-check run build up down logs clean help

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER = docker
PYTHON = python
PIP = pip

# Help message
help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code with black and isort"
	@echo "  make type-check    Run type checking with mypy"
	@echo "  make run           Run the application locally"
	@echo "  make build         Build Docker images"
	@echo "  make up            Start all services"
	@echo "  make down          Stop all services"
	@echo "  make logs          View logs"
	@echo "  make clean         Clean up temporary files"

# Install dependencies
install:
	$(PIP) install -e ".[dev,postgres]"
	pre-commit install

# Run tests
test:
	pytest -v --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml

# Run linters
lint:
	black --check app tests
	isort --check-only app tests
	pylint app tests

# Format code
format:
	black app tests
	isort app tests

# Run type checking
type-check:
	mypy app tests

# Run the application locally
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Build Docker images
build:
	$(DOCKER_COMPOSE) build

# Start all services
up:
	$(DOCKER_COMPOSE) up -d

# Stop all services
down:
	$(DOCKER_COMPOSE) down

# View logs
logs:
	$(DOCKER_COMPOSE) logs -f

# Clean up temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage coverage.xml htmlcov/
	docker system prune -f

db-migrate:
	alembic upgrade head

db-makemigrations:
	alembic revision --autogenerate -m "$(m)"

db-downgrade:
	alembic downgrade -1

# Initialize the database
init-db:
	$(DOCKER_COMPOSE) up -d postgres redis
	@echo "Waiting for database to be ready..."
	@while ! $(DOCKER) exec ff-codex-postgres pg_isready -U postgres > /dev/null 2>&1; do \
		sleep 1; \
	done
	$(MAKE) db-migrate

# Reset the database
reset-db: down
	$(DOCKER) volume rm -f ff-codex-auth_postgres_data
	$(MAKE) init-db

# Run tests with coverage in Docker
test-docker: build
	$(DOCKER_COMPOSE) run --rm app make test

# Run linters in Docker
lint-docker: build
	$(DOCKER_COMPOSE) run --rm app make lint

# Format code in Docker
format-docker: build
	$(DOCKER_COMPOSE) run --rm app make format

# Run type checking in Docker
type-check-docker: build
	$(DOCKER_COMPOSE) run --rm app make type-check

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Install pre-commit hooks
install-hooks:
	pre-commit install --install-hooks

# Run all checks
check: lint type-check test
