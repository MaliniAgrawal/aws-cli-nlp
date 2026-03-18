import sys

from src import aws_nlp


def test_history_mode_compat(monkeypatch, capsys):
    # Entry with old key 'execution_mode'
    entries = [
        {
            "timestamp": "1",
            "service": "s3",
            "safety_level": "SAFE",
            "command": "aws s3 ls",
            "query": "list s3",
            "execution_allowed": False,
            "execution_mode": "manual",
        }
    ]
    monkeypatch.setattr("src.core.history.read_history", lambda limit=None: entries)
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "history"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "manual" in out


def test_execute_no_prompt_blocks(monkeypatch, capsys):
    # Generate a destructive operation
    fake_result = {
        "command": "aws s3 rb s3://bucket --force",
        "safety": {"level": "DESTRUCTIVE"},
        "intent": "delete",
    }
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)
    monkeypatch.setattr(
        sys, "argv", ["aws-nlp", "--execute", "--no-prompt", "delete s3 bucket x"]
    )
    try:
        aws_nlp.main()
    except SystemExit as e:
        assert e.code == 2
    out = capsys.readouterr().out
    assert "--no-prompt blocks interactive execution" in out
