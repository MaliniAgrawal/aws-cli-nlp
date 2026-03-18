# src/pro/policy_schema.py

from typing import Dict, List, Literal, Optional, TypedDict  # noqa: F401

SafetyLevel = Literal["SAFE", "MUTATING", "SECURITY_SENSITIVE", "DESTRUCTIVE"]

Decision = Literal["allow", "confirm", "block"]


class PolicyRule(TypedDict, total=False):
    safety_level: SafetyLevel
    decision: Decision
    message: Optional[str]


class OrgPolicy(TypedDict):
    version: str
    rules: List[PolicyRule]
