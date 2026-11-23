.DEFAULT_GOAL := setup

.PHONY: help install-deps start-services stop-services show-status follow-logs \
	test run-etl run-kappa run-lambda run-data-mesh build-image \
	run-etl-docker run-kappa-docker run-lambda-docker run-data-mesh-docker \
	build-docs serve-docs clean-all setup up down status logs run \
	docker-build docker-run docker-kappa docker-lambda docker-data-mesh \
	docs docs-serve clean

UV ?= uv
COMPOSE ?= docker compose --project-directory . -f infra/docker-compose.yml
WAIT_TIMEOUT ?= 60
PYTEST_ARGS ?= -v
ARGS ?=

help: ## Show available targets and overrides
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '\nLegacy names remain available as aliases (setup, up, down, run, etc.).\n'
	@printf '\nOverrides: ARGS, PYTEST_ARGS, WAIT_TIMEOUT, UV, COMPOSE\n'

install-deps: ## Install runtime, development, and documentation dependencies
	$(UV) sync --all-groups

start-services: ## Start services and wait for health checks (WAIT_TIMEOUT in seconds)
	$(COMPOSE) up -d --wait --wait-timeout $(WAIT_TIMEOUT)
	@echo "Postgres is ready on localhost:5432"

stop-services: ## Stop services without deleting volumes
	$(COMPOSE) down

show-status: ## Show service status
	$(COMPOSE) ps

follow-logs: ## Follow service logs
	$(COMPOSE) logs --follow

test: ## Run tests (override PYTEST_ARGS to select tests)
	$(UV) run pytest $(PYTEST_ARGS)

run-etl: ## Run the batch ETL pipeline locally
	$(UV) run python examples/run_pipeline.py

run-kappa: ## Run Kappa locally (pass options with ARGS)
	$(UV) run python examples/run_kappa_stream.py $(ARGS)

run-lambda: ## Run Lambda locally (pass options with ARGS)
	$(UV) run python examples/run_lambda_architecture.py $(ARGS)

run-data-mesh: ## Run Data Mesh locally (pass options with ARGS)
	$(UV) run python examples/run_data_mesh.py $(ARGS)

build-image: ## Build the demo application image
	$(COMPOSE) --profile tools build app

run-etl-docker: ## Run batch ETL in Docker
	$(COMPOSE) --profile tools run --rm app

run-kappa-docker: ## Run Kappa in Docker (pass options with ARGS)
	$(COMPOSE) --profile tools run --rm app examples/run_kappa_stream.py $(ARGS)

run-lambda-docker: ## Run Lambda in Docker (pass options with ARGS)
	$(COMPOSE) --profile tools run --rm app examples/run_lambda_architecture.py $(ARGS)

run-data-mesh-docker: ## Run Data Mesh in Docker (pass options with ARGS)
	$(COMPOSE) --profile tools run --rm app examples/run_data_mesh.py $(ARGS)

build-docs: ## Build the documentation site
	$(UV) run --group docs mkdocs build --strict

serve-docs: ## Preview the documentation site
	$(UV) run --group docs mkdocs serve --livereload

clean-all: ## Delete database and demo state volumes, .venv, and site
	$(COMPOSE) down -v
	rm -rf .venv site

setup: install-deps
up: start-services
down: stop-services
status: show-status
logs: follow-logs
run: run-etl
docker-build: build-image
docker-run: run-etl-docker
docker-kappa: run-kappa-docker
docker-lambda: run-lambda-docker
docker-data-mesh: run-data-mesh-docker
docs: build-docs
docs-serve: serve-docs
clean: clean-all
