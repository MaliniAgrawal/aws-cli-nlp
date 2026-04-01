from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseParser(ABC):
    """Abstract base class for all service parsers."""

    @abstractmethod
    def get_service_name(self) -> str:
        """Return the unique service name used by the registry."""

    @abstractmethod
    def get_intents(self) -> List[str]:
        """Return intents supported by the parser."""

    @abstractmethod
    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        """Generate an AWS CLI command and explanation for an intent."""

    @abstractmethod
    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Validate the command or related resources for an intent."""

    @abstractmethod
    def get_examples(self) -> List[str]:
        """Return example natural-language prompts supported by the parser."""

    def to_service_dict(self) -> Dict[str, Any]:
        """Compatibility adapter for existing function-based registry consumers."""
        return {
            "name": self.get_service_name(),
            "intents": self.get_intents(),
            "generate_command": self.generate_command,
            "validate": self.validate,
            "examples": self.get_examples(),
            "parser": self,
        }
