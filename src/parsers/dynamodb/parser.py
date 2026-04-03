from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core import aws_validator
from src.core.base_parser import BaseParser

SERVICE_NAME = "dynamodb"
INTENTS = ["create_dynamodb_table", "list_dynamodb_tables"]
EXAMPLES = [
    "create a dynamodb table named Orders",
    "list dynamodb tables in us-west-2",
]


class DynamoDBParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region_flag = (
            f" --region {entities['region']}" if entities.get("region") else ""
        )

        if intent == "create_dynamodb_table":
            table = entities.get("table", "MyTable")
            cmd = f"aws dynamodb create-table --table-name {table} --attribute-definitions AttributeName=Id,AttributeType=S --key-schema AttributeName=Id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5{region_flag}"
            return {
                "command": cmd,
                "explanation": f"Creates DynamoDB table '{table}' with a simple string primary key 'Id'.",
            }
        if intent == "list_dynamodb_tables":
            return {
                "command": f"aws dynamodb list-tables{region_flag}",
                "explanation": "Lists DynamoDB tables.",
            }
        return {
            "command": "echo 'Unsupported DynamoDB intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if intent == "list_dynamodb_tables":
            return aws_validator.list_dynamodb_tables(aws_session=aws_session)
        return {
            "status": "unknown",
            "reason": "validation not implemented for create_dynamodb_table",
        }

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = DynamoDBParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
