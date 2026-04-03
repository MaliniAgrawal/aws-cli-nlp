from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "ssm"
INTENTS = ["get_ssm_parameter", "put_ssm_parameter"]
EXAMPLES = [
    "get ssm parameter /my/parameter in us-west-2",
    "put ssm parameter /my/parameter",
]


class SSMParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")

        if intent == "get_ssm_parameter":
            name = entities.get("name", "/my/parameter")
            cmd = f"aws ssm get-parameter --name {name} --with-decryption"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Gets an SSM Parameter."}

        if intent == "put_ssm_parameter":
            name = entities.get("name", "/my/parameter")
            value = entities.get("value", "default")
            cmd = f'aws ssm put-parameter --name {name} --value "{value}" --type SecureString --overwrite'
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Stores a SecureString parameter."}

        return {
            "command": "echo 'Unsupported SSM intent'",
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


_PARSER = SSMParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
