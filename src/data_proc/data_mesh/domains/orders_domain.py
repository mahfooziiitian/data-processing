"""Orders domain: owns order activity data end-to-end.

This domain's data product is a **per-customer order aggregate**
(order_count, total_spent, last_order_date) keyed by `customer_id` only —
deliberately with no customer name/email/country. Those fields belong to
the customers domain's product (`customers_domain.py`); this domain has no
business publishing data it doesn't own, even though it would be
convenient to just join them in here. A consumer that wants both joins the
two products itself (see `examples/run_data_mesh.py`).
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine

from data_proc.data_mesh import catalog, governance
from data_proc.data_mesh.contract import DataContract, validate_schema
from data_proc.etl import extract, transform
from data_proc.etl.load import load_dataframe

TABLE_NAME = "data_mesh_orders_product"

CONTRACT = DataContract(
    domain="orders",
    name="order_summary",
    version="v1",
    owner="orders-domain-team",
    description=(
        "Per-customer order activity aggregates (count, spend, last "
        "order date) owned end-to-end by the orders domain. Contains no "
        "customer identity fields by design — see the customers domain's "
        "product for those."
    ),
    schema={
        "customer_id": "int",
        "order_count": "int",
        "total_spent": "float",
        "last_order_date": "date",
    },
    sla_freshness_minutes=30,
)


def build_product() -> pd.DataFrame:
    """Build this domain's data product from its own owned source — the
    orders CSV — with no input from the customers domain."""
    orders = transform.clean_orders(extract.extract_orders_csv())
    summary = (
        orders.groupby("customer_id")
        .agg(
            order_count=("order_id", "count"),
            total_spent=("line_total", "sum"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    summary["total_spent"] = summary["total_spent"].round(2)
    return summary


def publish(engine: Engine, catalog_path: Path) -> dict:
    """Build, validate (contract schema + global governance policies), and
    publish this domain's product: write it to its own table and register
    it in the catalog for self-serve discovery.

    Raises `ValueError` if the product fails validation — a non-compliant
    product is never published, enforcing federated governance at the
    point of publish rather than after the fact.
    """
    df = build_product()

    violations = validate_schema(df, CONTRACT) + governance.check_global_policies(
        CONTRACT
    )
    if violations:
        raise ValueError(
            f"{CONTRACT.product_name} failed validation: {'; '.join(violations)}"
        )

    load_dataframe(df, TABLE_NAME, engine)
    catalog.register_product(catalog_path, CONTRACT, TABLE_NAME, len(df))
    return {"product_name": CONTRACT.product_name, "rows_published": len(df)}
