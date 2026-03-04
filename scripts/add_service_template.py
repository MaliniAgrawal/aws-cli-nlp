"""
Add a new service scaffold to src/core/aws_parsers/
usage: python scripts/add_service_template.py myservice
"""
import sys, os
TEMPLATE = """SERVICE_NAME = "{service}"
INTENTS = ["example_intent"]

def generate_command(intent, entities):
    return {{"command":"echo 'not implemented'","explanation":"Not implemented"}}

def validate(intent, entities, aws_session=None):
    return {{"status":"unknown","reason":"validation disabled"}}

def get_service():
    return {{"name": SERVICE_NAME, "intents": INTENTS, "generate_command": generate_command, "validate": validate}}
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: add_service_template.py <service_name>")
        sys.exit(1)
    name = sys.argv[1].lower()
    dest = os.path.join("src", "core", "aws_parsers", f"{name}_parser.py")
    with open(dest, "w", encoding="utf8") as f:
        f.write(TEMPLATE.format(service=name))
    print("Wrote", dest)
