from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "cloudwatch"
INTENTS = ["list_cloudwatch_metrics", "list_cloudwatch_logs"]
EXAMPLES = [
    "list cloudwatch metrics",
    "list cloudwatch log groups in us-west-2",
]


class CloudWatchParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")

        if intent == "list_cloudwatch_metrics":
            cmd = "aws cloudwatch list-metrics"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Lists CloudWatch metrics."}

        if intent == "list_cloudwatch_logs":
            cmd = "aws logs describe-log-groups"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Lists CloudWatch log groups."}

        return {
            "command": "echo 'Unsupported CloudWatch intent'",
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


_PARSER = CloudWatchParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
