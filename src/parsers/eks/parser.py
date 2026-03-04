SERVICE_NAME = "eks"
INTENTS = ["list_eks_clusters"]

def generate_command(intent, entities):
    region = entities.get("region")

    if intent == "list_eks_clusters":
        cmd = "aws eks list-clusters"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Lists EKS clusters."}

    return {"command": "echo 'Unsupported EKS intent'", "explanation": "Unsupported intent."}

def validate(intent, entities, aws_session=None):
    return {"status": "valid"}

def get_service():
    return {"name": SERVICE_NAME, "intents": INTENTS, "generate_command": generate_command, "validate": validate}