from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "lambda"
INTENTS = ["list_lambda_functions", "invoke_lambda_function"]
EXAMPLES = [
    "list lambda functions in us-west-1",
    "invoke lambda function test-func in us-east-1",
]


class LambdaParser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")
        if intent == "list_lambda_functions":
            cmd = "aws lambda list-functions"
            if region:
                cmd += f" --region {region}"
            return {
                "command": cmd,
                "explanation": f"Lists Lambda functions{' in ' + region if region else ''}.",
            }
        if intent == "invoke_lambda_function":
            fn = entities.get("function", "my-function")
            cmd = f"aws lambda invoke --function-name {fn} /tmp/output.json"
            if region:
                cmd += f" --region {region}"
            return {
                "command": cmd,
                "explanation": f"Invokes Lambda function '{fn}' (result to /tmp/output.json).",
            }
        return {
            "command": "echo 'Unsupported Lambda intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        return {"status": "unknown", "reason": "no validation by default"}

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = LambdaParser()


def generate_command(intent, entities):
    return _PARSER.generate_command(intent, entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
