# PostBot - Kubernetes Development Commands

.PHONY: help
help: ## Show this help
	@echo "PostBot Kubernetes Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: local-cluster
local-cluster: ## Create local Kind cluster
	kind create cluster --name postbot --config k8s/local/kind-config.yaml

.PHONY: local-delete
local-delete: ## Delete local Kind cluster
	kind delete cluster --name postbot

# Environment selection: ENV=local (default) or ENV=production
ENV ?= local

.PHONY: build
build: ## Build Docker images locally (ENV=local or ENV=production)
	@ENV_FILE=".env.$(ENV)"; \
	if [ ! -f "$$ENV_FILE" ]; then \
		echo "Warning: $$ENV_FILE not found. Using .env as fallback."; \
		ENV_FILE=".env"; \
	fi; \
	echo "Building with $(ENV) environment ($$ENV_FILE)..."; \
	echo "Building frontend with environment variables from $$ENV_FILE..."; \
	docker build -f Dockerfile.frontend -t postbot-frontend:local \
		--build-arg VITE_SUPABASE_URL=$$(grep VITE_SUPABASE_URL $$ENV_FILE | cut -d '=' -f2-) \
		--build-arg VITE_SUPABASE_ANON_KEY=$$(grep VITE_SUPABASE_ANON_KEY $$ENV_FILE | cut -d '=' -f2-) \
		--build-arg VITE_API_URL=$$(grep VITE_API_URL $$ENV_FILE | cut -d '=' -f2-) \
		--build-arg VITE_REDIRECT_URL=$$(grep VITE_REDIRECT_URL $$ENV_FILE | cut -d '=' -f2-) \
		--build-arg VITE_AUTH_PROVIDER_URL=$$(grep VITE_AUTH_PROVIDER_URL $$ENV_FILE | cut -d '=' -f2-) \
		--build-arg VITE_AUTH_PROVIDER_KEY=$$(grep VITE_AUTH_PROVIDER_KEY $$ENV_FILE | cut -d '=' -f2-) \
		.
	@echo "Building backend..."
	docker build -f Dockerfile.backend -t postbot-backend:local .

.PHONY: load-images
load-images: ## Load images into Kind cluster
	kind load docker-image postbot-frontend:local --name postbot
	kind load docker-image postbot-backend:local --name postbot

.PHONY: deploy-local
deploy-local: ## Deploy to local cluster using Kustomize
	@ENV_FILE=".env.$(ENV)"; \
	if [ ! -f "$$ENV_FILE" ]; then \
		echo "Warning: $$ENV_FILE not found. Using .env as fallback."; \
		ENV_FILE=".env"; \
	fi; \
	echo "Creating secrets from $$ENV_FILE file..."; \
	sed 's/="\(.*\)"/=\1/g' $$ENV_FILE > /tmp/.env-no-quotes; \
	kubectl create secret generic postbot-secrets --from-env-file=/tmp/.env-no-quotes --namespace=postbot --dry-run=client -o yaml | kubectl apply -f -; \
	rm /tmp/.env-no-quotes
	kubectl apply -k k8s/overlays/local
	kubectl apply -k k8s/overlays/local

.PHONY: deploy-prod
deploy-prod: ## Deploy to production cluster using Kustomize
	kubectl apply -k k8s/overlays/production

.PHONY: local-all
local-all: local-cluster build load-images deploy-local ## Complete local setup (cluster + build + deploy)
	@echo ""
	@echo "✅ Local cluster is ready!"
	@echo ""
	@echo "Access application:"
	@echo "  Frontend: kubectl port-forward -n postbot service/frontend 3000:3000"
	@echo "  Backend:  kubectl port-forward -n postbot service/backend 8000:8000"
	@echo ""
	@echo "Or run: make port-forward"

.PHONY: port-forward
port-forward: ## Port forward frontend and backend
	@echo "Forwarding ports..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"
	@kubectl port-forward -n postbot service/frontend 3000:3000 & \
	kubectl port-forward -n postbot service/backend 8000:8000

.PHONY: logs
logs: ## Show logs from all pods
	kubectl logs -f -l app=backend -n postbot --tail=100

.PHONY: logs-frontend
logs-frontend: ## Show frontend logs
	kubectl logs -f -l app=frontend -n postbot --tail=100

.PHONY: logs-backend
logs-backend: ## Show backend logs (excluding health checks)
	kubectl logs -f -l app=backend -n postbot --tail=100 | grep -v "GET /health"

.PHONY: status
status: ## Show cluster status
	@echo "=== Namespaces ==="
	kubectl get namespaces
	@echo ""
	@echo "=== Pods ==="
	kubectl get pods -n postbot
	@echo ""
	@echo "=== Services ==="
	kubectl get services -n postbot
	@echo ""
	@echo "=== Deployments ==="
	kubectl get deployments -n postbot

.PHONY: restart
restart: ## Restart all deployments
	kubectl rollout restart deployment/frontend -n postbot
	kubectl rollout restart deployment/backend -n postbot

.PHONY: scale-up
scale-up: ## Scale up replicas (3 each)
	kubectl scale deployment/frontend --replicas=3 -n postbot
	kubectl scale deployment/backend --replicas=3 -n postbot

.PHONY: scale-down
scale-down: ## Scale down replicas (1 each)
	kubectl scale deployment/frontend --replicas=1 -n postbot
	kubectl scale deployment/backend --replicas=1 -n postbot

.PHONY: update
update: build load-images restart ## Rebuild, load, and restart (for development)
	@echo "✅ Updated and restarted!"

.PHONY: clean
clean: ## Clean all resources
	kubectl delete namespace postbot

.PHONY: shell-backend
shell-backend: ## Shell into backend pod
	kubectl exec -it -n postbot deployment/backend -- /bin/sh

.PHONY: shell-frontend
shell-frontend: ## Shell into frontend pod
	kubectl exec -it -n postbot deployment/frontend -- /bin/sh

.PHONY: k9s
k9s: ## Launch k9s terminal UI
	k9s -n postbot

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
