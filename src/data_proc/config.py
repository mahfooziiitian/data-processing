"""Central configuration for the ETL demo, driven by environment variables."""
import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables with sane defaults."""

    customers_csv: Path = BASE_DIR / "data" / "raw" / "customers.csv"
    orders_csv: Path = BASE_DIR / "data" / "raw" / "orders.csv"
    processed_dir: Path = BASE_DIR / "data" / "processed"

    # Kappa demo: append-only event log + consumer checkpoint (gitignored,
    # like the rest of data/processed/).
    kappa_event_log: Path = BASE_DIR / "data" / "processed" / "kappa_events.jsonl"
    kappa_checkpoint: Path = BASE_DIR / "data" / "processed" / "kappa_checkpoint.json"
    kappa_state_path: Path = BASE_DIR / "data" / "processed" / "kappa_order_state.json"

    # Lambda demo: a separate event log (not shared with the Kappa demo's
    # log, so the two demos don't interfere) + the batch layer's watermark.
    lambda_event_log: Path = BASE_DIR / "data" / "processed" / "lambda_events.jsonl"
    lambda_watermark: Path = BASE_DIR / "data" / "processed" / "lambda_watermark.json"

    # Data Mesh demo: the self-serve catalog both domains publish their
    # data products' metadata into (gitignored, like the rest of
    # data/processed/).
    data_mesh_catalog: Path = BASE_DIR / "data" / "processed" / "data_mesh_catalog.json"

    # Public demo API used to enrich customer data (no auth required).
    enrichment_api_url: str = os.getenv(
        "ENRICHMENT_API_URL", "https://jsonplaceholder.typicode.com/users"
    )

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/data_processing_demo",
    )

    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))


settings = Settings()
