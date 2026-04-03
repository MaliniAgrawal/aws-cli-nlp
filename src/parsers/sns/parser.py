from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "sns"
INTENTS = ["create_sns_topic", "list_sns_topics"]
EXAMPLES = [
    "create sns topic test-topic",
    "list sns topics",
]


class SNSParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        if intent == "create_sns_topic":
            topic = entities.get("topic", "my-topic")
            return {
                "command": f"aws sns create-topic --name {topic}",
                "explanation": f"Creates SNS topic '{topic}'.",
            }
        if intent == "list_sns_topics":
            return {
                "command": "aws sns list-topics",
                "explanation": "Lists SNS topics.",
            }
        return {
            "command": "echo 'Unsupported SNS intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        return {"status": "unknown", "reason": "validation not implemented"}

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = SNSParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
