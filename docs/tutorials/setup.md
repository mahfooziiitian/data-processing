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
docker compose --project-directory . -f infra/docker-compose.yml up -d
```

This starts a `postgres:16-alpine` container on `localhost:5432` with:
- user: `postgres`
- password: `postgres`
- database: `data_processing_demo`

The schema in `sql/schema.sql` is applied automatically on first
container startup (via Postgres's `docker-entrypoint-initdb.d` mechanism).
If you change the schema file after the container's data volume already
exists, migrate the existing database to preserve its data. Alternatively,
if the data can be discarded, recreate the volume to re-apply the schema.
**This deletes the Compose database volume and the demo state volume:**

```bash
docker compose --project-directory . -f infra/docker-compose.yml down -v && docker compose --project-directory . -f infra/docker-compose.yml up -d
```

Check the container is healthy:

```bash
docker compose --project-directory . -f infra/docker-compose.yml ps
docker compose --project-directory . -f infra/docker-compose.yml exec postgres pg_isready -U postgres
```

## 2. Python environment

```bash
uv sync --all-groups
```

This creates `.venv/` and installs runtime dependencies plus the `dev`
(pytest) and `docs` (mkdocs) dependency groups declared in `pyproject.toml`.
Use `uv sync` alone to install only runtime dependencies.

## 3. Configuration

Copy `.env.example` to `.env` and adjust if needed. `src/data_proc/config.py`
automatically loads `.env` via `python-dotenv`, so there is no need to
`export` or `source` the file yourself:

```bash
cp .env.example .env
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
docker compose --project-directory . -f infra/docker-compose.yml exec postgres psql -U postgres -d data_processing_demo \
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
| `psycopg2.OperationalError: connection refused` | Ensure `docker compose --project-directory . -f infra/docker-compose.yml up -d` has finished and the container is healthy (`docker compose --project-directory . -f infra/docker-compose.yml ps`) |
| Schema changes not reflected | Migrate the database or, if its data can be discarded, recreate the volume as described above |
| `ModuleNotFoundError: No module named 'data_proc'` | Run `uv sync --all-groups`, then use `uv run` so the editable `data_proc` package is available |
| API enrichment step logs a warning | Expected when offline — `jsonplaceholder.typicode.com` is unreachable; the pipeline still completes with `company = NULL` |

## Tearing down

```bash
docker compose --project-directory . -f infra/docker-compose.yml down -v   # remove the database and demo state volumes
rm -rf .venv              # remove the uv-managed virtual environment, if desired
```
