from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseParser(ABC):
    """Abstract base class for all AWS service parser plugins."""

    @abstractmethod
    def get_service_name(self) -> str:
        """Return canonical service name used by the registry."""

    @abstractmethod
    def get_intents(self) -> List[str]:
        """Return supported intent names for the service."""

    @abstractmethod
    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AWS CLI command payload for an intent and entities."""

    @abstractmethod
    def validate(
        self, intent: str, entities: Dict[str, Any], aws_session=None
    ) -> Dict[str, Any]:
        """Validate parsed intent/entities."""

    @abstractmethod
    def get_examples(self) -> List[str]:
        """Return representative natural language examples for this parser."""
