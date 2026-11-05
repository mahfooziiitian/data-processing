"""Data product contracts: the shared, domain-agnostic schema/metadata
shape every domain publishes its data product against.

A `DataContract` is deliberately *not* domain-specific code — it's the
"self-serve platform" primitive that lets any domain describe its data
product declaratively (name, owner, schema, freshness SLA) and lets any
consumer validate a DataFrame against that description before trusting it,
without needing to read that domain's build logic.
"""
from dataclasses import dataclass, field

import pandas as pd

# Column "kinds" a contract can declare, each checked via a pandas dtype
# predicate below rather than an exact dtype string (e.g. "int64" vs
# "Int64" vs "int32"), so contracts stay robust to minor dtype differences
# between pandas/SQLAlchemy backends.
_KIND_CHECKS = {
    "int": pd.api.types.is_integer_dtype,
    "float": pd.api.types.is_float_dtype,
    "string": lambda s: pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s),
    "date": lambda s: pd.api.types.is_object_dtype(s) or pd.api.types.is_datetime64_any_dtype(s),
}


@dataclass(frozen=True)
class DataContract:
    """Describes one domain's data product: what it is, who owns it, and
    the schema consumers can rely on.

    `schema` maps column name -> kind (one of `"int"`, `"float"`,
    `"string"`, `"date"`), checked by `validate_schema` below.
    """

    domain: str
    name: str
    version: str
    owner: str
    description: str
    schema: dict[str, str] = field(default_factory=dict)
    sla_freshness_minutes: int = 60

    @property
    def product_name(self) -> str:
        """The catalog-wide unique identifier for this product, e.g.
        `"customers.customer_profile"`."""
        return f"{self.domain}.{self.name}"


def validate_schema(df: pd.DataFrame, contract: DataContract) -> list[str]:
    """Check `df` against `contract.schema`, returning a list of human
    -readable violation messages (empty list means `df` is compliant).

    Checks both directions: every contracted column must be present with
    a compatible dtype, and `df` must not carry undeclared columns — the
    contract is the full public shape of the product, not a minimum.
    """
    violations = []
    declared = set(contract.schema)
    actual = set(df.columns)

    for column in sorted(declared - actual):
        violations.append(f"missing contracted column '{column}'")
    for column in sorted(actual - declared):
        violations.append(f"undeclared column '{column}' not in contract schema")

    for column, kind in contract.schema.items():
        if column not in df.columns:
            continue
        check = _KIND_CHECKS.get(kind)
        if check is None:
            violations.append(f"column '{column}' declares unknown kind '{kind}'")
        elif not check(df[column]):
            violations.append(
                f"column '{column}' has dtype '{df[column].dtype}', "
                f"incompatible with declared kind '{kind}'"
            )
    return violations
