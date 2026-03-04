import sys
import builtins

from src import aws_nlp
import src.core.clipboard as clipboard


def test_copy_flag(monkeypatch):
    # Mock generate_command_sync to return a deterministic command
    fake_result = {"command": "aws s3 ls", "safety": {"level": "SAFE"}, "intent": "list"}
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)

    # Provide a fake clipboard helper that records the copied value
    copied = {}
    def fake_copy(text):
        copied['value'] = text
        return True, "Copied"
    monkeypatch.setattr(clipboard, "copy_to_clipboard", fake_copy)

    # Avoid interactive prompt by returning 'n' to the execute prompt
    monkeypatch.setattr(builtins, "input", lambda prompt='': 'n')

    # Run CLI with --copy flag
    monkeypatch.setattr(sys, "argv", ["aws-nlp", "list s3 buckets", "--copy"])

    try:
        aws_nlp.main()
    except SystemExit:
        # main uses sys.exit at the end; ignore it for this test
        pass

    assert copied.get("value") == "aws s3 ls"
