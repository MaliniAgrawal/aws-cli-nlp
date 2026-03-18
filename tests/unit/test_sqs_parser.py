from src.parsers.sqs import parser as sqs_parser


def test_create_sqs_queue():
    result = sqs_parser.generate_command("create_sqs_queue", {"queue": "test-queue"})
    assert "create-queue" in result["command"]
    assert "test-queue" in result["command"]


def test_list_sqs_queues():
    result = sqs_parser.generate_command("list_sqs_queues", {})
    assert result["command"] == "aws sqs list-queues"
    assert "Lists SQS queues" in result["explanation"]


def test_get_service():
    service = sqs_parser.get_service()
    assert service["name"] == "sqs"
    assert "create_sqs_queue" in service["intents"]
    assert "list_sqs_queues" in service["intents"]
