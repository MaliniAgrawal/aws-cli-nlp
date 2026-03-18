import sys

from src import aws_nlp


def test_non_execute_shows_instruction(monkeypatch, capsys):
    fake_result = {
        "command": "echo hi",
        "safety": {"level": "SAFE"},
        "intent": "say-hi",
    }
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "list s3 buckets"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "To execute this command" in out
    assert "--execute" in out


def test_non_execute_json_no_instruction(monkeypatch, capsys):
    fake_result = {
        "command": "echo hi",
        "safety": {"level": "SAFE"},
        "intent": "say-hi",
    }
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "--json", "list s3 buckets"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    # JSON output only; no instruction
    assert "To execute this command" not in out
