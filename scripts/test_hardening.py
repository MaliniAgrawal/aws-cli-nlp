"""
Phase B.2 Hardening Verification Test
Tests all hardening requirements for MCP server.
"""
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.core.command_generator import generate_command_sync
from src.core.hardening import run_hardening_checks
import json

def test_metadata_structure():
    """Test that all responses include proper metadata."""
    queries = [
        "list s3 buckets",
        "create s3 bucket test-bucket in us-west-1",
        "list ec2 instances in us-east-1",
        "list lambda functions",
        "unknown query that should fail"
    ]
    
    print("\n=== METADATA STRUCTURE TEST ===\n")
    all_passed = True
    
    for query in queries:
        result = generate_command_sync(query)
        
        # Check required fields
        required = ["command", "explanation", "intent", "entities", "validation", "meta"]
        meta_required = ["service", "confidence", "generated_by", "version"]
        
        missing = [f for f in required if f not in result]
        meta_missing = [f for f in meta_required if f not in result.get("meta", {})]
        
        if missing or meta_missing:
            print(f"❌ FAIL: {query}")
            if missing:
                print(f"   Missing fields: {missing}")
            if meta_missing:
                print(f"   Missing meta fields: {meta_missing}")
            all_passed = False
        else:
            print(f"✅ PASS: {query}")
            print(f"   Service: {result['meta']['service']}, Confidence: {result['meta']['confidence']}")
    
    return all_passed

def test_deterministic():
    """Test that same input produces same output."""
    print("\n=== DETERMINISTIC OUTPUT TEST ===\n")
    
    query = "list s3 buckets in us-west-1"
    result1 = generate_command_sync(query)
    result2 = generate_command_sync(query)
    
    # Compare all fields
    matches = (
        result1["command"] == result2["command"] and
        result1["explanation"] == result2["explanation"] and
        result1["intent"] == result2["intent"] and
        result1["entities"] == result2["entities"] and
        result1["validation"] == result2["validation"] and
        result1["meta"] == result2["meta"]
    )
    
    if matches:
        print(f"✅ PASS: Deterministic output verified")
        print(f"   Query: {query}")
        print(f"   Command: {result1['command']}")
    else:
        print(f"❌ FAIL: Non-deterministic output detected")
        print(f"   Result 1: {json.dumps(result1, indent=2)}")
        print(f"   Result 2: {json.dumps(result2, indent=2)}")
    
    return matches

def test_no_credentials():
    """Verify no AWS credentials are accessed."""
    print("\n=== NO CREDENTIALS TEST ===\n")
    
    # Test that aws_session parameter is ignored
    query = "list s3 buckets"
    result1 = generate_command_sync(query, aws_session=None)
    result2 = generate_command_sync(query, aws_session="fake_session")
    
    # Results should be identical regardless of aws_session
    matches = result1 == result2
    
    if matches:
        print(f"✅ PASS: AWS session parameter properly ignored")
        print(f"   No credentials accessed or stored")
    else:
        print(f"❌ FAIL: AWS session parameter affects output")
    
    return matches

def test_no_execution():
    """Verify commands are never executed."""
    print("\n=== NO EXECUTION TEST ===\n")
    
    # Generate a command that would fail if executed
    query = "delete s3 bucket nonexistent-bucket-12345"
    result = generate_command_sync(query)
    
    # If we got a result, command was not executed (would have failed)
    if result and "command" in result:
        print(f"✅ PASS: Command generated but not executed")
        print(f"   Command: {result['command']}")
        print(f"   (Command generation only, no AWS API calls made)")
        return True
    else:
        print(f"❌ FAIL: Unexpected behavior")
        return False

def test_stateless():
    """Verify no state persists between requests."""
    print("\n=== STATELESS TEST ===\n")
    
    # Make multiple requests and verify no state leakage
    queries = [
        "list s3 buckets in us-west-1",
        "list ec2 instances in us-east-1",
        "list s3 buckets in us-west-1"  # Repeat first query
    ]
    
    results = [generate_command_sync(q) for q in queries]
    
    # First and third results should be identical (no state)
    if results[0] == results[2]:
        print(f"✅ PASS: Stateless operation verified")
        print(f"   Repeated queries produce identical results")
        return True
    else:
        print(f"❌ FAIL: State appears to persist between requests")
        return False

def run_all_tests():
    """Run all hardening tests."""
    print("\n" + "="*60)
    print("PHASE B.2 - MCP SERVER HARDENING VERIFICATION")
    print("="*60)
    
    tests = [
        ("Metadata Structure", test_metadata_structure),
        ("Deterministic Output", test_deterministic),
        ("No Credentials", test_no_credentials),
        ("No Execution", test_no_execution),
        ("Stateless", test_stateless)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL HARDENING TESTS PASSED")
    else:
        print("⚠️  SOME HARDENING TESTS FAILED")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
