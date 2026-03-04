import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from parsers.dynamodb import parser as dynamodb_parser

def test_create_dynamodb_table():
    result = dynamodb_parser.generate_command("create_dynamodb_table", {"table": "Orders"})
    assert "create-table" in result["command"]
    assert "Orders" in result["command"]
    assert result["explanation"].startswith("Creates DynamoDB table")

def test_list_dynamodb_tables():
    result = dynamodb_parser.generate_command("list_dynamodb_tables", {})
    assert result["command"] == "aws dynamodb list-tables"
    assert "Lists DynamoDB tables" in result["explanation"]

def test_get_service():
    service = dynamodb_parser.get_service()
    assert service["name"] == "dynamodb"
    assert "create_dynamodb_table" in service["intents"]
    assert "list_dynamodb_tables" in service["intents"]