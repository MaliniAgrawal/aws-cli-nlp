from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.core.base_parser import BaseParser

SERVICE_NAME = "ec2"
INTENTS = [
    "list_ec2_instances",
    "start_ec2_instance",
    "stop_ec2_instance",
    "terminate_ec2_instance",
    "describe_instance_types",
    "create_ec2_keypair",
    "list_ec2_keypairs",
]
EXAMPLES = [
    "list ec2 instances in us-west-2",
    "start instance i-0123456789abcdef0",
    "create keypair named my-key",
]

_REGION_RE = re.compile(r"\b([a-z]{2}-[a-z]+-\d)\b", re.I)
_INSTANCE_ID_RE = re.compile(r"\b(i-[0-9a-f]{8,17})\b", re.I)
_KEY_NAME_RE_1 = re.compile(
    r"(?:keypair|key pair|key-pair)\s+named?\s+([A-Za-z0-9_\-\.]+)", re.I
)
_KEY_NAME_RE_2 = re.compile(
    r"(?:keypair|key pair|key-pair)\s+([A-Za-z0-9_\-\.]+)", re.I
)


def _extract_region(text: str) -> str | None:
    match = _REGION_RE.search(text)
    return match.group(1) if match else None


def _extract_instance_ids(text: str) -> List[str]:
    return _INSTANCE_ID_RE.findall(text)


def _extract_key_name(text: str) -> str | None:
    match = _KEY_NAME_RE_1.search(text) or _KEY_NAME_RE_2.search(text)
    return match.group(1) if match else None


def _make_region_flag(region: str | None) -> str:
    return f" --region {region}" if region else ""


def _safe_validation_stub(intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
    try:
        from src.core.aws_validator import validate_intent  # type: ignore
    except Exception:
        return {"status": "unknown", "reason": "validation-disabled-or-missing"}
    try:
        return validate_intent(intent, entities)
    except Exception:
        return {"status": "unknown", "reason": "validation-error"}


class EC2Parser(BaseParser):
    def get_service_name(self) -> str:
        return SERVICE_NAME

    def get_intents(self) -> List[str]:
        return INTENTS

    def generate_command(self, intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
        region = entities.get("region")

        if intent == "list_ec2_instances":
            cmd = "aws ec2 describe-instances" + _make_region_flag(region)
            return {
                "command": cmd,
                "explanation": f"Describes EC2 instances{(' in ' + region) if region else ''}.",
            }

        if intent == "start_ec2_instance":
            ids = entities.get("instance_ids", [])
            if not ids:
                return {
                    "command": "echo 'Specify one or more instance IDs (i-...) to start.'",
                    "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
                }
            cmd = f"aws ec2 start-instances --instance-ids {' '.join(ids)}" + _make_region_flag(
                region
            )
            return {
                "command": cmd,
                "explanation": f"Starts EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
            }

        if intent == "stop_ec2_instance":
            ids = entities.get("instance_ids", [])
            if not ids:
                return {
                    "command": "echo 'Specify one or more instance IDs (i-...) to stop.'",
                    "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
                }
            cmd = f"aws ec2 stop-instances --instance-ids {' '.join(ids)}" + _make_region_flag(
                region
            )
            return {
                "command": cmd,
                "explanation": f"Stops EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
            }

        if intent == "terminate_ec2_instance":
            ids = entities.get("instance_ids", [])
            if not ids:
                return {
                    "command": "echo 'Specify one or more instance IDs (i-...) to terminate.'",
                    "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
                }
            cmd = f"aws ec2 terminate-instances --instance-ids {' '.join(ids)}" + _make_region_flag(
                region
            )
            return {
                "command": cmd,
                "explanation": f"Terminates EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
            }

        if intent == "describe_instance_types":
            cmd = "aws ec2 describe-instance-types" + _make_region_flag(region)
            return {
                "command": cmd,
                "explanation": f"Lists EC2 instance types{(' in ' + region) if region else ''}.",
            }

        if intent == "create_ec2_keypair":
            key = entities.get("key_name", "my-key")
            cmd = f"aws ec2 create-key-pair --key-name {key} --query 'KeyMaterial' --output text > {key}.pem"
            return {
                "command": cmd,
                "explanation": f"Creates an EC2 key pair named '{key}' and saves the PEM to {key}.pem.",
            }

        if intent == "list_ec2_keypairs":
            cmd = "aws ec2 describe-key-pairs" + _make_region_flag(region)
            return {
                "command": cmd,
                "explanation": f"Lists EC2 key pairs{(' in ' + region) if region else ''}.",
            }

        return {
            "command": "echo 'Unknown EC2 intent'",
            "explanation": "Intent not supported",
        }

    def validate(
        self,
        intent: str,
        entities: Dict[str, Any],
        aws_session: Optional[Any] = None,
    ) -> Dict[str, Any]:
        return _safe_validation_stub(intent, entities)

    def get_examples(self) -> List[str]:
        return EXAMPLES


_PARSER = EC2Parser()


def list_ec2_instances_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    entities = {"region": region} if region else {}
    result = _PARSER.generate_command("list_ec2_instances", entities)
    return {
        **result,
        "intent": "list_ec2_instances",
        "entities": entities,
        "validation": _safe_validation_stub("list_ec2_instances", entities),
    }


def start_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    entities = {"instance_ids": ids, "region": region}
    result = _PARSER.generate_command("start_ec2_instance", entities)
    return {
        **result,
        "intent": "start_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("start_ec2_instance", entities)
        if ids
        else {"status": "unknown", "reason": "missing_instance_id"},
    }


def stop_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    entities = {"instance_ids": ids, "region": region}
    result = _PARSER.generate_command("stop_ec2_instance", entities)
    return {
        **result,
        "intent": "stop_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("stop_ec2_instance", entities)
        if ids
        else {"status": "unknown", "reason": "missing_instance_id"},
    }


def terminate_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    entities = {"instance_ids": ids, "region": region}
    result = _PARSER.generate_command("terminate_ec2_instance", entities)
    return {
        **result,
        "intent": "terminate_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("terminate_ec2_instance", entities)
        if ids
        else {"status": "unknown", "reason": "missing_instance_id"},
    }


def describe_instance_types_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    entities = {"region": region} if region else {}
    result = _PARSER.generate_command("describe_instance_types", entities)
    return {
        **result,
        "intent": "describe_instance_types",
        "entities": entities,
        "validation": _safe_validation_stub("describe_instance_types", entities),
    }


def create_ec2_keypair_handler(_args: dict, text: str) -> dict:
    key = _extract_key_name(text) or "my-key"
    entities = {"key_name": key}
    result = _PARSER.generate_command("create_ec2_keypair", entities)
    return {
        **result,
        "intent": "create_ec2_keypair",
        "entities": entities,
        "validation": _safe_validation_stub("create_ec2_keypair", entities),
    }


def list_ec2_keypairs_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    entities = {"region": region} if region else {}
    result = _PARSER.generate_command("list_ec2_keypairs", entities)
    return {
        **result,
        "intent": "list_ec2_keypairs",
        "entities": entities,
        "validation": _safe_validation_stub("list_ec2_keypairs", entities),
    }


def generate_command(intent, entities):
    normalized_entities = dict(entities)
    if intent in {"start_ec2_instance", "stop_ec2_instance", "terminate_ec2_instance"}:
        ids = normalized_entities.get("instance_ids")
        if isinstance(ids, str):
            normalized_entities["instance_ids"] = [ids]
        elif not ids:
            text = normalized_entities.get("text", "")
            normalized_entities["instance_ids"] = _extract_instance_ids(text)
    if intent == "create_ec2_keypair" and not normalized_entities.get("key_name"):
        text = normalized_entities.get("text", "")
        normalized_entities["key_name"] = _extract_key_name(text) or "my-key"
    if not normalized_entities.get("region"):
        text = normalized_entities.get("text", "")
        normalized_entities["region"] = _extract_region(text)
    return _PARSER.generate_command(intent, normalized_entities)


def validate(intent, entities, aws_session=None):
    return _PARSER.validate(intent, entities, aws_session=aws_session)


def get_service():
    return _PARSER.to_service_dict()
