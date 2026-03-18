from src.core import aws_validator

SERVICE_NAME = "dynamodb"
INTENTS = ["create_dynamodb_table", "list_dynamodb_tables"]


def generate_command(intent, entities):
    region_flag = f" --region {entities['region']}" if entities.get("region") else ""

    if intent == "create_dynamodb_table":
        table = entities.get("table", "MyTable")
        # simple template: partition key id:string
        cmd = f"aws dynamodb create-table --table-name {table} --attribute-definitions AttributeName=Id,AttributeType=S --key-schema AttributeName=Id,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5{region_flag}"
        return {
            "command": cmd,
            "explanation": f"Creates DynamoDB table '{table}' with a simple string primary key 'Id'.",
        }
    if intent == "list_dynamodb_tables":
        return {
            "command": f"aws dynamodb list-tables{region_flag}",
            "explanation": "Lists DynamoDB tables.",
        }


def validate(intent, entities, aws_session=None):
    if intent == "list_dynamodb_tables":
        return aws_validator.list_dynamodb_tables(aws_session=aws_session)
    # create table validation not implemented (name uniqueness implicit)
    return {
        "status": "unknown",
        "reason": "validation not implemented for create_dynamodb_table",
    }


def get_service():
    return {
        "name": SERVICE_NAME,
        "intents": INTENTS,
        "generate_command": generate_command,
        "validate": validate,
    }
