SERVICE_NAME = "lambda"
INTENTS = ["list_lambda_functions", "invoke_lambda_function"]


def generate_command(intent, entities):
    region = entities.get("region")
    if intent == "list_lambda_functions":
        cmd = "aws lambda list-functions"
        if region:
            cmd += f" --region {region}"
        return {
            "command": cmd,
            "explanation": f"Lists Lambda functions{' in ' + region if region else ''}.",
        }
    if intent == "invoke_lambda_function":
        fn = entities.get("function", "my-function")
        region = entities.get("region")
        cmd = f"aws lambda invoke --function-name {fn} /tmp/output.json"
        if region:
            cmd += f" --region {region}"
        return {
            "command": cmd,
            "explanation": f"Invokes Lambda function '{fn}' (result to /tmp/output.json).",
        }
    return {"command": "echo 'unsupported'", "explanation": "Unsupported lambda intent"}


def validate(intent, entities, aws_session=None):
    # optional: list functions via boto3
    return {"status": "unknown", "reason": "no validation by default"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
