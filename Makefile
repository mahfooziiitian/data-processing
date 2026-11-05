.PHONY: setup up down test run docs docs-serve clean

setup:
	uv sync --all-groups

up:
	docker compose up -d
	@echo "Waiting for Postgres to be healthy..."
	@until docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done
	@echo "Postgres is ready on localhost:5432"

down:
	docker compose down

test:
	uv run pytest -v

run:
	uv run python examples/run_pipeline.py

run-kappa:
	uv run python examples/run_kappa_stream.py

run-lambda:
	uv run python examples/run_lambda_architecture.py

run-data-mesh:
	uv run python examples/run_data_mesh.py

docs:
	uv run --group docs mkdocs build --strict

docs-serve:
	uv run --group docs mkdocs serve --livereload

clean:
	docker compose down -v
	rm -rf .venv site
