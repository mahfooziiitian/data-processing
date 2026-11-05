"""Example: Data Mesh demo — decentralized domain ownership, data as a
product, a self-serve catalog, and federated governance.

Unlike the batch pipeline, Kappa, and Lambda demos above (each a single
team's pipeline/path), this script wires together **two independent
domains** (`data_proc.data_mesh.domains.customers_domain` and
`.orders_domain`) that know nothing about each other, then runs a
**consumer** step that discovers both of their published products through
the shared catalog (`data_proc.data_mesh.catalog`) and joins them —
demonstrating self-serve cross-domain consumption instead of a central ETL
team wiring domains together directly.

This is usage/demo code, not part of the `data_proc` library itself — see
`src/data_proc/data_mesh/` for the reusable contract/governance/catalog/
domain building blocks this script composes.

Usage:
    uv run python examples/run_data_mesh.py
        Publish both domains' data products (each independently validated
        against its contract + the global governance policies), print the
        resulting catalog, then run the cross-domain consumer step and
        publish its joined view.

    uv run python examples/run_data_mesh.py --catalog-only
        Skip publishing; just print whatever is currently in the catalog
        (useful after a previous run).
"""
import argparse
import logging

import pandas as pd

from data_proc.config import settings
from data_proc.data_mesh import catalog
from data_proc.data_mesh.domains import customers_domain, orders_domain
from data_proc.etl.load import get_engine, load_dataframe, read_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_CONSUMER_TABLE = "data_mesh_consumer_view"


def publish_domains(engine) -> None:
    """Publish both domains' data products independently. Order doesn't
    matter — neither domain's `publish()` depends on the other having run,
    which is the point of decentralized ownership."""
    customers_result = customers_domain.publish(engine, settings.data_mesh_catalog)
    logger.info("Published %s", customers_result)
    orders_result = orders_domain.publish(engine, settings.data_mesh_catalog)
    logger.info("Published %s", orders_result)


def print_catalog() -> None:
    """Print every product currently registered in the self-serve catalog
    — what any consumer would see without asking a domain team directly."""
    products = catalog.list_products(settings.data_mesh_catalog)
    logger.info("Catalog has %s published product(s):", len(products))
    for product in products:
        logger.info(
            "  - %s (owner=%s, version=%s, table=%s, rows=%s)",
            f"{product['domain']}.{product['name']}",
            product["owner"],
            product["version"],
            product["table_name"],
            product["row_count"],
        )


def run_consumer(engine) -> pd.DataFrame:
    """Self-serve cross-domain consumption: discover the customers and
    orders products via the catalog (not by importing their modules
    directly), read their published tables, and join them into a view this
    consumer owns — neither domain publishes this joined shape itself."""
    customers_entry = catalog.get_product(
        settings.data_mesh_catalog, customers_domain.CONTRACT.product_name
    )
    orders_entry = catalog.get_product(
        settings.data_mesh_catalog, orders_domain.CONTRACT.product_name
    )
    if customers_entry is None or orders_entry is None:
        raise RuntimeError(
            "Both customers.customer_profile and orders.order_summary must "
            "be published before the consumer can run — try without "
            "--catalog-only first."
        )

    customers_df = read_dataframe(customers_entry["table_name"], engine)
    orders_df = read_dataframe(orders_entry["table_name"], engine)

    joined = customers_df.merge(orders_df, on="customer_id", how="left")
    joined["order_count"] = joined["order_count"].fillna(0).astype(int)
    joined["total_spent"] = joined["total_spent"].fillna(0.0).round(2)
    view = joined[
        [
            "customer_id", "name", "email", "country",
            "order_count", "total_spent", "last_order_date",
        ]
    ]

    rows = load_dataframe(view, _CONSUMER_TABLE, engine)
    logger.info("Consumer joined %s row(s) into '%s'", rows, _CONSUMER_TABLE)
    return view


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog-only", action="store_true",
        help="skip publishing; just print the current catalog contents",
    )
    args = parser.parse_args()

    engine = get_engine()
    if not args.catalog_only:
        publish_domains(engine)

    print_catalog()
    run_consumer(engine)


if __name__ == "__main__":
    main()
