from src.parsers.cloudformation import parser as cf_parser
from src.parsers.cloudwatch import parser as cw_parser
from src.parsers.ecr import parser as ecr_parser
from src.parsers.eks import parser as eks_parser
from src.parsers.secretsmanager import parser as sm_parser
from src.parsers.ssm import parser as ssm_parser


def test_ecr_service():
    service = ecr_parser.get_service()
    assert service["name"] == "ecr"
    result = ecr_parser.generate_command("list_ecr_repositories", {})
    assert "describe-repositories" in result["command"]


def test_eks_service():
    service = eks_parser.get_service()
    assert service["name"] == "eks"
    result = eks_parser.generate_command("list_eks_clusters", {})
    assert "list-clusters" in result["command"]


def test_cloudformation_service():
    service = cf_parser.get_service()
    assert service["name"] == "cloudformation"
    result = cf_parser.generate_command("list_cloudformation_stacks", {})
    assert "list-stacks" in result["command"]


def test_cloudwatch_service():
    service = cw_parser.get_service()
    assert service["name"] == "cloudwatch"
    result = cw_parser.generate_command("list_cloudwatch_metrics", {})
    assert "list-metrics" in result["command"]


def test_ssm_service():
    service = ssm_parser.get_service()
    assert service["name"] == "ssm"
    result = ssm_parser.generate_command("get_ssm_parameter", {"name": "/test/param"})
    assert "get-parameter" in result["command"]


def test_secretsmanager_service():
    service = sm_parser.get_service()
    assert service["name"] == "secretsmanager"
    result = sm_parser.generate_command("get_secret", {"secret_id": "test-secret"})
    assert "get-secret-value" in result["command"]
