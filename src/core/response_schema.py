# src/core/response_schema.py
"""
Frozen response schema for Phase B.1
All interfaces (MCP, HTTP, CLI) MUST return this exact structure.
"""

from typing import Any, Dict

VERSION = "1.0.0"


def _get_confirmation_hint(level: str) -> str:
    """Get confirmation hint based on safety level."""
    if level == "DESTRUCTIVE":
        return "Review carefully before running in production."
    elif level == "MUTATING" or level == "SECURITY_SENSITIVE":
        return "Review before running in production."
    elif level == "SAFE":
        return "This is a read-only operation."
    return "Verify the command before execution."


def build_standard_response(
    command: str,
    explanation: str,
    intent: str,
    entities: Dict[str, Any],
    validation: Dict[str, str],
    service: str = "unknown",
    confidence: str = "high",
    generated_by: str = "rule_engine",
) -> Dict[str, Any]:
    """
    Build the standard frozen response schema with MCP metadata.
    This structure is guaranteed across all interfaces (MCP, HTTP, CLI).

    Phase B.2 Requirements:
    - Stateless: No state stored between requests
    - No credentials: Never reads or stores AWS credentials
    - No execution: Only generates commands, never executes
    - Deterministic: Same input always produces same output

    Returns:
        {
            "command": str,
            "explanation": str,
            "intent": str,
            "entities": dict,
            "safety": {
                "level": str,
                "requires_confirmation": bool,
                "confirmation_hint": str
            },
            "meta": {
                "service": str,
                "confidence": str,
                "generated_by": str,
                "version": str
            }
        }
    """
    # Extract safety level from validation
    safety_level = validation.get("safety_level", "UNKNOWN")
    requires_confirmation = validation.get("requires_confirmation", False)

    return {
        "command": command,
        "explanation": explanation,
        "intent": intent,
        "entities": entities,
        "safety": {
            "level": safety_level,
            "requires_confirmation": requires_confirmation,
            "confirmation_hint": _get_confirmation_hint(safety_level),
        },
        "meta": {
            "service": service,
            "confidence": confidence,
            "generated_by": generated_by,
            "version": VERSION,
        },
    }
