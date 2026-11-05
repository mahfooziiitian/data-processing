"""Load layer: persist transformed data into PostgreSQL (or any SQLAlchemy target)."""
import logging

import pandas as pd
from sqlalchemy import Engine, create_engine

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
