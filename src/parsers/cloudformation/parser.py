SERVICE_NAME = "cloudformation"
INTENTS = ["create_cloudformation_stack", "list_cloudformation_stacks"]


def generate_command(intent, entities):
    if intent == "create_cloudformation_stack":
        stack = entities.get("stack", "mystack")
        cmd = f"aws cloudformation create-stack --stack-name {stack} --template-body file://template.yaml"
        return {
            "command": cmd,
            "explanation": f"Creates CloudFormation stack '{stack}' using local template.yaml.",
        }
    if intent == "list_cloudformation_stacks":
        return {
            "command": "aws cloudformation list-stacks",
            "explanation": "Lists CloudFormation stacks.",
        }


def validate(intent, entities, aws_session=None):
    return {"status": "unknown", "reason": "validation not implemented"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
