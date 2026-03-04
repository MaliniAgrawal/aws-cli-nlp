# src/parsers/ec2/parser.py
"""
EC2 parser plugin for MCP AWS CLI Generator (Track-1).
Interface expected by registry:
- SERVICE_NAME (str)
- get_service() -> dict with 'name' and 'intents' mapping
"""

import re
import json
import os
from pathlib import Path
from typing import Tuple, Dict, Any

SERVICE_NAME = "ec2"

# Intents supported by this parser
INTENTS = [
    "list_ec2_instances",
    "start_ec2_instance",
    "stop_ec2_instance",
    "terminate_ec2_instance",
    "describe_instance_types",
    "create_ec2_keypair",
    "list_ec2_keypairs",
]


# --- Helpers: light-weight rule extraction -----------------------------------
_REGION_RE = re.compile(r"\b([a-z]{2}-[a-z]+-\d)\b", re.I)
_INSTANCE_ID_RE = re.compile(r"\b(i-[0-9a-f]{8,17})\b", re.I)
_KEY_NAME_RE_1 = re.compile(r"(?:keypair|key pair|key-pair)\s+named?\s+([A-Za-z0-9_\-\.]+)", re.I)
_KEY_NAME_RE_2 = re.compile(r"(?:keypair|key pair|key-pair)\s+([A-Za-z0-9_\-\.]+)", re.I)


def _extract_region(text: str) -> str | None:
    m = _REGION_RE.search(text)
    return m.group(1) if m else None


def _extract_instance_ids(text: str) -> list[str]:
    return _INSTANCE_ID_RE.findall(text)


def _extract_key_name(text: str) -> str | None:
    m = _KEY_NAME_RE_1.search(text) or _KEY_NAME_RE_2.search(text)
    return m.group(1) if m else None


def _make_region_flag(region: str | None) -> str:
    return f" --region {region}" if region else ""


def _safe_validation_stub(intent: str, entities: Dict[str, Any]) -> Dict[str, str]:
    """
    Try to import aws_validator if available and run validation.
    If not available or disabled, return unknown status.
    """
    try:
        from src.core.aws_validator import validate_intent  # type: ignore
    except Exception:
        return {"status": "unknown", "reason": "validation-disabled-or-missing"}
    try:
        return validate_intent(intent, entities)
    except Exception:
        return {"status": "unknown", "reason": "validation-error"}


# --- Intent handlers ---------------------------------------------------------
def list_ec2_instances_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    cmd = "aws ec2 describe-instances" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Describes EC2 instances{(' in ' + region) if region else ''}.",
        "intent": "list_ec2_instances",
        "entities": {"region": region} if region else {},
        "validation": _safe_validation_stub("list_ec2_instances", {"region": region}),
    }


def start_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    if not ids:
        return {
            "command": "echo 'Specify one or more instance IDs (i-...) to start.'",
            "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
            "intent": "start_ec2_instance",
            "entities": {},
            "validation": {"status": "unknown", "reason": "missing_instance_id"},
        }
    cmd = f"aws ec2 start-instances --instance-ids {' '.join(ids)}" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Starts EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
        "intent": "start_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("start_ec2_instance", {"instance_ids": ids, "region": region}),
    }


def stop_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    if not ids:
        return {
            "command": "echo 'Specify one or more instance IDs (i-...) to stop.'",
            "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
            "intent": "stop_ec2_instance",
            "entities": {},
            "validation": {"status": "unknown", "reason": "missing_instance_id"},
        }
    cmd = f"aws ec2 stop-instances --instance-ids {' '.join(ids)}" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Stops EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
        "intent": "stop_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("stop_ec2_instance", {"instance_ids": ids, "region": region}),
    }


def terminate_ec2_instance_handler(_args: dict, text: str) -> dict:
    ids = _extract_instance_ids(text)
    region = _extract_region(text)
    if not ids:
        return {
            "command": "echo 'Specify one or more instance IDs (i-...) to terminate.'",
            "explanation": "Missing instance IDs. Provide at least one instance ID (i-...).",
            "intent": "terminate_ec2_instance",
            "entities": {},
            "validation": {"status": "unknown", "reason": "missing_instance_id"},
        }
    cmd = f"aws ec2 terminate-instances --instance-ids {' '.join(ids)}" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Terminates EC2 instance(s) {', '.join(ids)}{(' in ' + region) if region else ''}.",
        "intent": "terminate_ec2_instance",
        "entities": {"instance_ids": ids, "region": region},
        "validation": _safe_validation_stub("terminate_ec2_instance", {"instance_ids": ids, "region": region}),
    }


def describe_instance_types_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    cmd = "aws ec2 describe-instance-types" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Lists EC2 instance types{(' in ' + region) if region else ''}.",
        "intent": "describe_instance_types",
        "entities": {"region": region} if region else {},
        "validation": _safe_validation_stub("describe_instance_types", {"region": region}),
    }


def create_ec2_keypair_handler(_args: dict, text: str) -> dict:
    key = _extract_key_name(text) or "my-key"
    # Create keypair command writes key material to stdout; redirect to a file in examples.
    cmd = (
        f"aws ec2 create-key-pair --key-name {key} --query 'KeyMaterial' --output text > {key}.pem"
    )
    return {
        "command": cmd,
        "explanation": f"Creates an EC2 key pair named '{key}' and saves the PEM to {key}.pem.",
        "intent": "create_ec2_keypair",
        "entities": {"key_name": key},
        "validation": _safe_validation_stub("create_ec2_keypair", {"key_name": key}),
    }


def list_ec2_keypairs_handler(_args: dict, text: str) -> dict:
    region = _extract_region(text)
    cmd = "aws ec2 describe-key-pairs" + _make_region_flag(region)
    return {
        "command": cmd,
        "explanation": f"Lists EC2 key pairs{(' in ' + region) if region else ''}.",
        "intent": "list_ec2_keypairs",
        "entities": {"region": region} if region else {},
        "validation": _safe_validation_stub("list_ec2_keypairs", {"region": region}),
    }


# Intent handler mapping
INTENT_HANDLERS = {
    "list_ec2_instances": list_ec2_instances_handler,
    "start_ec2_instance": start_ec2_instance_handler,
    "stop_ec2_instance": stop_ec2_instance_handler,
    "terminate_ec2_instance": terminate_ec2_instance_handler,
    "describe_instance_types": describe_instance_types_handler,
    "create_ec2_keypair": create_ec2_keypair_handler,
    "list_ec2_keypairs": list_ec2_keypairs_handler,
}

def generate_command(intent, entities):
    """Registry-compatible command generator interface."""
    if intent in INTENT_HANDLERS:
        handler = INTENT_HANDLERS[intent]
        # Reconstruct text with region for handlers that extract from text
        text = ""
        if entities.get("region"):
            text += f" in {entities['region']}"
        if entities.get("instance_ids"):
            text += f" {' '.join(entities['instance_ids'])}"
        if entities.get("key_name"):
            text += f" {entities['key_name']}"
        
        result = handler(entities, text)
        return {"command": result["command"], "explanation": result["explanation"]}
    return {"command": "echo 'Unknown EC2 intent'", "explanation": "Intent not supported"}

def validate(intent, entities, aws_session=None):
    """Registry-compatible validation interface."""
    return _safe_validation_stub(intent, entities)

# --- Registry / plugin interface --------------------------------------------
def get_service() -> dict:
    """
    Return a dictionary describing the service for registry.autodiscover().
    Expected shape (lightweight):
    {
        "name": "ec2",
        "intents": ["list_ec2_instances", ...],
        "generate_command": generate_command_fn,
        "validate": validate_fn
    }
    """
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate
    }
