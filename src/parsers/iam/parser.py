from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "iam"
INTENTS = [
    "list_iam_users",
    "create_iam_user",
    "delete_iam_user",
    "list_iam_roles",
    "attach_user_policy",
    "detach_user_policy",
    "list_attached_user_policies",
]
EXAMPLES = [
    "list iam users",
    "create iam user alice",
    "attach ReadOnlyAccess to user alice",
]

AWS_MANAGED_POLICIES = {
    "ReadOnlyAccess": "arn:aws:iam::aws:policy/ReadOnlyAccess",
    "AdministratorAccess": "arn:aws:iam::aws:policy/AdministratorAccess",
    "PowerUserAccess": "arn:aws:iam::aws:policy/PowerUserAccess",
}


def _resolve_policy(policy: str) -> str:
    if policy.startswith("arn:aws:iam"):
        return policy
    if policy in AWS_MANAGED_POLICIES:
        return AWS_MANAGED_POLICIES[policy]
    raise ValueError("Only AWS-managed policy names are supported without ARN")


class IAMParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        if intent == "list_iam_users":
            return {
                "command": "aws iam list-users",
                "explanation": "Lists IAM users in the account.",
            }

        if intent == "create_iam_user":
            user = entities["user"]
            return {
                "command": f"aws iam create-user --user-name {user}",
                "explanation": f"Creates IAM user '{user}'.",
            }

        if intent == "delete_iam_user":
            user = entities["user"]
            return {
                "command": f"aws iam delete-user --user-name {user}",
                "explanation": f"Deletes IAM user '{user}'.",
            }

        if intent == "list_iam_roles":
            return {
                "command": "aws iam list-roles",
                "explanation": "Lists IAM roles in the account.",
            }

        if intent == "attach_user_policy":
            user = entities["user"]
            policy = _resolve_policy(entities["policy"])
            return {
                "command": f"aws iam attach-user-policy --user-name {user} --policy-arn {policy}",
                "explanation": f"Attaches policy to IAM user '{user}'.",
            }

        if intent == "detach_user_policy":
            user = entities["user"]
            policy = _resolve_policy(entities["policy"])
            return {
                "command": f"aws iam detach-user-policy --user-name {user} --policy-arn {policy}",
                "explanation": f"Detaches policy from IAM user '{user}'.",
            }

        if intent == "list_attached_user_policies":
            user = entities["user"]
            return {
                "command": f"aws iam list-attached-user-policies --user-name {user}",
                "explanation": f"Lists attached policies for IAM user '{user}'.",
            }

        return {
            "command": "echo 'Unsupported IAM intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "unknown",
            "reason": "Validation disabled by env",
        }

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = IAMParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
