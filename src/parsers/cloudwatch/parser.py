SERVICE_NAME = "cloudwatch"
INTENTS = ["list_cloudwatch_metrics", "list_cloudwatch_logs"]

def generate_command(intent, entities):
    region = entities.get("region")

    if intent == "list_cloudwatch_metrics":
        cmd = "aws cloudwatch list-metrics"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Lists CloudWatch metrics."}

    if intent == "list_cloudwatch_logs":
        cmd = "aws logs describe-log-groups"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Lists CloudWatch log groups."}

    return {"command": "echo 'Unsupported CloudWatch intent'", "explanation": "Unsupported intent."}

def validate(intent, entities, aws_session=None):
    return {"status": "valid"}

def get_service():
    return {"name": SERVICE_NAME, "intents": INTENTS, "generate_command": generate_command, "validate": validate}