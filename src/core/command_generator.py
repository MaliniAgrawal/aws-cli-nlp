import os
import logging
from src.core import nlp_utils
from src.core.registry import registry
from src.core.aws_validator import validate_command_safe
from src.core.response_schema import build_standard_response

logger = logging.getLogger(__name__)

def _attach_pro_enforcement(result: dict) -> dict:
    """
    Pro skeleton metadata attachment (no blocking yet).
    Must never break Free.
    """
    try:
        from src.pro.policy_loader import load_org_policy

        policy = load_org_policy()
        safety_level = (result.get("safety") or {}).get("level", "UNKNOWN")

        # Default: Pro not enabled
        enforcement = {
            "enabled": False,
            "decision": "allow",
            "reason": "No org policy present",
            "policy_version": None,
        }

        if policy and isinstance(policy, dict) and policy.get("rules"):
            decision = "allow"
            reason = "No matching rule"
            required_phrase = None
            for r in policy.get("rules", []):
                if (r.get("safety_level") or "").upper() == str(safety_level).upper():
                    decision = (r.get("decision") or "allow").lower()
                    reason = r.get("message") or f"Matched rule for {safety_level}"
                    required_phrase = r.get("required_phrase") or r.get("confirmation_phrase")
                    break

            enforcement = {
                "enabled": True,
                "decision": decision,  # allow|confirm|block
                "reason": reason,
                "policy_version": policy.get("version", "unknown"),
            }
            if isinstance(required_phrase, str) and required_phrase.strip():
                enforcement["required_phrase"] = required_phrase.strip()

        result["pro_enforcement"] = enforcement
        return result

    except Exception as e:
        # Never break Free behavior
        result["pro_enforcement"] = {
            "enabled": False,
            "decision": "allow",
            "reason": f"Policy evaluation unavailable: {type(e).__name__}",
            "policy_version": None,
        }
        return result

def _extract_service_from_intent(intent: str) -> str:
    """Extract AWS service name from intent."""
    if intent == "unknown":
        return "unknown"
    
    # Intent format: action_service_resource
    # Examples: list_s3_buckets, create_dynamodb_table, list_ec2_instances
    # Service is typically the second part
    parts = intent.split("_")
    
    if len(parts) >= 2:
        # Check if second part is a known AWS service
        service = parts[1]
        # Common AWS services
        aws_services = [
            "s3", "ec2", "lambda", "dynamodb", "iam", "rds", "sqs", "sns",
            "cloudformation", "cloudwatch", "ecr", "eks", "secretsmanager", "ssm"
        ]
        if service in aws_services:
            return service
    
    # Fallback: try first part if it's a service name
    if len(parts) >= 1 and parts[0] in ["s3", "ec2", "lambda", "dynamodb", "iam", "rds"]:
        return parts[0]
    
    return "unknown"

def _determine_confidence(intent: str, entities: dict, method: str) -> str:
    """Determine confidence level based on intent detection method."""
    if intent == "unknown":
        return "low"
    if method == "rule_engine" and entities:
        return "high"
    if method == "ml_classifier":
        return "medium"
    return "medium"

def generate_command_sync(query: str, aws_session=None):
    """
    Main synchronous entry point for generating CLI commands.
    
    Phase B.2 Hardening:
    - Stateless: No state persisted between calls
    - No credentials: Never reads AWS credentials (aws_session unused)
    - No execution: Only generates commands, never executes them
    - Deterministic: Same query always produces same output
    """
    # Ensure registry is initialized
    if not registry.services:
        registry.autodiscover()
    
    # Parse query (deterministic for same input)
    intent, entities = nlp_utils.parse_nlp(query)
    
    # Determine generation method for metadata
    generated_by = "rule_engine"  # Default, could be enhanced to detect ML usage
    
    # Extract service from intent
    service = _extract_service_from_intent(intent)
    
    # registry maps service intent -> parser
    svc = registry.get_service_for_intent(intent)
    if svc is None:
        logger.warning("Unsupported intent: %s", intent)
        return build_standard_response(
            "echo 'Unsupported intent'", 
            "Intent not supported", 
            intent, 
            entities, 
            {"status":"unknown","reason":"unsupported_intent"},
            service="unknown",
            confidence="low",
            generated_by=generated_by
        )

    # call parser (stateless, deterministic)
    result = svc["generate_command"](intent, entities)
    
    # Always run intent-based safety validation (no AWS calls)
    validation = validate_command_safe(intent, entities)
    
    # Determine confidence
    confidence = _determine_confidence(intent, entities, generated_by)
    
    # Phase B.2: aws_session parameter ignored - no AWS credentials used
    # No command execution - only generation
    
    result = build_standard_response(
        result["command"], 
        result["explanation"], 
        intent, 
        entities, 
        validation,
        service=service,
        confidence=confidence,
        generated_by=generated_by
    )

    result = _attach_pro_enforcement(result)
    return result

# async wrapper for MCP tools (fastmcp FunctionTool expects coroutine)
async def generate_command(query: str, aws_session=None):
    return generate_command_sync(query, aws_session=aws_session)

def list_supported_services():
    """List all registered services and their intents."""
    if not registry.services:
        registry.autodiscover()
    
    services_info = {}
    for service_name, service in registry.services.items():
        services_info[service_name] = {
            "intents": service.get("intents", []),
            "intent_count": len(service.get("intents", []))
        }
    
    return {
        "services": list(registry.services.keys()),
        "total_services": len(registry.services),
        "details": services_info
    }

