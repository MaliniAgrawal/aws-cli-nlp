"""
CI mode exit-code contract tests.

Two layers:
  - ci_exit_code() unit tests: pure function, no I/O, covers every code path.
  - main() --ci integration tests: drives the full CLI path and asserts on
    sys.exit code, stdout JSON shape, and stderr summary line.

Exit-code contract (from src/aws_nlp.py):
  0  allowed          SAFE, no confirmation needed
  2  requires review  MUTATING / DESTRUCTIVE / SECURITY_SENSITIVE
  3  blocked          org policy decision == block
  4  unknown intent   unrecognised or unsupported input
  5  internal error   exception inside ci_exit_code
"""

import json
import sys

import pytest

from src import aws_nlp
from src.cli.ci import ci_exit_code

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _result(
    intent,
    level,
    *,
    requires_confirmation=None,
    pro_enabled=False,
    pro_decision="allow",
    pro_reason="",
):
    """Build a minimal generate_command_sync-shaped result dict."""
    if requires_confirmation is None:
        requires_confirmation = level in (
            "MUTATING",
            "DESTRUCTIVE",
            "SECURITY_SENSITIVE",
        )
    return {
        "command": f"aws fake {intent}",
        "explanation": "test",
        "intent": intent,
        "entities": {},
        "safety": {
            "level": level,
            "requires_confirmation": requires_confirmation,
            "confirmation_hint": "",
        },
        "meta": {
            "service": "test",
            "confidence": "high",
            "generated_by": "rule_engine",
            "version": "1.0.0",
        },
        "pro_enforcement": {
            "enabled": pro_enabled,
            "decision": pro_decision,
            "reason": pro_reason,
            "policy_version": None,
        },
    }


def _run_ci(monkeypatch, capsys, query, fake_result, extra_argv=None):
    """Run main() in --ci mode and return (exit_code, stdout_text, stderr_text)."""
    monkeypatch.setattr(aws_nlp, "generate_command_sync", lambda q: fake_result)
    argv = ["aws-nlp", "--ci", query] + (extra_argv or [])
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        aws_nlp.main()
    captured = capsys.readouterr()
    return exc.value.code, captured.out, captured.err


# ---------------------------------------------------------------------------
# ci_exit_code() unit tests
# ---------------------------------------------------------------------------


class TestCiExitCodeUnit:

    def test_safe_returns_0(self):
        result = _result("list_s3_buckets", "SAFE")
        assert ci_exit_code(result) == 0

    def test_safe_allow_confirm_still_0(self):
        result = _result("list_s3_buckets", "SAFE")
        assert ci_exit_code(result, fail_on_confirm=False) == 0

    def test_mutating_returns_2(self):
        result = _result("create_s3_bucket", "MUTATING")
        assert ci_exit_code(result) == 2

    def test_destructive_returns_2(self):
        result = _result("delete_s3_bucket", "DESTRUCTIVE")
        assert ci_exit_code(result) == 2

    def test_security_sensitive_returns_2(self):
        result = _result("create_iam_user", "SECURITY_SENSITIVE")
        assert ci_exit_code(result) == 2

    def test_mutating_allow_confirm_returns_0(self):
        result = _result("create_s3_bucket", "MUTATING")
        assert ci_exit_code(result, fail_on_confirm=False) == 0

    def test_destructive_allow_confirm_returns_0(self):
        result = _result("delete_s3_bucket", "DESTRUCTIVE")
        assert ci_exit_code(result, fail_on_confirm=False) == 0

    def test_unknown_intent_returns_4(self):
        result = _result("unknown", "UNKNOWN")
        assert ci_exit_code(result) == 4

    def test_unsupported_intent_string_returns_4(self):
        result = _result("unsupported_intent", "UNKNOWN")
        assert ci_exit_code(result) == 4

    def test_empty_intent_returns_4(self):
        result = _result("", "UNKNOWN")
        assert ci_exit_code(result) == 4

    def test_unknown_safety_level_returns_4(self):
        # Known intent but safety level not in the map → UNKNOWN
        result = _result("create_sqs_queue", "UNKNOWN")
        assert ci_exit_code(result) == 4

    def test_internal_error_returns_5(self):
        # Passing a non-dict triggers the except branch
        assert ci_exit_code(None) == 5  # type: ignore[arg-type]

    def test_pro_block_returns_3(self):
        result = _result(
            "delete_s3_bucket",
            "DESTRUCTIVE",
            pro_enabled=True,
            pro_decision="block",
            pro_reason="blocked by org policy",
        )
        assert ci_exit_code(result) == 3

    def test_pro_confirm_returns_2(self):
        result = _result(
            "create_s3_bucket", "MUTATING", pro_enabled=True, pro_decision="confirm"
        )
        assert ci_exit_code(result) == 2

    def test_pro_confirm_allow_confirm_returns_0(self):
        result = _result(
            "create_s3_bucket", "MUTATING", pro_enabled=True, pro_decision="confirm"
        )
        assert ci_exit_code(result, fail_on_confirm=False) == 0

    def test_pro_allow_safe_returns_0(self):
        result = _result(
            "list_s3_buckets", "SAFE", pro_enabled=True, pro_decision="allow"
        )
        assert ci_exit_code(result) == 0


# ---------------------------------------------------------------------------
# main() --ci integration tests
# ---------------------------------------------------------------------------


class TestCiMainIntegration:

    def test_safe_exits_0_and_emits_json(self, monkeypatch, capsys):
        fake = _result("list_s3_buckets", "SAFE")
        code, out, err = _run_ci(monkeypatch, capsys, "list s3 buckets", fake)

        assert code == 0
        parsed = json.loads(out)
        assert parsed["intent"] == "list_s3_buckets"
        assert parsed["safety"]["level"] == "SAFE"

    def test_safe_stderr_summary(self, monkeypatch, capsys):
        fake = _result("list_s3_buckets", "SAFE")
        code, out, err = _run_ci(monkeypatch, capsys, "list s3 buckets", fake)

        assert "safety=SAFE" in err
        assert "exit_code=0" in err

    def test_mutating_exits_2(self, monkeypatch, capsys):
        fake = _result("create_s3_bucket", "MUTATING")
        code, out, err = _run_ci(monkeypatch, capsys, "create s3 bucket my-data", fake)

        assert code == 2
        assert "exit_code=2" in err

    def test_destructive_exits_2(self, monkeypatch, capsys):
        fake = _result("delete_s3_bucket", "DESTRUCTIVE")
        code, out, err = _run_ci(monkeypatch, capsys, "delete s3 bucket old-logs", fake)

        assert code == 2
        assert "exit_code=2" in err

    def test_security_sensitive_exits_2(self, monkeypatch, capsys):
        fake = _result("create_iam_user", "SECURITY_SENSITIVE")
        code, out, err = _run_ci(monkeypatch, capsys, "create iam user DevUser", fake)

        assert code == 2
        assert "exit_code=2" in err

    def test_unknown_intent_exits_4(self, monkeypatch, capsys):
        fake = _result("unknown", "UNKNOWN")
        code, out, err = _run_ci(monkeypatch, capsys, "xyzzy foobar", fake)

        assert code == 4
        assert "exit_code=4" in err

    def test_allow_confirm_flag_downgrades_mutating_to_0(self, monkeypatch, capsys):
        fake = _result("create_s3_bucket", "MUTATING")
        code, out, err = _run_ci(
            monkeypatch,
            capsys,
            "create s3 bucket staging",
            fake,
            extra_argv=["--allow-confirm"],
        )

        assert code == 0
        assert "exit_code=0" in err

    def test_allow_confirm_flag_downgrades_destructive_to_0(self, monkeypatch, capsys):
        fake = _result("delete_s3_bucket", "DESTRUCTIVE")
        code, out, err = _run_ci(
            monkeypatch,
            capsys,
            "delete s3 bucket old-logs",
            fake,
            extra_argv=["--allow-confirm"],
        )

        assert code == 0

    def test_stdout_is_valid_json(self, monkeypatch, capsys):
        fake = _result("delete_s3_bucket", "DESTRUCTIVE")
        _, out, _ = _run_ci(monkeypatch, capsys, "delete s3 bucket old-logs", fake)

        # Must parse without error and contain the required top-level keys
        parsed = json.loads(out)
        for key in ("command", "intent", "safety", "meta"):
            assert key in parsed

    def test_stdout_json_not_polluted_by_stderr(self, monkeypatch, capsys):
        fake = _result("list_s3_buckets", "SAFE")
        _, out, err = _run_ci(monkeypatch, capsys, "list s3 buckets", fake)

        # stderr summary must not appear in stdout
        assert "[CI]" not in out
        assert "[CI]" in err

    def test_ci_never_executes(self, monkeypatch, capsys):
        """--ci must never call execute_with_confirmation regardless of safety level."""
        executed = {"called": False}

        def _fake_execute(**kwargs):
            executed["called"] = True
            return {}

        monkeypatch.setattr(
            "src.core.executor.execute_with_confirmation", _fake_execute, raising=False
        )
        fake = _result("delete_s3_bucket", "DESTRUCTIVE")
        _run_ci(monkeypatch, capsys, "delete s3 bucket old-logs", fake)

        assert not executed["called"]
