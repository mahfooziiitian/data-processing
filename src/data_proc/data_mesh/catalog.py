"""Data product catalog: the self-serve registry domains publish to and
consumers discover products from.

Backed by a single JSON file (a minimal stand-in for a real catalog
service, same spirit as `data_proc.kappa.event_log`'s file-based stand-in
for a Kafka topic) so this demo needs no extra infrastructure. A consumer
only needs `catalog.get_product()`/`list_products()` — it never needs to
import a domain's own module — which is what makes catalog-based discovery
"self-serve" instead of requiring direct coordination with each domain.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from data_proc.data_mesh.contract import DataContract


def _read_catalog(catalog_path: Path) -> dict[str, dict[str, Any]]:
    if not catalog_path.exists():
        return {}
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def _write_catalog(catalog_path: Path, entries: dict[str, dict[str, Any]]) -> None:
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def register_product(
    catalog_path: Path,
    contract: DataContract,
    table_name: str,
    row_count: int,
) -> None:
    """Publish (or re-publish) one product's metadata entry into the
    catalog, keyed by `contract.product_name`. Re-registering an existing
    product overwrites its entry — the catalog always reflects the most
    recently published metadata, not a history of past publishes."""
    entries = _read_catalog(catalog_path)
    entries[contract.product_name] = {
        "domain": contract.domain,
        "name": contract.name,
        "version": contract.version,
        "owner": contract.owner,
        "description": contract.description,
        "schema": contract.schema,
        "sla_freshness_minutes": contract.sla_freshness_minutes,
        "table_name": table_name,
        "row_count": row_count,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_catalog(catalog_path, entries)


def list_products(catalog_path: Path) -> list[dict[str, Any]]:
    """Return every registered product's metadata entry, for self-serve
    browsing/discovery."""
    return list(_read_catalog(catalog_path).values())


def get_product(catalog_path: Path, product_name: str) -> dict[str, Any] | None:
    """Look up one product's metadata entry by `domain.name`, or `None`
    if it hasn't been published yet."""
    return _read_catalog(catalog_path).get(product_name)
