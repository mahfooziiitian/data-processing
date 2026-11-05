"""Central configuration for the ETL demo, driven by environment variables.

Variables are read from the process environment, optionally pre-populated
from a ``.env`` file (via ``python-dotenv``) if one exists in the current
working directory or a parent of it; real environment variables always take
precedence over ``.env`` values.

Every path setting resolves relative to a *data home* directory rather than
this file's location on disk, so the package behaves the same whether it is
run from a checkout or installed as a library (e.g. from site-packages,
where ``__file__``-relative paths would point at the wrong place). The data
home defaults to the current working directory — matching how the demo
scripts in ``examples/`` are documented to be run (``uv run python
examples/run_*.py`` from the repo root) — and can be overridden with the
``DATA_PROC_HOME`` environment variable. Each individual path can also be
overridden independently via its own environment variable.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# Load variables from a .env file (if present) into the process environment
# before any settings below are read. `usecwd=True` searches upward from the
# current working directory rather than from this file's location on disk,
# consistent with _data_home() below, so behavior does not depend on whether
# data_proc is run from a checkout or installed as a library. Existing
# environment variables always take precedence (load_dotenv never overrides
# by default).
load_dotenv(find_dotenv(usecwd=True))


def _data_home() -> Path:
    """Base directory that relative data paths are resolved against.

    Defaults to the current working directory. Override with the
    ``DATA_PROC_HOME`` environment variable to pin it to a specific
    directory regardless of where the process is launched from.
    """
    return Path(os.getenv("DATA_PROC_HOME", ".")).resolve()


def _path_setting(env_var: str, *default_parts: str) -> Path:
    """Resolve a path setting from ``env_var``, or default relative to the data home."""
    override = os.getenv(env_var)
    if override:
        return Path(override).resolve()
    return _data_home().joinpath(*default_parts)


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables with sane defaults."""

    customers_csv: Path = field(
        default_factory=lambda: _path_setting(
            "CUSTOMERS_CSV", "data", "raw", "customers.csv"
        )
    )
    orders_csv: Path = field(
        default_factory=lambda: _path_setting("ORDERS_CSV", "data", "raw", "orders.csv")
    )
    processed_dir: Path = field(
        default_factory=lambda: _path_setting("PROCESSED_DIR", "data", "processed")
    )

    # Kappa demo: append-only event log + consumer checkpoint (gitignored,
    # like the rest of data/processed/).
    kappa_event_log: Path = field(
        default_factory=lambda: _path_setting(
            "KAPPA_EVENT_LOG", "data", "processed", "kappa_events.jsonl"
        )
    )
    kappa_checkpoint: Path = field(
        default_factory=lambda: _path_setting(
            "KAPPA_CHECKPOINT", "data", "processed", "kappa_checkpoint.json"
        )
    )
    kappa_state_path: Path = field(
        default_factory=lambda: _path_setting(
            "KAPPA_STATE_PATH", "data", "processed", "kappa_order_state.json"
        )
    )

    # Lambda demo: a separate event log (not shared with the Kappa demo's
    # log, so the two demos don't interfere) + the batch layer's watermark.
    lambda_event_log: Path = field(
        default_factory=lambda: _path_setting(
            "LAMBDA_EVENT_LOG", "data", "processed", "lambda_events.jsonl"
        )
    )
    lambda_watermark: Path = field(
        default_factory=lambda: _path_setting(
            "LAMBDA_WATERMARK", "data", "processed", "lambda_watermark.json"
        )
    )

    # Data Mesh demo: the self-serve catalog both domains publish their
    # data products' metadata into (gitignored, like the rest of
    # data/processed/).
    data_mesh_catalog: Path = field(
        default_factory=lambda: _path_setting(
            "DATA_MESH_CATALOG", "data", "processed", "data_mesh_catalog.json"
        )
    )

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
