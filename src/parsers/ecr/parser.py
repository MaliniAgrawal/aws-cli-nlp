from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "ecr"
INTENTS = ["list_ecr_repositories", "create_ecr_repository"]
EXAMPLES = [
    "list ecr repositories",
    "create an ecr repository named my-repo in us-west-2",
]


class ECRParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")

        if intent == "list_ecr_repositories":
            cmd = "aws ecr describe-repositories"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Lists ECR repositories."}

        if intent == "create_ecr_repository":
            repo = entities.get("repository", "my-repo")
            cmd = f"aws ecr create-repository --repository-name {repo}"
            if region:
                cmd += f" --region {region}"
            return {"command": cmd, "explanation": "Creates an ECR repo."}

        return {
            "command": "echo 'Unsupported ECR intent'",
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


_PARSER = ECRParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
