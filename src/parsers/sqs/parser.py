SERVICE_NAME = "sqs"
INTENTS = ["create_sqs_queue", "list_sqs_queues"]


def generate_command(intent, entities):
    if intent == "create_sqs_queue":
        q = entities.get("queue", "my-queue")
        return {
            "command": f"aws sqs create-queue --queue-name {q}",
            "explanation": f"Creates SQS queue '{q}'.",
        }
    if intent == "list_sqs_queues":
        return {"command": "aws sqs list-queues", "explanation": "Lists SQS queues."}


def validate(intent, entities, aws_session=None):
    return {"status": "unknown", "reason": "validation not implemented"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
