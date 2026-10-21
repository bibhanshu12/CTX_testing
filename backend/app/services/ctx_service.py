from typing import Any, Dict, List, Optional

from app.configuration.settings import settings
from app.core.allowlist import is_allowed_entity
from app.core.exceptions import (
    DataSourceError,
    EntityNotAllowedError,
    EntityNotFoundError,
)
from app.domain.entities import CTX_METADATA, get_entity_metadata, get_columns, list_entities
from app.persistence.base import CTXRepository
from app.persistence.seed_repo import create_seed_repo
from app.services.odata_service import create_odata_repo


class CTXService:
    def __init__(self) -> None:
        self.data_source = settings.ctx_data_source
        self._repo: Optional[CTXRepository] = None

    def _get_repo(self) -> CTXRepository:
        if self._repo is None:
            if self.data_source == "odata":
                self._repo = create_odata_repo()
            else:
                self._repo = create_seed_repo(settings.seed_data_dir)
        return self._repo

    def list_entities(self) -> List[str]:
        return self._get_repo().list_entities()

    def get_metadata(self, entity_set: str) -> Dict[str, Any]:
        if not is_allowed_entity(entity_set):
            raise EntityNotAllowedError(entity_set)
        if entity_set not in CTX_METADATA:
            raise EntityNotFoundError(entity_set)
        try:
            repo_meta = self._get_repo().get_metadata(entity_set)
        except EntityNotAllowedError:
            raise
        except EntityNotFoundError:
            raise
        except Exception as exc:
            raise DataSourceError(
                f"Failed to retrieve metadata for '{entity_set}': {exc}",
                details={"entity_set": entity_set, "data_source": self.data_source},
            )
        static_meta = get_entity_metadata(entity_set)
        return {
            "name": entity_set,
            "namespace": static_meta["namespace"],
            "key": static_meta["key"],
            "columns": get_columns(entity_set),
            "source": repo_meta,
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
        try:
            return self._get_repo().get_records(
                entity_set=entity_set,
                top=top,
                skip=skip,
                filter=filter,
                orderby=orderby,
            )
        except (EntityNotAllowedError, EntityNotFoundError, DataSourceError):
            raise
        except Exception as exc:
            raise DataSourceError(
                f"Failed to retrieve records for '{entity_set}': {exc}",
                details={"entity_set": entity_set, "data_source": self.data_source},
            )

    def get_connection_status(self) -> Dict[str, Any]:
        try:
            return self._get_repo().get_connection_status()
        except Exception as exc:
            return {
                "data_source": self.data_source,
                "connected": False,
                "message": f"Connection check failed: {exc}",
                "details": {"error": str(exc)},
            }

    def validate_import_metadata(self, content: str) -> Dict[str, Any]:
        import re

        found = re.findall(r'EntityType Name="([^"]+)"', content)
        ctx_found = [e for e in found if e in CTX_METADATA]
        non_ctx = [e for e in found if e not in CTX_METADATA and e.startswith("CTX_")]
        valid = bool(found)
        return {
            "valid": valid,
            "entity_sets_found": found,
            "ctx_entities_found": ctx_found,
            "additional_ctx_discovered": non_ctx,
            "message": (
                f"Found {len(found)} entity set(s); {len(ctx_found)} are approved CTX entities."
                if valid
                else "No entity sets found in the provided content."
            ),
        }


ctx_service = CTXService()
