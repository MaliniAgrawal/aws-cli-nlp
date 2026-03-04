SERVICE_NAME = "rds"
INTENTS = ["create_rds_instance","list_rds_instances","delete_rds_instance"]

def generate_command(intent, entities):
    if intent == "create_rds_instance":
        db = entities.get("db","mydb")
        # Use AWS Secrets Manager for password - never hardcode passwords
        cmd = f"aws rds create-db-instance --db-instance-identifier {db} --db-instance-class db.t3.micro --engine mysql --allocated-storage 20 --master-username admin --manage-master-user-password"
        return {"command": cmd, "explanation": f"Creates RDS instance '{db}' with AWS-managed master password (stored in Secrets Manager)."}
    if intent == "list_rds_instances":
        return {"command":"aws rds describe-db-instances", "explanation":"Lists RDS DB instances."}
    if intent == "delete_rds_instance":
        db = entities.get("db")
        if not db:
            return {
                "command": "echo 'Missing DB instance identifier'",
                "explanation": "Cannot delete an RDS instance without a DB identifier.",
            }
        cmd = f"aws rds delete-db-instance --db-instance-identifier {db} --skip-final-snapshot"
        return {"command": cmd, "explanation": f"Deletes RDS instance '{db}' without taking a final snapshot."}

def validate(intent, entities, aws_session=None):
    return {"status":"unknown","reason":"validation not implemented"}

def get_service():
    return {"name": SERVICE_NAME, "intents": INTENTS, "generate_command": generate_command, "validate": validate}
