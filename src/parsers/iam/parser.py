# src/parsers/iam/parser.py

from typing import Dict

SERVICE_NAME = "iam"

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


def generate_command(intent: str, entities: Dict) -> Dict:
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

    raise ValueError(f"Unsupported IAM intent: {intent}")


def validate(_command: str) -> Dict:
    return {
        "status": "unknown",
        "reason": "Validation disabled by env",
    }


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": [
            "list_iam_users",
            "create_iam_user",
            "delete_iam_user",
            "list_iam_roles",
            "attach_user_policy",
            "detach_user_policy",
            "list_attached_user_policies",
        ],
        "generate_command": generate_command,
        "validate": validate,
    }
