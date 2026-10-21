import httpx
from typing import Any, Dict, List, Optional

from app.core.allowlist import is_allowed_entity
from app.core.exceptions import (
    DataSourceError,
    EntityNotAllowedError,
    EntityNotFoundError,
)
from app.configuration.settings import settings
from app.persistence.base import CTXRepository


class ODataCTXRepository(CTXRepository):
    def __init__(self) -> None:
        self.base_url = settings.capm_odata_base_url.rstrip("/")
        self.username = settings.capm_odata_username
        self.password = settings.capm_odata_password

    def _headers(self) -> Dict[str, str]:
        return {"Accept": "application/json"}

    def _auth(self) -> Optional[tuple]:
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def _entity_url(self, entity_set: str) -> str:
        return f"{self.base_url}/{entity_set}"

    def list_entities(self) -> List[str]:
        return [e for e in self._discover_entities() if is_allowed_entity(e)]

    def _discover_entities(self) -> List[str]:
        try:
            with httpx.Client(
                auth=self._auth(), timeout=30.0, headers=self._headers()
            ) as client:
                resp = client.get(f"{self.base_url}/$metadata")
                resp.raise_for_status()
            text = resp.text
            import re

            found = re.findall(r'EntityType Name="([^"]+)"', text)
            return found
        except Exception:
            return []

    def get_metadata(self, entity_set: str) -> Dict[str, Any]:
        if not is_allowed_entity(entity_set):
            raise EntityNotAllowedError(entity_set)
        try:
            with httpx.Client(
                auth=self._auth(), timeout=30.0, headers=self._headers()
            ) as client:
                resp = client.get(f"{self.base_url}/$metadata")
                resp.raise_for_status()
        except Exception as exc:
            raise DataSourceError(
                f"Failed to fetch metadata from OData service: {exc}",
                details={"entity_set": entity_set},
            )
        return {
            "name": entity_set,
            "namespace": "com.ev.bdcDataCatalyst",
            "key": "",
            "columns": [],
            "raw_metadata_available": True,
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

        params: Dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        if skip is not None:
            params["$skip"] = skip
        if filter:
            params["$filter"] = filter
        if orderby:
            params["$orderby"] = orderby

        try:
            with httpx.Client(
                auth=self._auth(), timeout=60.0, headers=self._headers()
            ) as client:
                resp = client.get(
                    self._entity_url(entity_set), params=params
                )
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise DataSourceError(
                f"OData service returned HTTP {exc.response.status_code} for '{entity_set}'.",
                details={
                    "entity_set": entity_set,
                    "status_code": exc.response.status_code,
                    "body": exc.response.text[:500],
                },
            )
        except Exception as exc:
            raise DataSourceError(
                f"Failed to fetch records from OData service for '{entity_set}': {exc}",
                details={"entity_set": entity_set},
            )

        data = resp.json()
        value = data.get("value", []) if isinstance(data, dict) else []
        return {
            "entity_set": entity_set,
            "count": len(value),
            "value": value,
        }

    def get_connection_status(self) -> Dict[str, Any]:
        if not self.base_url:
            return {
                "data_source": "odata",
                "connected": False,
                "message": "CAPM_ODATA_BASE_URL is not configured.",
                "details": {"configured": False},
            }
        try:
            with httpx.Client(
                auth=self._auth(), timeout=20.0, headers=self._headers()
            ) as client:
                resp = client.get(f"{self.base_url}/$metadata")
                if resp.status_code == 200:
                    return {
                        "data_source": "odata",
                        "connected": True,
                        "message": "OData service reachable.",
                        "details": {"base_url": self.base_url},
                    }
                return {
                    "data_source": "odata",
                    "connected": False,
                    "message": f"OData service returned HTTP {resp.status_code}.",
                    "details": {"base_url": self.base_url, "status_code": resp.status_code},
                }
        except Exception as exc:
            return {
                "data_source": "odata",
                "connected": False,
                "message": f"OData service unreachable: {exc}",
                "details": {"base_url": self.base_url, "error": str(exc)},
            }


def create_odata_repo() -> ODataCTXRepository:
    return ODataCTXRepository()
