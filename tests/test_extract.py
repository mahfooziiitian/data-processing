"""Tests for the extract layer: CSV reads and resilient API extraction."""
from unittest.mock import patch

import pandas as pd
import requests

from data_proc.etl import extract


def test_extract_customers_csv_reads_sample_data():
    df = extract.extract_customers_csv()
    assert len(df) == 10
    assert {"customer_id", "name", "email"}.issubset(df.columns)


def test_extract_orders_csv_reads_sample_data():
    df = extract.extract_orders_csv()
    assert len(df) == 20
    assert {"order_id", "customer_id", "quantity", "unit_price"}.issubset(df.columns)


def test_extract_customer_enrichment_api_falls_back_on_error():
    with patch("data_proc.etl.extract.requests.get", side_effect=requests.ConnectionError("boom")):
        df = extract.extract_customer_enrichment_api()
    assert isinstance(df, pd.DataFrame)
    assert df.empty
