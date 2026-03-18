"""
Run a small smoke test using your local registry and command generator.
"""

import asyncio
import os
import sys

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from scripts/ to phase-a/
sys.path.insert(0, project_root)

from src.core import nlp_utils
from src.core.command_generator import generate_command_sync
from src.core.registry import registry

QUERIES = [
    "create an S3 bucket named phase25-demo-bucket in us-west-1",
    "list s3 buckets",
    "create dynamodb table Orders in us-west-1",
    "list dynamodb tables",
    "list ec2 instances in us-west-1",
    "create IAM user DevUser",
    "list IAM users",
    "list lambda functions in us-west-1",
    "invoke lambda function named my-test-function in us-west-1",
    "create an RDS instance testdb in us-west-1",
    "list iam users",
    "create iam user DevUser",
    "attach ReadOnlyAccess to user DevUser",
    "detach policy arn:aws:iam::aws:policy/ReadOnlyAccess from user DevUser",
    "list policies for user DevUser",
]


def run_smoke():
    print("\n=== SMOKE TEST ===\n")
    # Ensure registry is initialized
    if not registry.services:
        registry.autodiscover()
    print("Registered services:", registry.list_services())
    for q in QUERIES:
        print("Query:", q)
        out = generate_command_sync(q)
        print(out)
        print("-" * 60)
    print("\nDone.\n")


# quick ad-hoc checks
def test_s3_parser_direct():
    try:
        from importlib import import_module

        m = import_module("src.parsers.s3.parser")
        print("SERVICE:", m.SERVICE)

        # Test S3 queries using generate_command_sync
        s3_queries = [
            "create an S3 bucket named test-bucket in us-west-1",
            "list s3 buckets",
            "delete s3 bucket old-bucket",
            "list objects in bucket my-bucket",
            "upload file test.txt to s3 bucket my-bucket key files/test.txt",
        ]

        for query in s3_queries:
            result = generate_command_sync(query)
            print(f"{query} -> {result['command']}")
    except Exception as e:
        print(f"S3 parser test failed: {e}")
        print("Make sure S3 parser is properly configured for autodiscovery")


def test_ec2_parser_direct():
    try:
        from importlib import import_module

        m = import_module("src.parsers.ec2.parser")
        print("SERVICE:", m.SERVICE_NAME)

        # Test EC2 queries
        ec2_queries = [
            "list ec2 instances in us-west-1",
            "describe ec2 instances",
            "list ec2 instances in us-east-1",
        ]

        for query in ec2_queries:
            result = generate_command_sync(query)
            print(f"{query} -> {result['command']}")
    except Exception as e:
        print(f"EC2 parser test failed: {e}")
        print("Make sure EC2 parser is properly configured for autodiscovery")


if __name__ == "__main__":
    run_smoke()
    print("\n=== S3 PARSER DIRECT TEST ===")
    test_s3_parser_direct()
    print("\n=== EC2 PARSER DIRECT TEST ===")
    test_ec2_parser_direct()
