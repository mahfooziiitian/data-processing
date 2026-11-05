"""Tests for the independent customers and orders domains' build logic."""
from unittest.mock import patch

import requests

from data_proc.data_mesh.domains import customers_domain, orders_domain


def test_customers_domain_build_product_matches_its_own_contract_schema():
    with patch(
        "data_proc.etl.extract.requests.get",
        side_effect=requests.ConnectionError("offline demo"),
    ):
        df = customers_domain.build_product()

    assert len(df) == 10
    assert set(df.columns) == set(customers_domain.CONTRACT.schema)


def test_customers_domain_build_product_contains_no_order_fields():
    with patch(
        "data_proc.etl.extract.requests.get",
        side_effect=requests.ConnectionError("offline demo"),
    ):
        df = customers_domain.build_product()

    assert "order_count" not in df.columns
    assert "total_spent" not in df.columns


def test_orders_domain_build_product_matches_its_own_contract_schema():
    df = orders_domain.build_product()

    assert set(df.columns) == set(orders_domain.CONTRACT.schema)


def test_orders_domain_build_product_contains_no_customer_identity_fields():
    df = orders_domain.build_product()

    assert "name" not in df.columns
    assert "email" not in df.columns


def test_orders_domain_build_product_aggregates_per_customer():
    df = orders_domain.build_product()

    row = df[df["customer_id"] == 1].iloc[0]
    assert row["order_count"] == 3
    assert row["total_spent"] == 229.47
