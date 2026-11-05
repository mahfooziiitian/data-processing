"""Tests for the load layer using an in-memory SQLite engine as a stand-in."""
import pandas as pd
from sqlalchemy import create_engine, text

from data_proc.etl import load


def test_load_dataframe_writes_rows_to_table():
    engine = create_engine("sqlite:///:memory:")
    df = pd.DataFrame({"id": [1, 2], "value": ["a", "b"]})

    rows_written = load.load_dataframe(df, "demo_table", engine)

    assert rows_written == 2
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM demo_table")).scalar()
    assert count == 2


def test_upsert_dataframe_replaces_only_matching_keys():
    engine = create_engine("sqlite:///:memory:")
    load.load_dataframe(
        pd.DataFrame({"id": [1, 2], "value": ["a", "b"]}), "demo_table", engine
    )

    rows_written = load.upsert_dataframe(
        pd.DataFrame({"id": [2], "value": ["b-updated"]}), "demo_table", "id", engine
    )

    assert rows_written == 1
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, value FROM demo_table ORDER BY id")).all()
    assert rows == [(1, "a"), (2, "b-updated")]


def test_upsert_dataframe_empty_input_is_a_noop():
    engine = create_engine("sqlite:///:memory:")
    load.load_dataframe(
        pd.DataFrame({"id": [1], "value": ["a"]}), "demo_table", engine
    )

    rows_written = load.upsert_dataframe(
        pd.DataFrame(columns=["id", "value"]), "demo_table", "id", engine
    )

    assert rows_written == 0
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM demo_table")).scalar()
    assert count == 1
