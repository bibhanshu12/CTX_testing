import json
import os
from typing import Any, Dict, List, Optional

from app.core.allowlist import is_allowed_entity
from app.core.exceptions import EntityNotAllowedError, EntityNotFoundError
from app.persistence.base import CTXRepository
from app.domain.entities import CTX_METADATA, get_columns


def _resolve_data_dir(data_dir: str) -> str:
    if os.path.isabs(data_dir) and os.path.isdir(data_dir):
        return data_dir
    if os.path.isdir(data_dir):
        return data_dir
    # Fallback: resolve relative to the backend directory (this file's parents)
    here = os.path.dirname(os.path.abspath(__file__))  # .../backend/app/persistence
    backend_dir = os.path.abspath(os.path.join(here, os.pardir, os.pardir))  # .../backend
    candidate = os.path.join(backend_dir, data_dir)
    if os.path.isdir(candidate):
        return candidate
    return data_dir


class SeedCTXRepository(CTXRepository):
    def __init__(self, data_dir: str) -> None:
        self.data_dir = _resolve_data_dir(data_dir)
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def _entity_path(self, entity_set: str) -> str:
        return os.path.join(self.data_dir, f"{entity_set}.json")

    def _load(self, entity_set: str) -> List[Dict[str, Any]]:
        if entity_set in self._cache:
            return self._cache[entity_set]
        path = self._entity_path(entity_set)
        if not os.path.isfile(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
        self._cache[entity_set] = data
        return data

    def list_entities(self) -> List[str]:
        return [e for e in CTX_METADATA.keys() if is_allowed_entity(e)]

    def get_metadata(self, entity_set: str) -> Dict[str, Any]:
        if not is_allowed_entity(entity_set):
            raise EntityNotAllowedError(entity_set)
        if entity_set not in CTX_METADATA:
            raise EntityNotFoundError(entity_set)
        meta = CTX_METADATA[entity_set]
        return {
            "name": entity_set,
            "namespace": meta["namespace"],
            "key": meta["key"],
            "columns": get_columns(entity_set),
        }

    def get_records(
        self,
        entity_set: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter: Optional[str] = None,
        orderby: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not is_allowed_entity(entity_set):
            raise EntityNotAllowedError(entity_set)
        if entity_set not in CTX_METADATA:
            raise EntityNotFoundError(entity_set)

        records = list(self._load(entity_set))

        if filter:
            records = [r for r in records if self._matches_filter(r, filter)]

        if orderby:
            field = orderby.lstrip("-").strip()
            desc = orderby.startswith("-")
            records.sort(
                key=lambda r: r.get(field, ""),
                reverse=desc,
            )

        total = len(records)
        if skip is not None:
            records = records[skip:]
        if top is not None:
            records = records[:top]

        return {"entity_set": entity_set, "count": len(records), "total": total, "value": records}

    def _matches_filter(self, record: Dict[str, Any], filter_expr: str) -> bool:
        try:
            if " eq " in filter_expr:
                field, value = filter_expr.split(" eq ", 1)
                field = field.strip()
                value = value.strip().strip("'").strip('"')
                return str(record.get(field, "")) == value
            if " contains " in filter_expr:
                field, value = filter_expr.split(" contains ", 1)
                field = field.strip()
                value = value.strip().strip("'").strip('"')
                return value.lower() in str(record.get(field, "")).lower()
            if " startswith " in filter_expr:
                field, value = filter_expr.split(" startswith ", 1)
                field = field.strip()
                value = value.strip().strip("'").strip('"')
                return str(record.get(field, "")).startswith(value)
        except Exception:
            return False
        return True

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "data_source": "seed",
            "connected": True,
            "message": "Seed data source connected.",
            "details": {"data_dir": self.data_dir},
        }


def create_seed_repo(data_dir: str) -> SeedCTXRepository:
    return SeedCTXRepository(data_dir)
