"""Load layer: persist transformed data into PostgreSQL (or any SQLAlchemy target)."""
import logging

import pandas as pd
from sqlalchemy import Engine, MetaData, Table, bindparam, create_engine, text

from data_proc.config import settings

logger = logging.getLogger(__name__)


def get_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the target database."""
    return create_engine(database_url or settings.database_url)


def load_dataframe(
    df: pd.DataFrame, table_name: str, engine: Engine, if_exists: str = "replace"
) -> int:
    """Write a DataFrame to a database table, returning the row count written."""
    logger.info("Loading %s row(s) into table '%s'", len(df), table_name)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    return len(df)


def refresh_tables(dataframes: dict[str, pd.DataFrame], engine: Engine) -> dict[str, int]:
    """Refresh existing tables in dependency order without dropping their schema.

    Pass parent tables before their dependents. Deletes run in reverse order
    and inserts run in forward order, in one transaction.
    """
    with engine.begin() as conn:
        metadata = MetaData()
        tables = {
            name: Table(name, metadata, autoload_with=conn) for name in dataframes
        }
        for table in reversed(list(tables.values())):
            conn.execute(table.delete())
        for name, df in dataframes.items():
            df.to_sql(name, conn, if_exists="append", index=False)
    return {name: len(df) for name, df in dataframes.items()}


def upsert_dataframe(
    df: pd.DataFrame, table_name: str, key_column: str, engine: Engine,
    *, remove_missing: bool = False, remove_keys: list | None = None,
) -> int:
    """Idempotently replace rows keyed by `key_column`: delete any existing
    rows whose key is present in `df`, then append `df`. Unlike
    `load_dataframe(..., if_exists="replace")`, this only touches the
    affected keys, so repeated or replayed calls with overlapping keys
    converge on the same end state without clobbering unrelated rows —
    the idempotency a Kappa-style replay (or any incremental upsert) needs.

    When `remove_missing` is true, `df` is the complete desired view and
    keys absent from it are deleted in the same transaction.
    Alternatively, `remove_keys` deletes only the specified stale keys.

    Uses a portable `DELETE ... WHERE key IN (...)` + `INSERT` rather than
    dialect-specific `ON CONFLICT`/`MERGE` syntax, so it works identically
    against Postgres (the demo target) and SQLite (used in tests).
    """
    if df.empty and not remove_missing and not remove_keys:
        return 0
    keys = df[key_column].tolist()
    keys_to_delete = keys + (remove_keys or [])
    delete_stmt = text(
        f"DELETE FROM {table_name} WHERE {key_column} IN :keys"  # noqa: S608
    ).bindparams(bindparam("keys", expanding=True))
    with engine.begin() as conn:
        if remove_missing:
            table = Table(table_name, MetaData(), autoload_with=conn)
            stale = table.delete()
            if keys:
                stale = stale.where(table.c[key_column].not_in(keys))
            conn.execute(stale)
        if keys_to_delete:
            conn.execute(delete_stmt, {"keys": keys_to_delete})
        if keys:
            df.to_sql(table_name, conn, if_exists="append", index=False)
    logger.info("Upserted %s row(s) into table '%s'", len(df), table_name)
    return len(df)


def read_dataframe(table_name: str, engine: Engine) -> pd.DataFrame:
    """Read a whole table into a DataFrame, returning an empty DataFrame
    (rather than raising) if the table exists but hasn't been populated
    yet — e.g. a serving-layer read of a batch view before the batch
    layer has ever run."""
    with engine.connect() as conn:
        return pd.read_sql_table(table_name, conn)
