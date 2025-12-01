.PHONY: help install docker-up docker-down docker-restart run dev test clean

ENV_FILE = .env


install: ## Install project dependencies using uv
	uv sync

docker-up: ## Start Docker services (MinIO and Qdrant)
	docker compose -f docker/docker-compose.yml --env-file $(ENV_FILE) up --build -d

docker-down: ## Stop Docker services
	docker compose -f docker/docker-compose.yml --env-file $(ENV_FILE) down -v

docker-restart: ## Restart Docker services
	docker compose -f docker/docker-compose.yml --env-file $(ENV_FILE) restart -v

docker-logs: ## View Docker services logs
	docker compose -f docker/docker-compose.yml --env-file $(ENV_FILE) logs

run-api: ## Run the FastAPI application
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

dev-api: ## Run the FastAPI application in development mode with auto-reload
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests
	uv run pytest src/tests/ -v

clean: ## Clean up Python temporary files and cache
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache

setup: ## Set up the project for the first time
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(YELLOW)Creating .env file from env.example...$(RESET)"; \
		cp env.example $(ENV_FILE); \
		echo "$(GREEN)✓ .env file created. Please review and adjust variables as needed.$(RESET)"; \
	else \
		echo "$(YELLOW).env file already exists.$(RESET)"; \
	fi
	@if ! command -v $(UV) >/dev/null 2>&1; then \
		echo "$(YELLOW)uv is not installed. Installing uv...$(RESET)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "$(GREEN)✓ uv installed successfully.$(RESET)"; \
	else \
		echo "$(GREEN)✓ uv is already installed.$(RESET)"; \
	fi
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	$(MAKE) install
	@echo "$(GREEN)✓ Setup completed!$(RESET)"

