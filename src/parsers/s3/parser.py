from src.core import aws_validator

SERVICE = "s3"
SERVICE_NAME = "s3"
INTENTS = [
    "create_s3_bucket",
    "list_s3_buckets",
    "delete_s3_bucket",
    "list_s3_objects",
    "put_s3_object",
]

# --- ADD THIS SECTION ---
EXAMPLES = [
    "create a new S3 bucket called my-new-data-lake in eu-central-1",
    "list s3 buckets",
    "delete bucket old-data-bucket",
    "list objects in the bucket my-files",
    "upload the file image.jpg to the bucket multimedia under the key photos/image.jpg",
]
# ------------------------


def generate_command(intent, entities):
    if intent == "create_s3_bucket":
        bucket = entities.get("bucket", "my-bucket")
        region = entities.get("region")
        if region:
            cmd = f"aws s3 mb s3://{bucket} --region {region}"
        else:
            cmd = f"aws s3 mb s3://{bucket}"
        return {
            "command": cmd,
            "explanation": f"Creates an S3 bucket named '{bucket}'{' in ' + region if region else ''}.",
        }

    if intent == "list_s3_buckets":
        return {
            "command": "aws s3 ls",
            "explanation": "Lists S3 buckets in your account (global).",
        }

    if intent == "delete_s3_bucket":
        bucket = entities.get("bucket", "my-bucket")
        cmd = f"aws s3 rb s3://{bucket} --force"
        return {
            "command": cmd,
            "explanation": f"Deletes S3 bucket '{bucket}' and all its contents (force).",
        }

    if intent == "list_s3_objects":
        bucket = entities.get("bucket", "my-bucket")
        prefix = entities.get("prefix")
        if prefix:
            cmd = f"aws s3 ls s3://{bucket}/{prefix} --recursive"
            return {
                "command": cmd,
                "explanation": f"Lists objects under '{prefix}' in bucket '{bucket}'.",
            }
        else:
            cmd = f"aws s3 ls s3://{bucket}"
            return {
                "command": cmd,
                "explanation": f"Lists objects in bucket '{bucket}'.",
            }

    if intent == "put_s3_object":
        bucket = entities.get("bucket", "my-bucket")
        key = entities.get("key", "upload.dat")
        local_path = entities.get("local_path", "./file")
        cmd = f"aws s3 cp {local_path} s3://{bucket}/{key}"
        return {
            "command": cmd,
            "explanation": f"Uploads local file '{local_path}' to s3://{bucket}/{key}.",
        }

    return {
        "command": "echo 'Unknown S3 intent'",
        "explanation": "Intent not supported",
    }


def validate(intent, entities, aws_session=None):
    if intent == "create_s3_bucket":
        bucket = entities.get("bucket", "")
        return aws_validator.check_s3_bucket_exists(bucket, aws_session=aws_session)
    if intent == "list_s3_buckets":
        return aws_validator.list_s3_buckets(aws_session=aws_session)
    return {"status": "unknown", "reason": "no validation for that intent"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
