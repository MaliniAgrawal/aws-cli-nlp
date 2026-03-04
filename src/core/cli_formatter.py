# src/core/cli_formatter.py
"""
CLI output formatter for human-friendly display.
MCP gets JSON, CLI gets formatted text.
"""
import json
import os
from typing import Dict, Any

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'

def _get_color(code: str, no_color: bool = False) -> str:
    """Get color code or empty string if no_color is True."""
    if no_color or os.environ.get("NO_COLOR"):
        return ""
    return code

def _get_safety_display(safety: dict, no_color: bool = False) -> str:
    """Format safety validation for display."""
    level = safety.get("level", "UNKNOWN")
    hint = safety.get("confirmation_hint", "")
    
    if level == "SAFE":
        color = _get_color(Colors.GREEN, no_color)
        icon = "[OK]"
        label = "SAFE"
    elif level == "MUTATING":
        color = _get_color(Colors.YELLOW, no_color)
        icon = "[!]"
        label = "MUTATING"
    elif level == "SECURITY_SENSITIVE":
        color = _get_color(Colors.RED, no_color)
        icon = "[!]"
        label = "SECURITY-SENSITIVE"
    elif level == "DESTRUCTIVE":
        color = _get_color(Colors.RED, no_color)
        icon = "[!]"
        label = "DESTRUCTIVE"
    else:
        color = _get_color(Colors.GRAY, no_color)
        icon = "?"
        label = "UNKNOWN"
    
    reset = _get_color(Colors.RESET, no_color)
    return f"{color}{icon} {label}{reset} - {hint}"

def _get_tip(safety: dict) -> str:
    """Get contextual tip based on safety level."""
    return safety.get("confirmation_hint", "Verify the command before execution.")

def format_human(result: Dict[str, Any], no_color: bool = False) -> str:
    """
    Format result as human-friendly text for CLI.
    
    Args:
        result: Standard response schema dict
        no_color: Disable color output
    
    Returns:
        Formatted string for CLI display
    """
    bold = _get_color(Colors.BOLD, no_color)
    cyan = _get_color(Colors.CYAN, no_color)
    blue = _get_color(Colors.BLUE, no_color)
    gray = _get_color(Colors.GRAY, no_color)
    reset = _get_color(Colors.RESET, no_color)
    
    command = result.get("command", "")
    explanation = result.get("explanation", "")
    safety = result.get("safety", {})
    
    # Build output
    lines = []
    lines.append(f"{bold}Command:{reset}")
    lines.append(f"  {cyan}{command}{reset}")
    lines.append("")
    lines.append(f"{bold}Safety:{reset}")
    lines.append(f"  {_get_safety_display(safety, no_color)}")
    lines.append("")
    lines.append(f"{bold}Explanation:{reset}")
    lines.append(f"  {explanation}")
    lines.append("")
    lines.append(f"{bold}Tip:{reset}")
    lines.append(f"  {gray}{_get_tip(safety)}{reset}")
    
    return "\n".join(lines)

def format_json(result: Dict[str, Any]) -> str:
    """Format result as JSON (for --json flag or MCP)."""
    return json.dumps(result, indent=2)


def format_agent(result: Dict[str, Any]) -> str:
    """IDE / agent-friendly compact JSON.
    - single line
    - stable keys
    - minimal but sufficient metadata
    """
    safety = result.get("safety", {}) or {}
    meta = result.get("meta", {}) or {}

    payload = {
        "command": result.get("command", ""),
        "intent": result.get("intent", ""),
        "service": meta.get("service", ""),
        "explanation": result.get("explanation", ""),
        "safety": {
            "level": safety.get("level", "UNKNOWN"),
            "requires_confirmation": bool(safety.get("requires_confirmation", False)),
            "confirmation_hint": safety.get("confirmation_hint", ""),
        },
        "meta": {
            "confidence": meta.get("confidence", ""),
            "generated_by": meta.get("generated_by", ""),
            "version": meta.get("version", ""),
        },
    }

    # single-line json for tooling
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def format_explain_only(result: Dict[str, Any], no_color: bool = False) -> str:
    intent = result.get("intent", "unknown")
    service = (result.get("meta", {}) or {}).get("service", "unknown")
    explanation = result.get("explanation", "Intent not supported")

    return (
        f"Intent: {intent}\n"
        f"Service: {service}\n"
        f"Explanation:\n"
        f"  {explanation}\n"
    )


def format_human_cli(response: Dict[str, Any], no_color: bool = False) -> str:
    """
    Human-friendly CLI block format used for demos, reviewers and marketplace.
    Keeps output read-only and emphasizes safety information.
    """
    sep = "─" * 56
    command = response.get("command", "")
    explanation = response.get("explanation", "")
    safety = response.get("safety", {}) or {}
    entities = response.get("entities", {}) or {}
    meta = response.get("meta", {}) or {}

    # Safety fields
    level = safety.get("level", "UNKNOWN")
    requires_confirmation = safety.get("requires_confirmation", False)
    auto_run = safety.get("auto_run_enabled", False)

    lines = []
    lines.append(sep)
    lines.append("🤖 AI-SUGGESTED AWS CLI COMMAND")
    lines.append(sep)
    lines.append(command)
    lines.append("")

    lines.append("🧠 Explanation")
    lines.append(explanation)
    lines.append("")

    lines.append("🔐 Safety Assessment")
    lines.append(f"• Level        : {level}")
    lines.append(f"• Auto-run     : {'✅ Enabled' if auto_run else '❌ Disabled'}")
    lines.append(f"• Confirmation: {'✅ Required' if requires_confirmation else '❌ Not required'}")
    lines.append("")

    lines.append("📦 Detected Intent")
    lines.append(f"• Intent   : {response.get('intent')}")
    lines.append(f"• Service  : {meta.get('service')}")
    if entities.get("region"):
        lines.append(f"• Region   : {entities.get('region')}")
    lines.append("")

    lines.append("▶️ Next Steps")
    lines.append("• Review the command carefully")
    lines.append("• Copy & run it manually, or")
    lines.append("• Run with confirmation mode enabled")
    lines.append("")
    lines.append("ℹ️ Note")
    lines.append("This tool NEVER executes AWS commands automatically.")
    lines.append(sep)

    return "\n".join(lines)

def format_mcp_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format response for MCP/agent consumption.
    
    Design principles:
    - Compact (token-efficient for LLMs)
    - Stable (no UI strings, colors, or prose)
    - Execution-safe (always allowed=False)
    - Deterministic (machine-friendly, not human-friendly)
    - No emojis, colors, or human narrative
    
    This is a machine contract, not a UI.
    
    Args:
        response: Standard response schema dict
        
    Returns:
        Minimal agent-friendly JSON response
    """
    safety = response.get("safety", {})
    meta = response.get("meta", {})
    
    return {
        "type": "aws.cli.suggestion",
        "version": "1.0",
        "command": response.get("command"),
        "intent": response.get("intent"),
        "service": meta.get("service"),
        "safety": {
            "level": safety.get("level"),
            "requires_confirmation": safety.get("requires_confirmation", False)
        },
        "execution": {
            "allowed": False,
            "mode": "manual",
            "reason": "MCP execution is disabled"
        },
        "confidence": meta.get("confidence", "unknown")
    }


def format_agent_payload(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strict, deterministic payload for IDE/AI agent consumption.
    No prose; stable keys; minimal fields.
    """
    safety = result.get("safety", {}) or {}
    meta = result.get("meta", {}) or {}
    entities = result.get("entities", {}) or {}

    return {
        "command": result.get("command", ""),
        "intent": result.get("intent", "unknown"),
        "service": meta.get("service", "unknown"),
        "confidence": meta.get("confidence", "low"),
        "entities": entities,

        "safety_level": safety.get("level", "UNKNOWN"),
        "requires_confirmation": bool(safety.get("requires_confirmation", False)),
        "confirmation_hint": safety.get("confirmation_hint", ""),
        "execution": {
            "allowed": bool((result.get("execution") or {}).get("allowed", False)),
            "mode": (result.get("execution") or {}).get("mode", "manual"),
        },
        "schema_version": meta.get("version", "1.0.0"),
    }
