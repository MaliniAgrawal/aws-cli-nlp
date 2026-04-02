from __future__ import annotations

from typing import Any, Dict, List

from src.core.base_parser import BaseParser

SERVICE_NAME = "rds"
INTENTS = ["create_rds_instance", "list_rds_instances", "delete_rds_instance"]
EXAMPLES = [
    "create rds instance mydb",
    "list rds instances",
    "delete rds instance old-db",
]


class RDSParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def get_examples(self) -> List[str]:
        return EXAMPLES

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        if intent == "create_rds_instance":
            db = entities.get("db", "mydb")
            cmd = (
                "aws rds create-db-instance "
                f"--db-instance-identifier {db} "
                "--db-instance-class db.t3.micro "
                "--engine mysql "
                "--allocated-storage 20 "
                "--master-username admin "
                "--manage-master-user-password"
            )
            return {
                "command": cmd,
                "explanation": f"Creates RDS instance '{db}' with AWS-managed master password (stored in Secrets Manager).",
            }
        if intent == "list_rds_instances":
            return {
                "command": "aws rds describe-db-instances",
                "explanation": "Lists RDS DB instances.",
            }
        if intent == "delete_rds_instance":
            db = entities.get("db")
            if not db:
                return {
                    "command": "echo 'Missing DB instance identifier'",
                    "explanation": "Cannot delete an RDS instance without a DB identifier.",
                }
            cmd = f"aws rds delete-db-instance --db-instance-identifier {db} --skip-final-snapshot"
            return {
                "command": cmd,
                "explanation": f"Deletes RDS instance '{db}' without taking a final snapshot.",
            }

        return {
            "command": "echo 'Unknown RDS intent'",
            "explanation": "Intent not supported",
        }

    def validate(self, intent: str, entities: Dict[str, Any], aws_session=None) -> Dict[str, Any]:
        return {"status": "unknown", "reason": "validation not implemented"}


_PARSER = RDSParser()


def get_parser() -> BaseParser:
    return _PARSER


# Backward-compatible function-based API

def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return {
        "name": _PARSER.get_service_name(),
        "intents": _PARSER.get_intents(),
        "generate_command": generate_command,
        "validate": validate,
        "examples": _PARSER.get_examples(),
        "parser": _PARSER,
    }
