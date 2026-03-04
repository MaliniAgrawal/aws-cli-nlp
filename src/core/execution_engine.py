"""src/core/execution_engine.py

Execution engine for optional AWS CLI command execution with human authorization.

Phase B.2 Guarantees:
- AI suggests (command generation)
- Human authorizes (explicit confirmation)
- Policy blocks (safety enforcement)
- Never executes without authorization
"""
import subprocess
import shlex
import json
import os
import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum

class ExecutionPolicy(Enum):
    """Execution policy levels."""
    ALLOW_SAFE = "allow_safe"           # Auto-allow SAFE operations
    REQUIRE_CONFIRMATION = "require_confirmation"  # Require confirmation for all
    BLOCK_DESTRUCTIVE = "block_destructive"  # Block DESTRUCTIVE operations
    BLOCK_ALL = "block_all"             # Block all execution


class CallerType(Enum):
    """Explicit caller types to avoid fragile string checks."""
    CLI = "cli"
    MCP = "mcp"
    HTTP = "http"


class ExecutionResult:
    """Result of command execution."""
    def __init__(self, success: bool, stdout: str = "", stderr: str = "", 
                 exit_code: int = 0, blocked: bool = False, reason: str = ""):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.blocked = blocked
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "blocked": self.blocked,
            "reason": self.reason
        }


def check_policy(safety_level: str, policy: ExecutionPolicy) -> tuple[bool, str]:
    """
    Check if execution is allowed by policy.
    
    Returns: (allowed, reason)
    """
    if policy == ExecutionPolicy.BLOCK_ALL:
        return False, "Execution blocked by policy: BLOCK_ALL"
    
    if policy == ExecutionPolicy.BLOCK_DESTRUCTIVE and safety_level == "DESTRUCTIVE":
        return False, "Execution blocked by policy: DESTRUCTIVE operations not allowed"
    
    if policy == ExecutionPolicy.REQUIRE_CONFIRMATION:
        return True, "Confirmation required by policy"
    
    if policy == ExecutionPolicy.ALLOW_SAFE and safety_level == "SAFE":
        return True, "Auto-allowed by policy: SAFE operation"
    
    return True, "Execution allowed by policy"


def _normalize_caller(caller: Union[str, CallerType]) -> CallerType:
    """Normalize caller to CallerType, accepting strings for backward compatibility."""
    if isinstance(caller, CallerType):
        return caller
    if not isinstance(caller, str):
        return CallerType.CLI
    key = caller.lower()
    if key == "mcp":
        return CallerType.MCP
    if key == "http":
        return CallerType.HTTP
    return CallerType.CLI


def execute_command(
    command: str,
    safety_level: str,
    human_authorized: bool = False,
    policy: ExecutionPolicy = ExecutionPolicy.REQUIRE_CONFIRMATION,
    dry_run: bool = False,
    timeout: int = 30,
    caller: Union[str, CallerType] = CallerType.CLI,
    auto_approve: bool = False
) -> ExecutionResult:
    """
    Execute AWS CLI command with safety guarantees.
    
    Args:
        command: AWS CLI command to execute
        safety_level: SAFE, MUTATING, SECURITY_SENSITIVE, DESTRUCTIVE
        human_authorized: Explicit human authorization
        policy: Execution policy to enforce
        dry_run: If True, simulate execution without running
        timeout: Command timeout in seconds
    
    Returns:
        ExecutionResult with outcome
    
    Safety Guarantees:
    - Never executes without human_authorized=True
    - Policy enforcement before execution
    - Timeout protection
    - Dry-run mode available
    """
    # Normalize caller and block remote/MCP callers explicitly
    caller_type = _normalize_caller(caller)
    if caller_type in {CallerType.MCP, CallerType.HTTP}:
        result = ExecutionResult(
            success=False,
            blocked=True,
            reason="Execution unavailable: calls from MCP/server/API are blocked"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result

    # Auto-approve guard: do not allow auto-approve for destructive/security-sensitive
    if auto_approve and safety_level in ("DESTRUCTIVE", "SECURITY_SENSITIVE"):
        result = ExecutionResult(
            success=False,
            blocked=True,
            reason="Auto-approve not allowed for destructive or security-sensitive operations"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result

    # Guarantee 1: Human authorization required
    if not human_authorized:
        result = ExecutionResult(
            success=False,
            blocked=True,
            reason="Execution requires explicit human authorization"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result
    
    # Guarantee 2: Policy enforcement
    allowed, reason = check_policy(safety_level, policy)
    if not allowed:
        result = ExecutionResult(
            success=False,
            blocked=True,
            reason=reason
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result
    
    # Guarantee 3: Dry-run mode
    if dry_run:
        result = ExecutionResult(
            success=True,
            stdout=f"[DRY RUN] Would execute: {command}",
            reason="Dry-run mode - command not executed"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result
    
    # Execute with timeout protection
    try:
        # Use shlex.split to avoid shell interpolation and pass list to subprocess (shell=False)
        proc = subprocess.run(
            shlex.split(command),
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        result_obj = ExecutionResult(
            success=True,
            stdout=proc.stdout,
            stderr=proc.stderr,
            exit_code=proc.returncode,
            reason="Executed successfully"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result_obj)
        return result_obj

    except subprocess.CalledProcessError as cpe:
        # Command executed but returned non-zero exit status
        result = ExecutionResult(
            success=False,
            stdout=getattr(cpe, "stdout", ""),
            stderr=getattr(cpe, "stderr", ""),
            exit_code=getattr(cpe, "returncode", -1),
            reason="Execution failed"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result

    except subprocess.TimeoutExpired:
        result = ExecutionResult(
            success=False,
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=-1,
            reason="Timeout"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result

    except Exception as e:
        result = ExecutionResult(
            success=False,
            stderr=str(e),
            exit_code=-1,
            reason=f"Execution error: {str(e)}"
        )
        _audit_execution(command, safety_level, policy, human_authorized, dry_run, result)
        return result


def _audit_execution(command: str, safety_level: str, policy: ExecutionPolicy, human_authorized: bool, dry_run: bool, result: ExecutionResult) -> None:
    """
    Append an auditable JSON line to a log file with execution metadata.
    """
    try:
        audit_record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "command": command,
            "safety_level": safety_level,
            "policy": policy.value if isinstance(policy, ExecutionPolicy) else str(policy),
            "human_authorized": human_authorized,
            "dry_run": dry_run,
            "result": result.to_dict()
        }

        # Place the audit log at the phase-a root directory
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        log_path = os.path.join(root_dir, "execution_audit.log")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_record) + "\n")

        # Try to emit telemetry if available
        try:
            from src.core.telemetry import telemetry_log_event
            telemetry_log_event("execution.attempt", {
                "command": command,
                "safety_level": safety_level,
                "success": result.success,
                "blocked": result.blocked
            })
        except Exception:
            # Telemetry is optional; swallow errors to avoid breaking execution
            pass

    except Exception:
        # Swallow all audit errors to avoid interfering with execution flow
        pass


def execute_with_confirmation(
    generated_response: Dict[str, Any],
    policy: ExecutionPolicy = ExecutionPolicy.REQUIRE_CONFIRMATION,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute command from generated response with confirmation.
    
    This is the main entry point for AI-assisted, human-authorized execution.
    
    Args:
        generated_response: Response from generate_command_sync()
        policy: Execution policy
        dry_run: Dry-run mode
    
    Returns:
        Response with execution result added
    """
    pe = generated_response.get("pro_enforcement") or {}
    if pe.get("enabled") and (pe.get("decision") or "").lower() == "block":
        # Do not execute. Return structured failure.
        resp = dict(generated_response)
        resp["execution"] = {
            "allowed": False,
            "mode": "manual",
            "blocked": True,
            "reason": f"BLOCKED by org-policy: {pe.get('reason', 'Policy rule')}"
        }
        return resp

    command = generated_response.get("command", "")
    safety = generated_response.get("safety", {})
    safety_level = safety.get("level", "UNKNOWN")
    
    # Human authorization is implicit when calling this function
    # In practice, this would be called after user confirms
    result = execute_command(
        command=command,
        safety_level=safety_level,
        human_authorized=True,  # Caller confirms authorization
        policy=policy,
        dry_run=dry_run
    )
    
    # Add execution result to response
    response = generated_response.copy()
    response["execution"] = result.to_dict()
    
    return response
