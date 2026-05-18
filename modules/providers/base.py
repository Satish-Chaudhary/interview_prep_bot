from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        ...

    @abstractmethod
    def generate_json(self, prompt: str, schema: Optional[dict] = None, **kwargs) -> Optional[dict[str, Any]]:
        ...
