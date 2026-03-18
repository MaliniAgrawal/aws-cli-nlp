SERVICE_NAME = "ssm"
INTENTS = ["get_ssm_parameter", "put_ssm_parameter"]


def generate_command(intent, entities):
    region = entities.get("region")

    if intent == "get_ssm_parameter":
        name = entities.get("name", "/my/parameter")
        cmd = f"aws ssm get-parameter --name {name} --with-decryption"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Gets an SSM Parameter."}

    if intent == "put_ssm_parameter":
        name = entities.get("name", "/my/parameter")
        value = entities.get("value", "default")
        cmd = f'aws ssm put-parameter --name {name} --value "{value}" --type SecureString --overwrite'
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Stores a SecureString parameter."}

    return {
        "command": "echo 'Unsupported SSM intent'",
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
