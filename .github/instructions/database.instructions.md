---
applyTo: "sql/schema.sql,infra/**,.env.example"
---

# Database & infrastructure conventions

- `sql/schema.sql` is the single source of truth for table
  DDL. It is auto-applied by the `postgres` container only on **first
  startup** (mounted into `/docker-entrypoint-initdb.d/`). After editing
  it, an existing volume needs a migration or recreation before the new
  schema applies. `docker compose --project-directory . -f infra/docker-compose.yml down -v` destroys its data: explain this
  and obtain permission before resetting a volume.
- Keep `customers`, `orders`, and `customer_order_summary` table/column
  names and types in `schema.sql` in sync with what
  `src/data_proc/etl/transform.py`/`load.py` actually produce —
  the batch pipeline refreshes rows without dropping the initialized tables.
  Other demos use `if_exists="replace"` for independent tables, which
  recreates those tables and does not preserve their original constraints.
- From the repository root, use
  `docker compose --project-directory . -f infra/docker-compose.yml` so
  Compose resolves paths, `.env`, and existing volume names from the root.
  Docker build context filtering lives in `infra/Dockerfile.dockerignore`.
- Default local credentials (`postgres`/`postgres`,
  `data_processing_demo`) are for the local demo only — never reuse them
  outside `infra/docker-compose.yml`/`.env.example`, and don't introduce real
  secrets into either file.
- Keep `DATABASE_URL` in `.env.example` and the default in
  `src/data_proc/config.py`'s `Settings` dataclass consistent with the
  `infra/docker-compose.yml` service credentials/port/db name.
