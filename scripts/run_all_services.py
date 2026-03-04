"""Run helper that tests all AWS service parsers without using a `test_` filename.

This is a simple preservation of the original `scripts/test_all_services.py` behavior
but renamed to avoid pytest discovery issues.
"""
import sys
from pathlib import Path
from pprint import pprint

# Add src folder to Python path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC.resolve()))

from src.core.registry import registry
from src.core.nlp_utils import parse_nlp
from src.core.command_generator import generate_command
from src.core.aws_validator import validate_command_safe


def test_service_command(service, intent, entities):
    print(f"\n{'='*80}")
    print(f"Testing {service.upper()} Service")
    print(f"Intent: {intent}")
    print(f"Entities: {entities}")
    print(f"{'-'*80}")
    
    # Generate command using registry
    result = generate_command(intent, entities)
    print(f"\nCommand generated: {result}")
    
    # Validate command
    validation = validate_command_safe(intent, entities)
    print(f"\nValidation result:")
    print(f"Status: {validation.get('status')}")
    print(f"Reason: {validation.get('reason')}")
    print(f"Details: {validation.get('detail')}")


def run_all_tests():
    # Initialize registry once
    if not registry.services:
        registry.autodiscover()
    
    # Test cases for each service
    test_cases = [
        # S3 Tests
        {
            'service': 's3',
            'intent': 'create_s3_bucket',
            'entities': {'bucket': 'phase3-test-bucket', 'region': 'us-west-1'}
        },
        {
            'service': 's3',
            'intent': 'list_s3_buckets',
            'entities': {}
        },
        
        # EC2 Tests
        {
            'service': 'ec2',
            'intent': 'list_ec2_instances',
            'entities': {'region': 'us-west-1'}
        },
        {
            'service': 'ec2',
            'intent': 'start_ec2_instance',
            'entities': {'instance_id': 'i-1234567890abcdef0', 'region': 'us-west-1'}
        },
        
        # Lambda Tests
        {
            'service': 'lambda',
            'intent': 'list_lambda_functions',
            'entities': {'region': 'us-west-1'}
        },
        {
            'service': 'lambda',
            'intent': 'invoke_lambda',
            'entities': {'function_name': 'test-function', 'region': 'us-west-1'}
        },
        
        # DynamoDB Tests
        {
            'service': 'dynamodb',
            'intent': 'list_dynamodb_tables',
            'entities': {}
        },
        {
            'service': 'dynamodb',
            'intent': 'create_dynamodb_table',
            'entities': {'table': 'test-table', 'region': 'us-west-1'}
        },
        
        # IAM Tests
        {
            'service': 'iam',
            'intent': 'list_iam_users',
            'entities': {}
        },
        {
            'service': 'iam',
            'intent': 'create_iam_user',
            'entities': {'user_name': 'test-user'}
        }
    ]
    
    for test in test_cases:
        test_service_command(
            test['service'],
            test['intent'],
            test['entities']
        )


if __name__ == "__main__":
    print("\n🚀 Testing All AWS Services Command Generation and Validation\n")
    
    # Test AWS credentials
    import boto3
    from botocore.exceptions import NoCredentialsError, PartialCredentialsError
    
    print("🔐 Checking AWS credentials:")
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print("✅ Valid credentials detected:", identity["Arn"])
    except (NoCredentialsError, PartialCredentialsError):
        print("⚠️ No AWS credentials found. Some validations will show 'unknown'.")
    
    run_all_tests()
