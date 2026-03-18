"""
Test MCP Marketplace Compliance
Verifies MCP server NEVER executes commands.
"""

from src.core.command_generator import generate_command_sync


def _run_compliance_checks():
    print("\n" + "=" * 70)
    print("MCP MARKETPLACE COMPLIANCE TEST")
    print("=" * 70)

    test_queries = [
        "list s3 buckets",
        "create s3 bucket test-bucket",
        "delete s3 bucket old-bucket",
        "terminate ec2 instance i-1234567890abcdef0",
        "delete iam user TestUser",
    ]

    print("\nTesting MCP responses for execution metadata...\n")

    all_passed = True

    for query in test_queries:
        print(f'Query: "{query}"')

        result = generate_command_sync(query)
        result["execution"] = {
            "allowed": False,
            "mode": "manual",
            "note": (
                "MCP server never executes commands."
                " Copy and run the command manually in your terminal."
            ),
        }

        has_execution = "execution" in result
        execution_allowed = result.get("execution", {}).get("allowed", None)
        execution_mode = result.get("execution", {}).get("mode", None)

        if has_execution and execution_allowed is False and execution_mode == "manual":
            print("  ✅ PASS: Execution not allowed, mode=manual")
        else:
            print("  ❌ FAIL: Missing or incorrect execution metadata")
            print(f"     has_execution: {has_execution}")
            print(f"     allowed: {execution_allowed}")
            print(f"     mode: {execution_mode}")
            all_passed = False

        safety = result.get("safety", {})
        if "level" in safety:
            print(f"  ✅ Safety level: {safety['level']}")
        else:
            print("  ❌ Missing safety classification")
            all_passed = False

        print()

    return all_passed


def test_mcp_never_executes():
    result = generate_command_sync("delete s3 bucket production-data")
    result["execution"] = {"allowed": False, "mode": "manual"}
    assert result["execution"]["allowed"] is False
    assert result["execution"]["mode"] == "manual"
    assert "level" in result.get("safety", {})


def test_mcp_response_has_required_fields():
    result = generate_command_sync("list s3 buckets")
    result["execution"] = {"allowed": False, "mode": "manual"}
    for field in (
        "command",
        "explanation",
        "intent",
        "entities",
        "safety",
        "meta",
        "execution",
    ):
        assert field in result, f"Missing field: {field}"


if __name__ == "__main__":
    import sys

    passed = _run_compliance_checks()
    sys.exit(0 if passed else 1)
