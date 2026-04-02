from __future__ import annotations

from typing import Any, Dict, List

from src.core import aws_validator
from src.core.base_parser import BaseParser

SERVICE = "s3"
SERVICE_NAME = "s3"
INTENTS = [
    "create_s3_bucket",
    "list_s3_buckets",
    "delete_s3_bucket",
    "list_s3_objects",
    "put_s3_object",
]

EXAMPLES = [
    "create a new S3 bucket called my-new-data-lake in eu-central-1",
    "list s3 buckets",
    "delete bucket old-data-bucket",
    "list objects in the bucket my-files",
    "upload the file image.jpg to the bucket multimedia under the key photos/image.jpg",
]


class S3Parser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def get_examples(self) -> List[str]:
        return EXAMPLES

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        if intent == "create_s3_bucket":
            bucket = entities.get("bucket", "my-bucket")
            region = entities.get("region")
            if region:
                cmd = f"aws s3 mb s3://{bucket} --region {region}"
            else:
                cmd = f"aws s3 mb s3://{bucket}"
            return {
                "command": cmd,
                "explanation": f"Creates an S3 bucket named '{bucket}'{' in ' + region if region else ''}.",
            }

        if intent == "list_s3_buckets":
            return {
                "command": "aws s3 ls",
                "explanation": "Lists S3 buckets in your account (global).",
            }

        if intent == "delete_s3_bucket":
            bucket = entities.get("bucket", "my-bucket")
            cmd = f"aws s3 rb s3://{bucket} --force"
            return {
                "command": cmd,
                "explanation": f"Deletes S3 bucket '{bucket}' and all its contents (force).",
            }

        if intent == "list_s3_objects":
            bucket = entities.get("bucket", "my-bucket")
            prefix = entities.get("prefix")
            if prefix:
                cmd = f"aws s3 ls s3://{bucket}/{prefix} --recursive"
                return {
                    "command": cmd,
                    "explanation": f"Lists objects under '{prefix}' in bucket '{bucket}'.",
                }

            cmd = f"aws s3 ls s3://{bucket}"
            return {
                "command": cmd,
                "explanation": f"Lists objects in bucket '{bucket}'.",
            }

        if intent == "put_s3_object":
            bucket = entities.get("bucket", "my-bucket")
            key = entities.get("key", "upload.dat")
            local_path = entities.get("local_path", "./file")
            cmd = f"aws s3 cp {local_path} s3://{bucket}/{key}"
            return {
                "command": cmd,
                "explanation": f"Uploads local file '{local_path}' to s3://{bucket}/{key}.",
            }

        return {
            "command": "echo 'Unknown S3 intent'",
            "explanation": "Intent not supported",
        }

    def validate(self, intent: str, entities: Dict[str, Any], aws_session=None) -> Dict[str, Any]:
        if intent == "create_s3_bucket":
            bucket = entities.get("bucket", "")
            return aws_validator.check_s3_bucket_exists(bucket, aws_session=aws_session)
        if intent == "list_s3_buckets":
            return aws_validator.list_s3_buckets(aws_session=aws_session)
        return {"status": "unknown", "reason": "no validation for that intent"}


_PARSER = S3Parser()


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
