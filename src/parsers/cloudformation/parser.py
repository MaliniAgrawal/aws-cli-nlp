from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "cloudformation"
INTENTS = ["create_cloudformation_stack", "list_cloudformation_stacks"]
EXAMPLES = [
    "create a cloudformation stack named mystack",
    "list cloudformation stacks",
]


class CloudFormationParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        if intent == "create_cloudformation_stack":
            stack = entities.get("stack", "mystack")
            cmd = f"aws cloudformation create-stack --stack-name {stack} --template-body file://template.yaml"
            return {
                "command": cmd,
                "explanation": f"Creates CloudFormation stack '{stack}' using local template.yaml.",
            }
        if intent == "list_cloudformation_stacks":
            return {
                "command": "aws cloudformation list-stacks",
                "explanation": "Lists CloudFormation stacks.",
            }
        return {
            "command": "echo 'Unsupported CloudFormation intent'",
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


_PARSER = CloudFormationParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
