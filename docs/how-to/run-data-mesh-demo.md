---
diataxis: how-to
---

# Run the Data Mesh demo

This guide walks through `examples/run_data_mesh.py`, which demonstrates
the **Data Mesh** pattern: two independent domains publishing their own
data products through a shared, self-serve catalog, consumed by a
cross-domain join that neither domain writes itself. See
[Data Mesh architecture demo](../explanation/architecture.md#data-mesh-architecture-demo)
for the design rationale.

## Prerequisites

- Dependencies installed: `uv sync --all-groups`
- PostgreSQL running with the current schema applied:

  ```bash
  docker compose down -v   # only needed if you've run an older schema before
  docker compose up -d --wait
  ```

## 1. Publish both domains and run the consumer

```bash
uv run python examples/run_data_mesh.py
```

This single command:

1. Builds and publishes the **customers domain**'s product
   (`data_mesh_customers_product`) — customer identity/profile fields
   only, no order activity.
2. Builds and publishes the **orders domain**'s product
   (`data_mesh_orders_product`) — per-customer order aggregates only, no
   customer identity fields.
3. Prints every product currently registered in the self-serve catalog
   (`data/processed/data_mesh_catalog.json`).
4. Runs the **consumer** step: discovers both products via the catalog
   (not by importing either domain's module), joins them, and writes the
   result to `data_mesh_consumer_view`.

You should see log lines like:

```text
INFO Published {'product_name': 'customers.customer_profile', 'rows_published': 10}
INFO Published {'product_name': 'orders.order_summary', 'rows_published': 10}
INFO Catalog has 2 published product(s):
INFO   - customers.customer_profile (owner=customers-domain-team, ...)
INFO   - orders.order_summary (owner=orders-domain-team, ...)
INFO Consumer joined 10 row(s) into 'data_mesh_consumer_view'
```

## 2. Inspect each domain's own table

Each domain owns and writes only its own table — confirm neither contains
the other's fields:

```bash
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "\d data_mesh_customers_product" \
  -c "\d data_mesh_orders_product"
```

`data_mesh_customers_product` has no `order_count`/`total_spent` columns;
`data_mesh_orders_product` has no `name`/`email`/`country` columns. That
boundary is enforced by each domain's contract, not by convention — see
`tests/test_data_mesh_domains.py`.

## 3. Inspect the consumer's joined view

```bash
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "SELECT * FROM data_mesh_consumer_view ORDER BY total_spent DESC LIMIT 5;"
```

This view only exists because the *consumer* joined both products — it's
not something either domain publishes itself.

## 4. Browse the catalog without re-publishing

Once both domains have published at least once, you can inspect the
catalog and re-run the consumer without rebuilding either product:

```bash
uv run python examples/run_data_mesh.py --catalog-only
```

This models a second, independent consumer joining the mesh later: it
only needs the catalog (`data_proc.data_mesh.catalog.get_product()`) to
discover what's available, never direct coordination with the customers
or orders domain teams.

## What to look for

- The two domains' `publish()` calls in `examples/run_data_mesh.py` can
  run in either order (or on entirely separate schedules in a real
  system) — there's no shared state between them besides the catalog.
- Try breaking governance on purpose: edit `CONTRACT.owner = ""` in
  `src/data_proc/data_mesh/domains/customers_domain.py` and re-run — the
  domain's own `publish()` call raises `ValueError` before writing
  anything, since `governance.check_global_policies()` rejects an empty
  owner. Revert the change afterwards.
