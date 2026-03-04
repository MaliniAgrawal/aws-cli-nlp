# src/core/clipboard.py
from typing import Tuple

def copy_to_clipboard(text: str) -> Tuple[bool, str]:
    """
    Copies text to clipboard (best-effort).
    Never raises; returns (ok, message).
    """
    try:
        import pyperclip
        if not text:
            return False, "Nothing to copy (empty command)."
        pyperclip.copy(text)
        return True, "✅ Copied command to clipboard."
    except Exception as e:
        return False, f"⚠ Clipboard copy failed: {e}"
