"""Customers domain: owns customer identity + profile data end-to-end.

This domain's data product intentionally does **not** include order
activity (order_count, total_spent, etc.) — that's the orders domain's
concern (see `orders_domain.py`). A consumer that wants both joins the two
published products itself (see `examples/run_data_mesh.py`'s consumer
step); that composition-by-consumer, not inter-domain coupling, is the
point of decentralized domain ownership.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine

from data_proc.data_mesh import catalog, governance
from data_proc.data_mesh.contract import DataContract, validate_schema
from data_proc.etl import extract, transform
from data_proc.etl.load import load_dataframe

TABLE_NAME = "data_mesh_customers_product"

CONTRACT = DataContract(
    domain="customers",
    name="customer_profile",
    version="v1",
    owner="customers-domain-team",
    description=(
        "Customer identity and profile data owned end-to-end by the "
        "customers domain: raw CSV fields plus optional company "
        "enrichment from the public demo API."
    ),
    schema={
        "customer_id": "int",
        "name": "string",
        "email": "string",
        "country": "string",
        "signup_date": "date",
        "company": "string",
    },
    sla_freshness_minutes=60,
)


def build_product() -> pd.DataFrame:
    """Build this domain's data product from its own owned sources — the
    customers CSV plus the enrichment API — with no input from the orders
    domain."""
    customers = transform.clean_customers(extract.extract_customers_csv())
    enrichment = extract.extract_customer_enrichment_api()
    return transform.enrich_customers(customers, enrichment)


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
