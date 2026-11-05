"""Tests for the transform layer using small in-memory fixtures."""
import pandas as pd

from src.etl import transform


def test_clean_customers_normalizes_fields():
    raw = pd.DataFrame(
        {
            "customer_id": [1, 1, 2],
            "name": [" Alice ", " Alice ", "Bob"],
            "email": ["ALICE@EXAMPLE.COM ", "ALICE@EXAMPLE.COM ", "bob@example.com"],
            "country": ["USA", "USA", "UK"],
            "signup_date": ["2023-01-01", "2023-01-01", "2023-02-01"],
        }
    )

    result = transform.clean_customers(raw)

    assert len(result) == 2  # duplicate customer_id removed
    assert result.loc[result["customer_id"] == 1, "name"].iloc[0] == "Alice"
    assert result.loc[result["customer_id"] == 1, "email"].iloc[0] == "alice@example.com"


def test_clean_orders_drops_missing_customer_and_computes_line_total():
    raw = pd.DataFrame(
        {
            "order_id": [1, 2],
            "customer_id": [1, None],
            "product": ["Widget", "Gadget"],
            "quantity": [2, 3],
            "unit_price": [10.0, 5.0],
            "order_date": ["2023-01-01", "2023-01-02"],
        }
    )

    result = transform.clean_orders(raw)

    assert len(result) == 1
    assert result.iloc[0]["line_total"] == 20.0


def test_build_customer_order_summary_aggregates_per_customer():
    customers = pd.DataFrame(
        {"customer_id": [1, 2], "name": ["Alice", "Bob"], "email": ["a@x.com", "b@x.com"]}
    )
    orders = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "customer_id": [1, 1, 2],
            "line_total": [20.0, 30.0, 15.0],
            "order_date": pd.to_datetime(["2023-01-01", "2023-01-05", "2023-01-02"]).date,
        }
    )

    summary = transform.build_customer_order_summary(customers, orders)

    alice = summary.loc[summary["customer_id"] == 1].iloc[0]
    assert alice["order_count"] == 2
    assert alice["total_spent"] == 50.0


def test_enrich_customers_without_api_data_adds_null_company():
    customers = pd.DataFrame({"customer_id": [1], "name": ["Alice"]})

    result = transform.enrich_customers(customers, pd.DataFrame())

    assert "company" in result.columns
    assert result.iloc[0]["company"] is None
