from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "secretsmanager"
INTENTS = ["get_secret", "create_secret"]
EXAMPLES = [
    "get secret my/secret",
    "create a secret named mysecret",
]


class SecretsManagerParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        if intent == "get_secret":
            secret = entities.get("secret_id", "my/secret")
            cmd = f"aws secretsmanager get-secret-value --secret-id {secret}"
            return {"command": cmd, "explanation": "Retrieves a secret."}

        if intent == "create_secret":
            name = entities.get("secret_name", "mysecret")
            cmd = f"aws secretsmanager create-secret --name {name} --secret-string file://secret.json"
            return {
                "command": cmd,
                "explanation": "Creates a new secret from file://secret.json (never hardcode secrets).",
            }

        return {
            "command": "echo 'Unsupported SecretsManager intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        return {"status": "valid"}

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = SecretsManagerParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
