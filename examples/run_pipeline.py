"""Example: wire the data_proc library functions together into a full
demo ETL run (extract -> transform -> load).

This is usage/demo code, not part of the `data_proc` library itself — it
shows how an application would compose the reusable extract/transform/load
helpers in `src/data_proc/etl/`. Run directly with:

    uv run python examples/run_pipeline.py
"""
import logging

from data_proc.etl import extract, transform, load

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> dict:
    """Execute the full demo ETL pipeline and return a summary of rows loaded."""
    logger.info("Starting data-processing demo pipeline")

    raw_customers = extract.extract_customers_csv()
    raw_orders = extract.extract_orders_csv()
    enrichment = extract.extract_customer_enrichment_api()

    customers = transform.clean_customers(raw_customers)
    customers = transform.enrich_customers(customers, enrichment)
    orders = transform.clean_orders(raw_orders)
    summary = transform.build_customer_order_summary(customers, orders)

    engine = load.get_engine()
    rows_loaded = {
        "customers": load.load_dataframe(customers, "customers", engine),
        "orders": load.load_dataframe(orders, "orders", engine),
        "customer_order_summary": load.load_dataframe(
            summary, "customer_order_summary", engine
        ),
    }

    logger.info("Pipeline complete: %s", rows_loaded)
    return rows_loaded


if __name__ == "__main__":
    run()
