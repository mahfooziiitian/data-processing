"""Tests for the load layer using an in-memory SQLite engine as a stand-in."""
import pandas as pd
from sqlalchemy import create_engine, text

from src.etl import load


def test_load_dataframe_writes_rows_to_table():
    engine = create_engine("sqlite:///:memory:")
    df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    rows_written = load.load_dataframe(df, "demo_table", engine)

    assert rows_written == 2
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM demo_table")).scalar()
    assert count == 2
