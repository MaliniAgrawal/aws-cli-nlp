import sys
import builtins
from src import aws_nlp
import src.core.clipboard as clipboard


def test_copy_with_json(monkeypatch, capsys):
    # Mock generate_command_sync to return a deterministic command
    fake_result = {"command": "aws s3 rb s3://demo-bucket --force", "safety": {"level": "DESTRUCTIVE"}, "intent": "delete"}
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)

    # Capture copy invocation
    copied = {}
    def fake_copy(text):
        copied['value'] = text
        return True, "✅ Copied command to clipboard."
    monkeypatch.setattr(clipboard, "copy_to_clipboard", fake_copy)

    # Run CLI with --json and --copy
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "--json", "--copy", "delete s3 bucket demo-bucket"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass

    captured = capsys.readouterr()
    out = captured.out
    err = captured.err
    assert '"command"' in out or '{' in out  # JSON printed
    assert copied.get('value') == "aws s3 rb s3://demo-bucket --force"
    assert "Copied" in err or "Copied" in err  # message printed to stderr for JSON mode


def test_explain_only_does_not_copy(monkeypatch):
    # Mock generate_command_sync to return a deterministic command
    fake_result = {"command": "aws s3 ls", "safety": {"level": "SAFE"}, "intent": "list"}
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)

    # If copy_to_clipboard is called, raise to fail the test
    def bad_copy(text):
        raise RuntimeError("copy_called")
    monkeypatch.setattr(clipboard, "copy_to_clipboard", bad_copy)

    # Run CLI with --explain-only and --copy
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "--explain-only", "--copy", "list s3 buckets"])
    try:
        aws_nlp.main()
    except SystemExit:
        pass
    # If bad_copy was called, it would have raised and failed the test
