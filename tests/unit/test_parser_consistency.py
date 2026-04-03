import importlib
import inspect
import pkgutil

from src.core.base_parser import BaseParser
from src.core.registry import PARSERS_PKG, ServiceRegistry


def _parser_modules():
    pkg = importlib.import_module(PARSERS_PKG)
    for _, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        if ispkg and not name.startswith("_"):
            yield importlib.import_module(f"{PARSERS_PKG}.{name}.parser")


def _sample_entities(intent: str) -> dict:
    samples = {
        "create_cloudformation_stack": {"stack": "demo-stack"},
        "create_dynamodb_table": {"table": "Orders"},
        "start_ec2_instance": {"instance_ids": ["i-0123456789abcdef0"]},
        "stop_ec2_instance": {"instance_ids": ["i-0123456789abcdef0"]},
        "terminate_ec2_instance": {"instance_ids": ["i-0123456789abcdef0"]},
        "create_ec2_keypair": {"key_name": "mykey"},
        "create_ecr_repository": {"repository": "my-repo"},
        "create_iam_user": {"user": "DevUser"},
        "delete_iam_user": {"user": "DevUser"},
        "attach_user_policy": {
            "user": "DevUser",
            "policy": "ReadOnlyAccess",
        },
        "detach_user_policy": {
            "user": "DevUser",
            "policy": "ReadOnlyAccess",
        },
        "list_attached_user_policies": {"user": "DevUser"},
        "invoke_lambda_function": {"function": "test-func"},
        "delete_rds_instance": {"db": "testdb"},
        "create_secret": {"secret_name": "mysecret"},
        "create_sns_topic": {"topic": "test-topic"},
        "create_sqs_queue": {"queue": "test-queue"},
        "get_ssm_parameter": {"name": "/my/parameter"},
        "put_ssm_parameter": {"name": "/my/parameter", "value": "secret"},
        "create_s3_bucket": {"bucket": "demo-bucket"},
        "delete_s3_bucket": {"bucket": "demo-bucket"},
        "list_s3_objects": {"bucket": "demo-bucket"},
        "put_s3_object": {
            "bucket": "demo-bucket",
            "key": "upload.dat",
            "local_path": "./file",
        },
        "create_rds_instance": {"db": "testdb"},
        "get_secret": {"secret_id": "my/secret"},
    }
    return samples.get(intent, {})


def test_all_parsers_implement_base_parser_contract():
    for mod in _parser_modules():
        parser_classes = [
            cls
            for _, cls in inspect.getmembers(mod, inspect.isclass)
            if cls is not BaseParser and issubclass(cls, BaseParser)
        ]
        assert parser_classes, f"{mod.__name__} is missing a BaseParser implementation"

        parser = parser_classes[0]()
        service_dict = parser.to_service_dict()

        assert callable(service_dict["generate_command"])
        assert callable(service_dict["validate"])
        assert isinstance(parser.get_service_name(), str)
        assert isinstance(parser.get_intents(), list)
        assert isinstance(parser.get_examples(), list)


def test_all_parser_generate_command_results_keep_command_and_explanation():
    for mod in _parser_modules():
        service = mod.get_service()
        for intent in service["intents"]:
            result = service["generate_command"](intent, _sample_entities(intent))
            assert isinstance(
                result, dict
            ), f"{mod.__name__}:{intent} did not return a dict"
            assert "command" in result, f"{mod.__name__}:{intent} missing command"
            assert (
                "explanation" in result
            ), f"{mod.__name__}:{intent} missing explanation"


def test_registry_stores_class_based_parsers_as_objects():
    test_registry = ServiceRegistry()
    test_registry.autodiscover()

    assert test_registry.services, "Expected autodiscover to register services"

    for service_name, service in test_registry.services.items():
        if isinstance(service, dict):
            continue
        assert isinstance(
            service, BaseParser
        ), f"{service_name} should be stored as a parser object"
