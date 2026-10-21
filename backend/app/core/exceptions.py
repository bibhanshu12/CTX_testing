from typing import Any, Dict, Optional


class CTXError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        code: str = "ctx_error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class EntityNotAllowedError(CTXError):
    def __init__(self, entity_set: str) -> None:
        super().__init__(
            message=f"Entity set '{entity_set}' is not in the CTX allowlist.",
            status_code=403,
            code="entity_not_allowed",
            details={"entity_set": entity_set},
        )


class EntityNotFoundError(CTXError):
    def __init__(self, entity_set: str) -> None:
        super().__init__(
            message=f"Entity set '{entity_set}' not found.",
            status_code=404,
            code="entity_not_found",
            details={"entity_set": entity_set},
        )


class DataSourceError(CTXError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=502,
            code="data_source_error",
            details=details or {},
        )


class InvalidImportError(CTXError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=400,
            code="invalid_import",
        )
