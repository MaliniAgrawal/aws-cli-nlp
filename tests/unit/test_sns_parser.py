import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from parsers.sns import parser as sns_parser

def test_create_sns_topic():
    result = sns_parser.generate_command("create_sns_topic", {"topic": "test-topic"})
    assert "create-topic" in result["command"]
    assert "test-topic" in result["command"]

def test_list_sns_topics():
    result = sns_parser.generate_command("list_sns_topics", {})
    assert result["command"] == "aws sns list-topics"

def test_get_service():
    service = sns_parser.get_service()
    assert service["name"] == "sns"
    assert len(service["intents"]) == 2