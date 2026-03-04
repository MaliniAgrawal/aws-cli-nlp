# src/pro/enforcement.py

from typing import Optional, Dict, Any
from .policy_schema import OrgPolicy

def evaluate_policy(
    policy: Optional[OrgPolicy],
    safety_level: str
) -> Dict[str, Any]:
    """
    Returns enforcement recommendation.
    Does NOT block or execute.
    """

    if not policy:
        return {
            "enabled": False,
            "decision": "allow",
            "reason": "No org policy present"
        }

    for rule in policy.get("rules", []):
        if rule.get("safety_level") == safety_level:
            return {
                "enabled": True,
                "decision": rule.get("decision", "allow"),
                "reason": rule.get("message", "Policy rule matched")
            }

    return {
        "enabled": True,
        "decision": "allow",
        "reason": "No matching rule"
    }
