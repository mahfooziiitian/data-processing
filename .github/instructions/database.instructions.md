---
applyTo: "src/db/schema.sql,docker-compose.yml,.env.example"
---

# Database & infrastructure conventions

- `src/db/schema.sql` is the single source of truth for table DDL. It is
  auto-applied by the `postgres` container only on **first startup**
  (mounted into `/docker-entrypoint-initdb.d/`); after editing it, run
  `docker compose down -v` (drops the data volume) before `docker compose
  up -d` so the new schema is actually applied.
- Keep `customers`, `orders`, and `customer_order_summary` table/column
  names and types in `schema.sql` in sync with what
  `src/etl/transform.py`/`load.py` actually produce — `load_dataframe()`
  uses `if_exists="replace"`, so a mismatch won't surface as a load error
  until queried.
- Default local credentials (`postgres`/`postgres`,
  `data_processing_demo`) are for the local demo only — never reuse them
  outside `docker-compose.yml`/`.env.example`, and don't introduce real
  secrets into either file.
- Keep `DATABASE_URL` in `.env.example` and the default in
  `src/config.py`'s `Settings` dataclass consistent with the
  `docker-compose.yml` service credentials/port/db name.
