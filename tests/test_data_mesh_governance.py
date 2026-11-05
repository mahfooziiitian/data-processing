"""Tests for federated governance policy checks."""
from dataclasses import replace

from data_proc.data_mesh.contract import DataContract
from data_proc.data_mesh.governance import check_global_policies

_COMPLIANT = DataContract(
    domain="customers",
    name="customer_profile",
    version="v1",
    owner="customers-domain-team",
    description="A sufficiently long and descriptive product description.",
    schema={"customer_id": "int"},
    sla_freshness_minutes=60,
)


def test_compliant_contract_has_no_violations():
    assert check_global_policies(_COMPLIANT) == []


def test_flags_non_snake_case_domain():
    contract = replace(_COMPLIANT, domain="Customers Domain")

    violations = check_global_policies(contract)

    assert any("lowercase snake_case" in v for v in violations)


def test_flags_bad_version_format():
    contract = replace(_COMPLIANT, version="1.0")

    violations = check_global_policies(contract)

    assert any("version '1.0'" in v for v in violations)


def test_flags_empty_owner():
    contract = replace(_COMPLIANT, owner="   ")

    violations = check_global_policies(contract)

    assert any("owner must be" in v for v in violations)


def test_flags_too_short_description():
    contract = replace(_COMPLIANT, description="short")

    violations = check_global_policies(contract)

    assert any("description must be at least" in v for v in violations)


def test_flags_empty_schema():
    contract = replace(_COMPLIANT, schema={})

    violations = check_global_policies(contract)

    assert any("schema must declare" in v for v in violations)


def test_flags_non_positive_sla():
    contract = replace(_COMPLIANT, sla_freshness_minutes=0)

    violations = check_global_policies(contract)

    assert any("sla_freshness_minutes must be" in v for v in violations)
