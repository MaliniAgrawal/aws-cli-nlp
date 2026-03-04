import sys
import builtins
import io
from src import aws_nlp


def test_history_filters(monkeypatch, capsys):
    entries = [
        {"timestamp": "1", "service": "s3", "safety_level": "DESTRUCTIVE", "command": "rm -rf /", "query": "delete bucket"},
        {"timestamp": "2", "service": "ec2", "safety_level": "SAFE", "command": "aws ec2 describe-instances", "query": "list ec2"},
    ]

    monkeypatch.setattr('src.core.history.read_history', lambda limit=None: entries)
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "history", "--history-service", "s3"])

    try:
        aws_nlp.main()
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert "s3" in captured.out
    assert "ec2" not in captured.out

    # Test safety filter
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "history", "--history-safety", "DESTRUCTIVE"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "DESTRUCTIVE" in captured.out or "delete bucket" in captured.out


def test_no_prompt_mode(monkeypatch):
    # Mock generator to return a result and ensure input() is NOT called
    fake_result = {"command": "echo hi", "safety": {"level": "SAFE"}, "intent": "say-hi"}
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)

    # If input is called, raise to fail the test
    monkeypatch.setattr(builtins, "input", lambda prompt='': (_ for _ in ()).throw(RuntimeError("should_not_prompt")))

    monkeypatch.setattr(sys, "argv", ["aws-nlp", "list s3 buckets", "--no-prompt"])
    try:
        aws_nlp.main()
    except SystemExit:
        # acceptable; ensure no prompt
        pass
