---
diataxis: tutorial
---

# Setup Guide

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker and Docker Compose (for the local PostgreSQL instance)
- `make` (optional, for the shortcut commands below)

## 1. Start PostgreSQL

```bash
docker compose up -d
```

This starts a `postgres:16-alpine` container on `localhost:5432` with:
- user: `postgres`
- password: `postgres`
- database: `data_processing_demo`

The schema in `src/data_proc/db/schema.sql` is applied automatically on first
container startup (via Postgres's `docker-entrypoint-initdb.d` mechanism).
If you change the schema file after the container's data volume already
exists, recreate the volume to re-apply it:

```bash
docker compose down -v && docker compose up -d
```

Check the container is healthy:

```bash
docker compose ps
docker compose exec postgres pg_isready -U postgres
```

## 2. Python environment

```bash
uv sync --all-groups
```

This creates `.venv/` and installs runtime dependencies plus the `dev`
(pytest) and `docs` (mkdocs) dependency groups declared in `pyproject.toml`.
Use `uv sync` alone to install only runtime dependencies.

## 3. Configuration

Copy `.env.example` to `.env` and adjust if needed, then export the
variables into your shell (the project does not depend on `python-dotenv`,
so either `export $(cat .env | xargs)` or set these manually):

```bash
cp .env.example .env
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/data_processing_demo
```

Defaults in `src/data_proc/config.py` already match the Docker Compose setup, so this
step is optional for a local demo run.

## 4. Run the pipeline

```bash
uv run python examples/run_pipeline.py
```

Expected log output ends with a summary like:

```
... Pipeline complete: {'customers': 10, 'orders': 19, 'customer_order_summary': 10}
```

## 5. Verify the results

```bash
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "SELECT name, country, order_count, total_spent FROM customer_order_summary ORDER BY total_spent DESC;"
```

## 6. Run the tests

```bash
uv run pytest -v
```

Tests do not require Docker/Postgres to be running — they use an in-memory
SQLite engine for the load layer and mock the external API call.

## 7. Build/preview the documentation site

```bash
uv run --group docs mkdocs serve   # http://127.0.0.1:8000, live reload
uv run --group docs mkdocs build --strict  # static site -> site/
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `psycopg2.OperationalError: connection refused` | Ensure `docker compose up -d` has finished and the container is healthy (`docker compose ps`) |
| Schema changes not reflected | Volumes persist data; run `docker compose down -v` to reset, then `up -d` again |
| `ModuleNotFoundError: No module named 'src'` | Run commands via `uv run` from the repo root so `pythonpath = ["."]` in `pyproject.toml` (`[tool.pytest.ini_options]`) takes effect |
| API enrichment step logs a warning | Expected when offline — `jsonplaceholder.typicode.com` is unreachable; the pipeline still completes with `company = NULL` |

## Tearing down

```bash
docker compose down -v   # stop Postgres and remove its data volume
rm -rf .venv              # remove the uv-managed virtual environment, if desired
```
