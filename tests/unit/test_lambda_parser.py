import importlib

lambda_parser = importlib.import_module("src.parsers.lambda.parser")


def test_list_lambda_functions():
    result = lambda_parser.generate_command(
        "list_lambda_functions", {"region": "us-west-1"}
    )
    assert "list-functions" in result["command"]
    assert "us-west-1" in result["command"]


def test_invoke_lambda_function():
    result = lambda_parser.generate_command(
        "invoke_lambda_function", {"function": "test-func", "region": "us-east-1"}
    )
    assert "invoke" in result["command"]
    assert "test-func" in result["command"]
    assert "us-east-1" in result["command"]


def test_get_service():
    service = lambda_parser.get_service()
    assert service["name"] == "lambda"
    assert "list_lambda_functions" in service["intents"]
    assert "invoke_lambda_function" in service["intents"]
