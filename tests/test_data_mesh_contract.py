"""Tests for data product contracts: schema validation."""
import pandas as pd

from data_proc.data_mesh.contract import DataContract, validate_schema

_CONTRACT = DataContract(
    domain="customers",
    name="customer_profile",
    version="v1",
    owner="customers-domain-team",
    description="A compliant test contract with a long enough description.",
    schema={"customer_id": "int", "name": "string", "signup_date": "date"},
)


def _valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [1, 2],
            "name": ["Alice", "Bob"],
            "signup_date": [pd.Timestamp("2024-01-01").date(), pd.Timestamp("2024-01-02").date()],
        }
    )


def test_product_name_combines_domain_and_name():
    assert _CONTRACT.product_name == "customers.customer_profile"


def test_validate_schema_passes_for_compliant_dataframe():
    assert validate_schema(_valid_df(), _CONTRACT) == []


def test_validate_schema_flags_missing_column():
    df = _valid_df().drop(columns=["signup_date"])

    violations = validate_schema(df, _CONTRACT)

    assert any("missing contracted column 'signup_date'" in v for v in violations)


def test_validate_schema_flags_undeclared_column():
    df = _valid_df()
    df["extra"] = "unexpected"

    violations = validate_schema(df, _CONTRACT)

    assert any("undeclared column 'extra'" in v for v in violations)


def test_validate_schema_flags_dtype_mismatch():
    df = _valid_df()
    df["customer_id"] = df["customer_id"].astype(str)

    violations = validate_schema(df, _CONTRACT)

    assert any("incompatible with declared kind 'int'" in v for v in violations)
