"""Data Mesh building blocks: decentralized, domain-oriented data products.

Unlike the batch ETL package (`data_proc.etl`), the Kappa package
(`data_proc.kappa`), and the Lambda package (`data_proc.lambda_arch`) — all
of which model a single pipeline/path owned by one team — this package
models **Data Mesh**'s four principles, each mapped onto a small module
here:

  * **Domain-oriented decentralized ownership** — `domains/customers_domain.py`
    and `domains/orders_domain.py` each independently own their source data
    and build logic. Neither imports the other; they only share the
    generic platform modules below, never each other's business logic.
  * **Data as a product** — every domain publishes its output as a
    `contract.DataContract`-described, discoverable **data product**
    (not just a table), with an owner, version, description, and schema.
  * **Self-serve data infrastructure as a platform** — `contract.py` and
    `catalog.py` are the generic, domain-agnostic platform primitives every
    domain reuses to validate and publish its product, and that any
    consumer uses to discover products without asking a domain team
    directly. `examples/run_data_mesh.py`'s cross-domain consumer step
    demonstrates self-serve consumption: it discovers both products via
    the catalog and joins them into its own view, without either domain
    needing to know the consumer exists.
  * **Federated computational governance** — `governance.py` defines
    global policies (naming, ownership, documentation, freshness SLA)
    that every domain's `publish()` function enforces on *itself* before
    publishing, rather than a central team gatekeeping every release.

Modules:
  * `contract` — `DataContract` dataclass + schema validation.
  * `governance` — global policy checks every contract must pass.
  * `catalog` — a JSON-backed, self-serve data product registry.
  * `domains/` — the two independent domains (customers, orders).

This is a library package: reusable building blocks only. The runnable
demo that wires these together (publishing both domains, then running a
cross-domain consumer) lives in `examples/run_data_mesh.py`.
"""
