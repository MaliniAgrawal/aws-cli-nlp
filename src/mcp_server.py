# src/mcp_server.py
import argparse
import asyncio
import os
import sys
import json

USE_HAIKU = bool(os.getenv("USE_HAIKU", "false").lower() in ["true", "1", "yes"])


# ensure src on path (if running from repo root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP

from src.core.nlp_utils import parse_nlp
from src.core.command_generator import generate_command, list_supported_services
from src.core.aws_validator import validate_command_safe
from src.core.telemetry import telemetry_log_event
from src.core.cli_formatter import format_mcp_response
from src.core.registry import registry
from src.core.logging_utils import setup_logger

# Setup safe cross-platform logging
logger = setup_logger("aws-cli-generator-phase-a")

# Initialize registry before creating MCP tools
registry.autodiscover()

mcp = FastMCP("aws-cli-generator")

# Tool: generate aws cli
@mcp.tool()
async def generate_aws_cli(query: str):
    """
    Generate AWS CLI command from natural language query.
    
    CRITICAL: This tool NEVER executes commands.
    It only generates command strings for human review and manual execution.
    
    Phase B.2 Marketplace Requirement:
    - MCP always refuses execution
    - User must execute commands manually
    - This is required for marketplace approval
    
    Phase B.3.3 Agent Optimization:
    - Returns compact, deterministic JSON
    - No UI strings, colors, or prose
    - Safe for direct agent/LLM consumption
    """
    result = await generate_command(query)
    
    # EXPLICIT REFUSAL: Make MCP execution block undeniable in code
    # This is a marketplace defense: execution is impossible by design
    if "execution" in result:
        result["execution"]["allowed"] = False
        result["execution"]["mode"] = "manual"
    else:
        result["execution"] = {
            "allowed": False,
            "mode": "manual"
        }
    
    # Format for agent consumption: compact, stable, machine-friendly
    formatted = format_mcp_response(result)
    
    telemetry_log_event("response.emitted", {
        "result_summary": {
            "intent": result["intent"], 
            "safety_level": result["safety"].get("level"),
            "execution_mode": "manual",
            "format": "mcp"
        }
    })
    
    return formatted

@mcp.tool()
async def health_check():
    return {"status": "ok", "model": "haiku" if USE_HAIKU else "local-transformer"}

@mcp.tool()
async def list_supported_services_mcp():
    return list_supported_services()

async def run_stdio():
    logger.info("Starting MCP stdio server")
    await mcp.run_stdio_async()

def main():
    # Free v1 exposes MCP stdio mode only.
    parser = argparse.ArgumentParser(description="AWS CLI Assistant MCP server (stdio only)")
    parser.add_argument(
        "--mode",
        default="mcp",
        help="Compatibility flag. Only 'mcp' is supported in Free v1."
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Deprecated and unsupported in Free v1."
    )
    args = parser.parse_args()

    if args.http or str(args.mode).lower() != "mcp":
        print("[!] Free v1 supports MCP stdio mode only. Use: python -m src.mcp_server", file=sys.stderr)
        sys.exit(2)

    print("[MCP] Starting MCP stdio server...", file=sys.stderr)
    asyncio.run(run_stdio())

if __name__ == "__main__":
    main()
    __all__ = ["generate_aws_cli", "list_supported_services", "health_check"]

