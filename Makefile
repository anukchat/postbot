# PostBot - Simple Commands

.PHONY: help
help: ## Show this help
	@echo "PostBot commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: local-up
local-up: ## Start locally (Docker Compose)
	docker compose -f docker-compose.local.yml up --build

.PHONY: local-down
local-down: ## Stop local containers
	docker compose -f docker-compose.local.yml down

.PHONY: local-logs
local-logs: ## Follow local logs
	docker compose -f docker-compose.local.yml logs -f

.PHONY: prod-up
prod-up: ## Start production stack (uses docker-compose.yml + .env on this machine)
	docker compose up -d --build --remove-orphans

.PHONY: prod-logs
prod-logs: ## Follow production logs (on this machine)
	docker compose logs -f

# ============================================================================
# Database Commands
# ============================================================================

.PHONY: db-seed
db-seed: ## Seed database with reference data (uses DATABASE_URL from .env.local or .env)
	@if [ -f .env.local ]; then \
		export $$(cat .env.local | grep DATABASE_URL | xargs) && \
		psql "$$DATABASE_URL" -f src/backend/db/migrations/seed_reference_data.sql; \
	elif [ -f .env ]; then \
		export $$(cat .env | grep DATABASE_URL | xargs) && \
		psql "$$DATABASE_URL" -f src/backend/db/migrations/seed_reference_data.sql; \
	else \
		echo "Error: No .env or .env.local file found"; \
		exit 1; \
	fi

.PHONY: db-seed-local
db-seed-local: ## Seed local database with reference data
	psql postgresql://anukoolchaturvedi@localhost:5432/postbot_dev -f src/backend/db/migrations/seed_reference_data.sql

.PHONY: db-migrate
db-migrate: ## Run Alembic migrations
	alembic upgrade head

.PHONY: db-reset-local
db-reset-local: ## Reset local database (drop and recreate)
	@echo "⚠️  This will drop and recreate the local database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		dropdb --if-exists postbot_dev; \
		createdb postbot_dev; \
		alembic upgrade head; \
		make db-seed-local; \
		echo "✅ Database reset complete!"; \
	fi

.DEFAULT_GOAL := help
