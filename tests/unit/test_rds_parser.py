from src.parsers.rds import parser as rds_parser


def test_create_rds_instance():
    result = rds_parser.generate_command("create_rds_instance", {"db": "testdb"})
    assert "create-db-instance" in result["command"]
    assert "testdb" in result["command"]


def test_list_rds_instances():
    result = rds_parser.generate_command("list_rds_instances", {})
    assert result["command"] == "aws rds describe-db-instances"
    assert "Lists RDS DB instances" in result["explanation"]


def test_get_service():
    service = rds_parser.get_service()
    assert service["name"] == "rds"
    assert "create_rds_instance" in service["intents"]
    assert "list_rds_instances" in service["intents"]
