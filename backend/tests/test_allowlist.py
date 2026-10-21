import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.allowlist import CTX_ALLOWLIST, is_allowed_entity  # noqa: E402


EXPECTED = [
    "CTX_RULEBOOK",
    "CTX_MOVEMENT_CLASS",
    "CTX_KPI_SOURCE_MAP",
    "CTX_KPI_CATALOG_MVT_TYPE",
    "CTX_CDS_S4_TABLE_FIELD_MAP",
    "CTX_KPI_CATALOG",
    "CTX_OBJECT_GRAIN_REGISTRY",
    "CTX_RELATIONSHIP_REGISTRY",
    "CTX_KPI_RELATIONSHIP_USAGE",
    "CTX_HARMONIZATION_RULES",
    "CTX_KPI_DEPENDENCY_GRAPH",
    "CTX_PARAMETER_CONFIG",
    "CTX_KPI_SAP_DETAIL",
    "CTX_MVP_SCOPE",
    "CTX_REQUIREMENT_CATALOG",
    "CTX_KNOWLEDGE_LINK",
]


def test_allowlist_exact():
    assert CTX_ALLOWLIST == EXPECTED


def test_allowlist_no_forbidden():
    forbidden = ["CsnDesignRun", "ModelDesignRun", "ProjectPortfolioView"]
    for f in forbidden:
        assert f not in CTX_ALLOWLIST
        assert is_allowed_entity(f) is False


def test_all_allowed_true():
    for e in EXPECTED:
        assert is_allowed_entity(e) is True
