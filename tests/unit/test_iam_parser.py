from src.parsers.iam import parser as iamp


def test_list_users():
    r = iamp.generate_command("list_iam_users", {})
    assert "list-users" in r["command"]


def test_create_user():
    r = iamp.generate_command("create_iam_user", {"user": "DevUser"})
    assert "create-user" in r["command"]


def test_attach_policy_by_name():
    r = iamp.generate_command(
        "attach_user_policy",
        {"user": "DevUser", "policy": "ReadOnlyAccess"},
    )
    assert "arn:aws:iam::aws:policy/ReadOnlyAccess" in r["command"]


def test_attach_policy_by_arn():
    arn = "arn:aws:iam::aws:policy/AdministratorAccess"
    r = iamp.generate_command(
        "attach_user_policy",
        {"user": "DevUser", "policy": arn},
    )
    assert arn in r["command"]


def test_invalid_policy_name():
    try:
        iamp.generate_command(
            "attach_user_policy",
            {"user": "DevUser", "policy": "MyCustomPolicy"},
        )
        assert False
    except ValueError:
        assert True
