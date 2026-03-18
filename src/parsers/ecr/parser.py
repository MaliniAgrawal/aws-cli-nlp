SERVICE_NAME = "ecr"
INTENTS = ["list_ecr_repositories", "create_ecr_repository"]


def generate_command(intent, entities):
    region = entities.get("region")

    if intent == "list_ecr_repositories":
        cmd = "aws ecr describe-repositories"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Lists ECR repositories."}

    if intent == "create_ecr_repository":
        repo = entities.get("repository", "my-repo")
        cmd = f"aws ecr create-repository --repository-name {repo}"
        if region:
            cmd += f" --region {region}"
        return {"command": cmd, "explanation": "Creates an ECR repo."}

    return {
        "command": "echo 'Unsupported ECR intent'",
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
