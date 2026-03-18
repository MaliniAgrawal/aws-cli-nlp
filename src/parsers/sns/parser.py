SERVICE_NAME = "sns"
INTENTS = ["create_sns_topic", "list_sns_topics"]


def generate_command(intent, entities):
    if intent == "create_sns_topic":
        topic = entities.get("topic", "my-topic")
        return {
            "command": f"aws sns create-topic --name {topic}",
            "explanation": f"Creates SNS topic '{topic}'.",
        }
    if intent == "list_sns_topics":
        return {"command": "aws sns list-topics", "explanation": "Lists SNS topics."}


def validate(intent, entities, aws_session=None):
    return {"status": "unknown", "reason": "validation not implemented"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
