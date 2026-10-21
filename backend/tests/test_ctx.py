import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api.routes import app  # noqa: E402
from app.services.ctx_service import ctx_service  # noqa: E402


client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["app"] == "CTX OData Explorer"


def test_list_entities():
    res = client.get("/api/ctx/entities")
    assert res.status_code == 200
    data = res.json()
    assert data["data_source"] == "seed"
    names = [e["name"] for e in data["entities"]]
    expected = [
        "CTX_RULEBOOK", "CTX_MOVEMENT_CLASS", "CTX_KPI_SOURCE_MAP",
        "CTX_KPI_CATALOG_MVT_TYPE", "CTX_CDS_S4_TABLE_FIELD_MAP",
        "CTX_KPI_CATALOG", "CTX_OBJECT_GRAIN_REGISTRY",
        "CTX_RELATIONSHIP_REGISTRY", "CTX_KPI_RELATIONSHIP_USAGE",
        "CTX_HARMONIZATION_RULES", "CTX_KPI_DEPENDENCY_GRAPH",
        "CTX_PARAMETER_CONFIG", "CTX_KPI_SAP_DETAIL", "CTX_MVP_SCOPE",
        "CTX_REQUIREMENT_CATALOG", "CTX_KNOWLEDGE_LINK",
    ]
    for e in expected:
        assert e in names, f"{e} missing from entity list"


def test_disallowed_entity_rejected():
    res = client.get("/api/ctx/entities/CsnDesignRun/records")
    assert res.status_code == 403


def test_get_metadata():
    res = client.get("/api/ctx/entities/CTX_RULEBOOK/metadata")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "CTX_RULEBOOK"
    assert data["key"] == "RULE_ID"
    col_names = [c["name"] for c in data["columns"]]
    assert "RULE_ID" in col_names
    assert "RULE_TYPE" in col_names


def test_get_records_seed():
    res = client.get("/api/ctx/entities/CTX_MOVEMENT_CLASS/records?$top=5")
    assert res.status_code == 200
    data = res.json()
    assert data["entity_set"] == "CTX_MOVEMENT_CLASS"
    assert data["count"] <= 5
    assert len(data["value"]) > 0
    assert data["value"][0]["MOVEMENT_TYPE"] == "101"


def test_get_records_pagination():
    res = client.get("/api/ctx/entities/CTX_MOVEMENT_CLASS/records?$top=1&$skip=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data["value"]) == 1


def test_get_records_filter():
    res = client.get("/api/ctx/entities/CTX_MOVEMENT_CLASS/records?$filter=STATUS eq 'Active'")
    assert res.status_code == 200
    data = res.json()
    for row in data["value"]:
        assert row["STATUS"] == "Active"


def test_connection_status():
    res = client.get("/api/ctx/status")
    assert res.status_code == 200
    data = res.json()
    assert data["data_source"] == "seed"
    assert data["connected"] is True


def test_import_metadata_valid():
    content = 'EntityType Name="CTX_RULEBOOK" \nEntityType Name="CsnDesignRun"'
    res = client.post("/api/ctx/import/metadata", json={"content": content})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert "CTX_RULEBOOK" in data["ctx_entities_found"]


def test_import_metadata_empty():
    res = client.post("/api/ctx/import/metadata", json={"content": "nothing here"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False


def test_ctx_service_allowlist():
    assert ctx_service is not None
    from app.core.allowlist import is_allowed_entity
    assert is_allowed_entity("CTX_RULEBOOK") is True
    assert is_allowed_entity("CsnDesignRun") is False
    assert is_allowed_entity("ProjectPortfolioView") is False
