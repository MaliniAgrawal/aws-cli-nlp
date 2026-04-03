from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "eks"
INTENTS = ["list_eks_clusters"]
EXAMPLES = ["list eks clusters in us-west-2"]


class EKSParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")

        if intent == "list_eks_clusters":
            cmd = "aws eks list-clusters"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Lists EKS clusters."}

        return {
            "command": "echo 'Unsupported EKS intent'",
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


_PARSER = EKSParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
