"""Test intent-based safety classification."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.aws_validator import (classify_intent_safety,
                                    validate_command_safe)

# Test cases
test_intents = [
    "list_s3_buckets",  # SAFE
    "create_s3_bucket",  # MUTATING
    "delete_s3_bucket",  # DESTRUCTIVE
    "create_iam_user",  # SECURITY_SENSITIVE
    "terminate_ec2_instance",  # DESTRUCTIVE
    "list_lambda_functions",  # SAFE
    "unknown_intent",  # UNKNOWN
]

print("\n=== Intent-Based Safety Classification Test ===\n")

for intent in test_intents:
    safety = classify_intent_safety(intent)
    validation = validate_command_safe(intent, {})

    print(f"Intent: {intent}")
    print(f"  Level: {safety['level']}")
    print(f"  Requires Confirmation: {safety['requires_confirmation']}")
    print(f"  Validation Status: {validation['status']}")
    print(f"  Reason: {validation['reason']}")
    print()

print("Done.\n")
