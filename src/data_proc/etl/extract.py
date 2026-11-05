"""Extraction layer: pull raw data from CSV files and a public REST API.

Each function returns a pandas DataFrame so downstream transform steps can
operate on a consistent in-memory representation regardless of source type.
"""
import logging

import pandas as pd
import requests

from data_proc.config import settings

logger = logging.getLogger(__name__)


def extract_customers_csv() -> pd.DataFrame:
    """Read raw customer records from the local CSV source."""
    logger.info("Extracting customers from %s", settings.customers_csv)
    return pd.read_csv(settings.customers_csv)


def extract_orders_csv() -> pd.DataFrame:
    """Read raw order records from the local CSV source."""
    logger.info("Extracting orders from %s", settings.orders_csv)
    return pd.read_csv(settings.orders_csv)


def extract_customer_enrichment_api() -> pd.DataFrame:
    """Fetch supplementary customer profile data from a public demo API.

    Falls back to an empty DataFrame if the API is unreachable so the
    pipeline can still run end-to-end in offline/demo environments.
    """
    logger.info("Extracting enrichment data from %s", settings.enrichment_api_url)
    try:
        response = requests.get(
            settings.enrichment_api_url, timeout=settings.request_timeout_seconds
        )
        response.raise_for_status()
        payload = response.json()
        return pd.json_normalize(payload)
    except requests.RequestException as exc:
        logger.warning("Enrichment API unavailable (%s); continuing without it", exc)
        return pd.DataFrame()
