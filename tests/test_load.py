"""Tests for the load layer using an in-memory SQLite engine as a stand-in."""
import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from data_proc.etl import load
from examples import run_pipeline


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


def test_refresh_tables_preserves_foreign_keys_and_replaces_rows():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
        conn.execute(text("CREATE TABLE child (id INTEGER REFERENCES parent(id))"))
        conn.execute(text("INSERT INTO parent VALUES (1)"))
        conn.execute(text("INSERT INTO child VALUES (1)"))

    frames = {"parent": pd.DataFrame({"id": [2]}), "child": pd.DataFrame({"id": [2]})}
    for _ in range(2):
        assert load.refresh_tables(frames, engine) == {"parent": 1, "child": 1}
    with engine.connect() as conn:
        assert conn.execute(text("SELECT id FROM child")).scalar() == 2
        assert conn.execute(text("PRAGMA foreign_key_list(child)")).first() is not None


def test_refresh_tables_rolls_back_if_insert_fails():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
        conn.execute(text("CREATE TABLE child (id INTEGER REFERENCES parent(id))"))
        conn.execute(text("INSERT INTO parent VALUES (1)"))
        conn.execute(text("INSERT INTO child VALUES (1)"))

    with pytest.raises(pd.errors.DatabaseError, match="FOREIGN KEY constraint failed"):
        load.refresh_tables(
            {"parent": pd.DataFrame({"id": [2]}), "child": pd.DataFrame({"id": [3]})},
            engine,
        )
    with engine.connect() as conn:
        assert conn.execute(text("SELECT id FROM parent")).scalar() == 1
        assert conn.execute(text("SELECT id FROM child")).scalar() == 1


def test_upsert_complete_view_removes_missing_keys_including_empty_view():
    engine = create_engine("sqlite:///:memory:")
    load.load_dataframe(pd.DataFrame({"id": [1, 2], "value": ["a", "b"]}), "demo_table", engine)

    load.upsert_dataframe(
        pd.DataFrame({"id": [2], "value": ["updated"]}),
        "demo_table", "id", engine, remove_missing=True,
    )
    with engine.connect() as conn:
        assert conn.execute(text("SELECT id, value FROM demo_table")).all() == [(2, "updated")]

    load.upsert_dataframe(
        pd.DataFrame(columns=["id", "value"]), "demo_table", "id", engine,
        remove_missing=True,
    )
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM demo_table")).scalar() == 0


def test_upsert_removes_only_explicit_stale_keys():
    engine = create_engine("sqlite:///:memory:")
    load.load_dataframe(
        pd.DataFrame({"id": [1, 2, 3], "value": ["old", "stale", "unrelated"]}),
        "demo_table", engine,
    )

    load.upsert_dataframe(
        pd.DataFrame({"id": [1], "value": ["new"]}), "demo_table", "id",
        engine, remove_keys=[2],
    )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT id, value FROM demo_table ORDER BY id")).all() == [
            (1, "new"), (3, "unrelated"),
        ]


def test_pipeline_refreshes_initialized_schema_twice(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.execute(text(
            "CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, "
            "email TEXT, country TEXT, signup_date DATE, company TEXT)"
        ))
        conn.execute(text(
            "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER "
            "REFERENCES customers(customer_id), product TEXT, quantity INTEGER, "
            "unit_price REAL, order_date DATE, line_total REAL)"
        ))
        conn.execute(text(
            "CREATE TABLE customer_order_summary (customer_id INTEGER PRIMARY KEY "
            "REFERENCES customers(customer_id), name TEXT, email TEXT, country TEXT, "
            "signup_date DATE, company TEXT, order_count INTEGER, total_spent REAL, "
            "last_order_date DATE)"
        ))

    customers = pd.DataFrame([{
        "customer_id": 1, "name": "Alice", "email": "alice@example.com",
        "country": "USA", "signup_date": "2024-01-01",
    }])
    orders = pd.DataFrame([{
        "order_id": 10, "customer_id": 1, "product": "Widget",
        "quantity": 2, "unit_price": 5.0, "order_date": "2024-01-02",
    }])
    monkeypatch.setattr(run_pipeline.extract, "extract_customers_csv", lambda: customers)
    monkeypatch.setattr(run_pipeline.extract, "extract_orders_csv", lambda: orders)
    monkeypatch.setattr(run_pipeline.extract, "extract_customer_enrichment_api", pd.DataFrame)
    monkeypatch.setattr(run_pipeline.load, "get_engine", lambda: engine)

    for _ in range(2):
        assert run_pipeline.run() == {"customers": 1, "orders": 1, "customer_order_summary": 1}
    with engine.connect() as conn:
        assert conn.execute(text(
            "SELECT customer_id, order_count, total_spent FROM customer_order_summary"
        )).all() == [(1, 1, 10.0)]
