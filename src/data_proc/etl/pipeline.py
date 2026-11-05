"""Pipeline orchestration: wires extract -> transform -> load together.

Run directly with: `python -m data_proc.etl.pipeline`
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
