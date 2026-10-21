from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CTXRepository(ABC):
    @abstractmethod
    def list_entities(self) -> List[str]:
        ...

    @abstractmethod
    def get_metadata(self, entity_set: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_records(
        self,
        entity_set: str,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter: Optional[str] = None,
        orderby: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_connection_status(self) -> Dict[str, Any]:
        ...
