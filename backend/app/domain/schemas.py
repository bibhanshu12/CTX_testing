from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ColumnDef(BaseModel):
    name: str
    type: str
    key: bool = False


class EntityMetadata(BaseModel):
    name: str
    namespace: str
    key: str
    columns: List[ColumnDef]


class EntityListItem(BaseModel):
    name: str
    path: str


class EntityListResponse(BaseModel):
    data_source: str
    entities: List[EntityListItem]


class RecordsResponse(BaseModel):
    entity_set: str
    count: int
    value: List[Dict[str, Any]]


class ConnectionStatus(BaseModel):
    data_source: str
    connected: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class ImportMetadataRequest(BaseModel):
    content: str


class ImportMetadataResponse(BaseModel):
    valid: bool
    entity_sets_found: List[str]
    ctx_entities_found: List[str]
    message: str
