SERVICE_NAME = "secretsmanager"
INTENTS = ["get_secret", "create_secret"]


def generate_command(intent, entities):
    if intent == "get_secret":
        secret = entities.get("secret_id", "my/secret")
        cmd = f"aws secretsmanager get-secret-value --secret-id {secret}"
        return {"command": cmd, "explanation": "Retrieves a secret."}

    if intent == "create_secret":
        name = entities.get("secret_name", "mysecret")
        cmd = f"aws secretsmanager create-secret --name {name} --secret-string file://secret.json"
        return {
            "command": cmd,
            "explanation": "Creates a new secret from file://secret.json (never hardcode secrets).",
        }

    return {
        "command": "echo 'Unsupported SecretsManager intent'",
        "explanation": "Unsupported intent.",
    }


def validate(intent, entities, aws_session=None):
    return {"status": "valid"}


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
