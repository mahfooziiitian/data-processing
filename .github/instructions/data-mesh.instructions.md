---
applyTo: "src/data_proc/data_mesh/**/*.py"
---

# Data Mesh demo library conventions

This package is the reusable **library** half of the Data Mesh demo (see
the `src/` vs. `examples/` convention in
`.github/copilot-instructions.md`): it models decentralized domain
ownership via two independent domains, publishing through shared
contract/governance/catalog platform primitives. Usage code (CLI wiring,
publishing both domains, the cross-domain consumer) belongs in
`examples/run_data_mesh.py`, not here.

- **`domains/customers_domain.py` and `domains/orders_domain.py` must
  never import each other.** Decentralized ownership is the point — if a
  domain needs another domain's data, that need belongs in a *consumer*
  (`examples/run_data_mesh.py` or a new one), discovered via
  `catalog.get_product()`, not via direct inter-domain imports.
- Each domain's data product must stay scoped to what that domain
  actually owns: `customers_domain` must never publish order activity
  fields (`order_count`, `total_spent`, `last_order_date`), and
  `orders_domain` must never publish customer identity fields (`name`,
  `email`, `country`). If a consumer needs both, it joins the two
  published products itself.
- `contract.py` and `governance.py` are domain-agnostic platform code —
  don't add domain-specific logic (e.g. a `if domain == "orders"` branch)
  to either; new domain-specific rules belong in that domain's own
  `CONTRACT`/`build_product()`, not in the shared platform modules.
- Every domain's `publish()` must validate with both
  `contract.validate_schema()` **and**
  `governance.check_global_policies()` before writing anything, and must
  raise `ValueError` (never publish partially) if either reports
  violations — federated governance is enforced at the point of publish,
  not after.
- `catalog.py` is a JSON-backed registry, same spirit as
  `data_proc.kappa.event_log`'s file-based stand-in for a Kafka topic —
  keep entries plain-JSON-serializable and keyed by
  `DataContract.product_name` (`"<domain>.<name>"`).
- If you add/rename a field in a domain's product, update that domain's
  `CONTRACT.schema`, its `build_product()`, the matching table in
  `sql/schema.sql` (`data_mesh_customers_product` /
  `data_mesh_orders_product`), and `examples/run_data_mesh.py`'s consumer
  join + `data_mesh_consumer_view` together, and add/adjust a case in
  `tests/test_data_mesh_domains.py`.
- Persist each domain's own table with
  `data_proc.etl.load.load_dataframe(..., if_exists="replace")` (each
  domain's product is small and fully recomputed on every publish); the
  consumer view in `examples/run_data_mesh.py` does the same, since it's
  rebuilt fresh from both domains' tables on every consumer run.
