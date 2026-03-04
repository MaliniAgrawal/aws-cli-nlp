"""
Test Phase B.3 CLI UX Polish
Demonstrates human-friendly output vs JSON output
"""
import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.core.command_generator import generate_command_sync
from src.core.cli_formatter import format_human, format_json, format_explain_only

def test_cli_formats():
    """Test different CLI output formats."""
    
    test_queries = [
        ("list s3 buckets", "safe"),
        ("create s3 bucket test-bucket in us-west-1", "warning"),
        ("delete s3 bucket old-bucket", "dangerous"),
        ("unknown weird query", "unknown")
    ]
    
    print("\n" + "="*70)
    print("PHASE B.3 - CLI UX POLISH TEST")
    print("="*70)
    
    for query, expected_status in test_queries:
        result = generate_command_sync(query)
        
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        
        # Test 1: Human-friendly format (default)
        print("\n--- DEFAULT (Human-Friendly) ---")
        print(format_human(result, no_color=False))
        
        # Test 2: JSON format
        print("\n--- WITH --json FLAG ---")
        print(format_json(result))
        
        # Test 3: Explain-only format
        print("\n--- WITH --explain-only FLAG ---")
        print(format_explain_only(result, no_color=False))
        
        # Test 4: No color
        print("\n--- WITH --no-color FLAG ---")
        print(format_human(result, no_color=True))
        
        print("\n")

def test_color_codes():
    """Test that color codes work correctly."""
    print("\n" + "="*70)
    print("COLOR CODE TEST")
    print("="*70)
    
    queries = [
        "list s3 buckets",           # Safe - green
        "create s3 bucket test",     # Warning - yellow
        "delete s3 bucket old"       # Dangerous - red
    ]
    
    for query in queries:
        result = generate_command_sync(query)
        print(f"\n{query}:")
        print(format_human(result, no_color=False))
        print()

def test_cli_flags():
    """Test CLI flag behavior."""
    print("\n" + "="*70)
    print("CLI FLAGS TEST")
    print("="*70)
    
    query = "list ec2 instances in us-west-1"
    result = generate_command_sync(query)
    
    print("\n1. Default output (human-friendly):")
    print("-" * 70)
    print(format_human(result))
    
    print("\n2. --json flag:")
    print("-" * 70)
    print(format_json(result))
    
    print("\n3. --explain-only flag:")
    print("-" * 70)
    print(format_explain_only(result))
    
    print("\n4. --no-color flag:")
    print("-" * 70)
    print(format_human(result, no_color=True))

if __name__ == "__main__":
    print("\n🎨 Testing CLI UX Polish Features\n")
    
    test_cli_formats()
    test_color_codes()
    test_cli_flags()
    
    print("\n" + "="*70)
    print("✅ CLI UX POLISH TEST COMPLETE")
    print("="*70)
    print("\nTo use the CLI:")
    print("  python src/aws_nlp.py \"list s3 buckets\"")
    print("  python src/aws_nlp.py --json \"list s3 buckets\"")
    print("  python src/aws_nlp.py --no-color \"list s3 buckets\"")
    print("  python src/aws_nlp.py --explain-only \"list s3 buckets\"")
    print()
