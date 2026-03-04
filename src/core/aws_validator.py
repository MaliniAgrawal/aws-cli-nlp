import os
import boto3
import logging

logger = logging.getLogger(__name__)

# Intent-based safety classification
INTENT_SAFETY_MAP = {
    # S3 - Safe operations
    "list_s3_buckets": "SAFE",
    "list_s3_objects": "SAFE",
    # S3 - Mutating operations
    "create_s3_bucket": "MUTATING",
    "put_s3_object": "MUTATING",
    # S3 - Destructive operations
    "delete_s3_bucket": "DESTRUCTIVE",
    "delete_s3_object": "DESTRUCTIVE",
    
    # DynamoDB
    "list_dynamodb_tables": "SAFE",
    "create_dynamodb_table": "MUTATING",
    "delete_dynamodb_table": "DESTRUCTIVE",
    
    # EC2
    "list_ec2_instances": "SAFE",
    "start_ec2_instance": "MUTATING",
    "stop_ec2_instance": "MUTATING",
    "terminate_ec2_instance": "DESTRUCTIVE",
    "create_ec2_keypair": "MUTATING",
    "list_ec2_keypairs": "SAFE",
    
    # Lambda
    "list_lambda_functions": "SAFE",
    "invoke_lambda": "MUTATING",
    "create_lambda_function": "MUTATING",
    "delete_lambda_function": "DESTRUCTIVE",
    
    # IAM - All security sensitive
    "list_iam_users": "SECURITY_SENSITIVE",
    "create_iam_user": "SECURITY_SENSITIVE",
    "delete_iam_user": "SECURITY_SENSITIVE",
    "attach_iam_policy": "SECURITY_SENSITIVE",
    "detach_iam_policy": "SECURITY_SENSITIVE",
    "list_iam_policies": "SECURITY_SENSITIVE",
    
    # RDS
    "list_rds_instances": "SAFE",
    "create_rds_instance": "MUTATING",
    "delete_rds_instance": "DESTRUCTIVE",
    
    # CloudFormation
    "list_cloudformation_stacks": "SAFE",
    "create_cloudformation_stack": "MUTATING",
    "delete_cloudformation_stack": "DESTRUCTIVE",
    
    # Other services
    "list_cloudwatch_logs": "SAFE",
    "list_cloudwatch_metrics": "SAFE",
    "get_secret": "SECURITY_SENSITIVE",
    "create_secret": "SECURITY_SENSITIVE",
}

def classify_intent_safety(intent: str) -> dict:
    """Classify safety level based on intent."""
    level = INTENT_SAFETY_MAP.get(intent, "UNKNOWN")
    return {
        "level": level,
        "requires_confirmation": level in ["DESTRUCTIVE", "SECURITY_SENSITIVE"],
        "intent": intent
    }

def validate_command_safe(intent: str, entities: dict) -> dict:
    """Validate command safety based on intent classification."""
    safety = classify_intent_safety(intent)
    
    if safety["level"] == "DESTRUCTIVE":
        return {
            "status": "dangerous",
            "reason": f"Performs destructive operations",
            "requires_confirmation": True,
            "safety_level": "DESTRUCTIVE"
        }
    
    if safety["level"] == "SECURITY_SENSITIVE":
        return {
            "status": "warning",
            "reason": f"Modifies security settings",
            "requires_confirmation": True,
            "safety_level": "SECURITY_SENSITIVE"
        }
    
    if safety["level"] == "MUTATING":
        return {
            "status": "warning",
            "reason": f"Creates or modifies resources",
            "requires_confirmation": True,
            "safety_level": "MUTATING"
        }
    
    if safety["level"] == "SAFE":
        return {
            "status": "safe",
            "reason": f"Read-only operation",
            "requires_confirmation": False,
            "safety_level": "SAFE"
        }
    
    return {
        "status": "unknown",
        "reason": f"Intent '{intent}' not classified",
        "requires_confirmation": True,
        "safety_level": "UNKNOWN"
    }

def _session_from_aws_session(aws_session):
    # callers may pass an existing boto3 session, or None
    if aws_session:
        return aws_session
    return boto3.Session()

def check_s3_bucket_exists(bucket_name, aws_session=None):
    if os.environ.get("ENABLE_AWS_VALIDATION", "").lower() != "true":
        return {"status":"unknown", "reason":"validation disabled"}
    sess = _session_from_aws_session(aws_session)
    s3 = sess.client("s3")
    try:
        s3.head_bucket(Bucket=bucket_name)
        return {"status":"invalid","reason":f"Bucket '{bucket_name}' already exists."}
    except s3.exceptions.NoSuchBucket:
        return {"status":"valid","reason":"Bucket name available."}
    except Exception as e:
        logger.warning("S3 check error: %s", e)
        return {"status":"unknown","reason":str(e)}

def list_s3_buckets(aws_session=None):
    if os.environ.get("ENABLE_AWS_VALIDATION", "").lower() != "true":
        return {"status": "unknown", "buckets": []}
    sess = _session_from_aws_session(aws_session)
    s3 = sess.client("s3")
    resp = s3.list_buckets()
    return {"status":"valid", "buckets": [b["Name"] for b in resp.get("Buckets",[])]}

# Add simple validators for DynamoDB, EC2, Lambda, IAM, RDS, etc. per need
def list_dynamodb_tables(aws_session=None):
    if os.environ.get("ENABLE_AWS_VALIDATION", "").lower() != "true":
        return {"status":"unknown", "tables": []}
    sess = _session_from_aws_session(aws_session)
    dd = sess.client("dynamodb")
    resp = dd.list_tables()
    return {"status":"valid", "tables": resp.get("TableNames", [])}

def list_ec2_instances(region=None, aws_session=None):
    if os.environ.get("ENABLE_AWS_VALIDATION", "").lower() != "true":
        return {"status":"unknown", "instances": []}
    sess = _session_from_aws_session(aws_session)
    ec2 = sess.client("ec2", region_name=region)
    resp = ec2.describe_instances()
    instances = []
    for r in resp.get("Reservations", []):
        for i in r.get("Instances", []):
            inst = {"InstanceId": i.get("InstanceId"), "State": i.get("State",{}).get("Name"), "Tags": i.get("Tags", [])}
            instances.append(inst)
    return {"status":"valid", "instances": instances}

# similarly add list_lambda_functions, list_iam_users, list_rds_instances, etc.
