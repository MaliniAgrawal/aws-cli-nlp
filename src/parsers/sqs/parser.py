from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "sqs"
INTENTS = ["create_sqs_queue", "list_sqs_queues"]
EXAMPLES = [
    "create sqs queue test-queue",
    "list sqs queues",
]


class SQSParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        if intent == "create_sqs_queue":
            queue = entities.get("queue", "my-queue")
            return {
                "command": f"aws sqs create-queue --queue-name {queue}",
                "explanation": f"Creates SQS queue '{queue}'.",
            }
        if intent == "list_sqs_queues":
            return {"command": "aws sqs list-queues", "explanation": "Lists SQS queues."}
        return {
            "command": "echo 'Unsupported SQS intent'",
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


_PARSER = SQSParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
