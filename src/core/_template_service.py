# small helper base for parsers - each parser should follow this simple contract
SERVICE_NAME = None
INTENTS = []

def generate_command(intent: str, entities: dict) -> dict:
    """
    Return { command: str, explanation: str }
    """
    raise NotImplementedError

def validate(intent: str, entities: dict, aws_session=None) -> dict:
    """
    Try to validate intent/params using boto3 session if present.
    Return { status: 'valid'|'invalid'|'unknown', reason: str, extra: {} }
    """
    return {"status": "unknown", "reason": "Validation not implemented", "extra": {}}

def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate
    }
