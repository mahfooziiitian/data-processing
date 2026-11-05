"""Federated computational governance: global policies every domain's data
product must satisfy, enforced independently by each domain at publish
time (via `domains/*_domain.py`'s own `publish()` function) rather than by
a central gatekeeping team or service.

"Federated" is the key word: the policies themselves are defined once,
globally, here — but *applying* them is each domain's own responsibility,
computationally checked rather than reviewed by a person. A domain that
fails a policy should fix its own contract; this module never reaches
into a domain to fix it for them.
"""
import re

from data_proc.data_mesh.contract import DataContract

_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_VERSION_PATTERN = re.compile(r"^v[0-9]+$")
_MIN_DESCRIPTION_LENGTH = 10


def check_global_policies(contract: DataContract) -> list[str]:
    """Check `contract` against the mesh-wide governance policies, returning
    a list of human-readable violation messages (empty list means the
    contract is compliant and may be published)."""
    violations = []

    if not _NAME_PATTERN.match(contract.domain):
        violations.append(
            f"domain '{contract.domain}' must be lowercase snake_case"
        )
    if not _NAME_PATTERN.match(contract.name):
        violations.append(
            f"product name '{contract.name}' must be lowercase snake_case"
        )
    if not _VERSION_PATTERN.match(contract.version):
        violations.append(
            f"version '{contract.version}' must match 'v<N>' (e.g. 'v1')"
        )
    if not contract.owner.strip():
        violations.append("owner must be a non-empty team/individual identifier")
    if len(contract.description.strip()) < _MIN_DESCRIPTION_LENGTH:
        violations.append(
            f"description must be at least {_MIN_DESCRIPTION_LENGTH} "
            "characters — it's the product's self-serve documentation"
        )
    if not contract.schema:
        violations.append("schema must declare at least one column")
    if contract.sla_freshness_minutes <= 0:
        violations.append("sla_freshness_minutes must be a positive number")

    return violations
