"""Transformation layer: clean, validate, and reshape extracted data.

Business rules demonstrated here:
  * drop order rows with a missing/invalid customer reference
  * compute a `line_total` per order (quantity * unit_price)
  * aggregate per-customer lifetime order metrics
  * optionally enrich customers with a company/website field from the API
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Normalize customer records: trim whitespace, dedupe, parse dates."""
    df = customers.copy()
    df["name"] = df["name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.date
    df = df.drop_duplicates(subset="customer_id")
    return df


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Drop orders with no valid customer_id and compute line totals."""
    df = orders.copy()
    before = len(df)
    df = df.dropna(subset=["customer_id"])
    df["customer_id"] = df["customer_id"].astype(int)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["line_total"] = df["quantity"] * df["unit_price"]
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %s order(s) with missing customer_id", dropped)
    return df


def enrich_customers(customers: pd.DataFrame, enrichment: pd.DataFrame) -> pd.DataFrame:
    """Left-join optional API enrichment data (company name) onto customers.

    Matching is done by position against the demo API (ids 1-10) purely to
    illustrate a multi-source merge; a real pipeline would join on a stable
    business key such as email.
    """
    df = customers.copy()
    if enrichment.empty or "company.name" not in enrichment.columns:
        df["company"] = None
        return df

    enrichment_map = enrichment.set_index("id")["company.name"].to_dict()
    df["company"] = df["customer_id"].map(enrichment_map)
    return df


def build_customer_order_summary(
    customers: pd.DataFrame, orders: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate orders per customer: count, total spend, last order date."""
    summary = (
        orders.groupby("customer_id")
        .agg(
            order_count=("order_id", "count"),
            total_spent=("line_total", "sum"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    result = customers.merge(summary, on="customer_id", how="left")
    result["order_count"] = result["order_count"].fillna(0).astype(int)
    result["total_spent"] = result["total_spent"].fillna(0.0).round(2)
    return result
