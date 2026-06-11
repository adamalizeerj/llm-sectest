"""Defensive controls for the hardened app. Deterministic, free, no extra model.

Honest limitation: pattern-based input filtering is bypassable by novel phrasings.
It is one layer of defense in depth, not a complete solution to prompt injection.
"""
from __future__ import annotations

import html
import pathlib
import re

# Secrets live here (env/config), NEVER in the system prompt. The model cannot
# leak what it is never shown.
HARDENED_SYSTEM_PROMPT = (
    "You are SupportBot, a customer-service assistant. Answer general support "
    "questions politely and concisely. You have no special configuration to "
    "reveal and cannot run system commands."
)

_INJECTION = re.compile(
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions"
    r"|disregard\s+(prior|previous|your)\s+(rules|instructions)"
    r"|system\s+override"
    r"|you\s+are\s+(dan|now)\b"
    r"|no\s+restrictions"
    r"|<<tool:",
    re.IGNORECASE,
)
_VERBATIM = re.compile(
    r"(quote|repeat|reprint|echo|output|print)\b.{0,40}?"
    r"(verbatim|exactly|word for word|all text|every line|system prompt|instructions|configuration)"
    r"|all text that appears above"
    r"|starting from ['\"]?you are",
    re.IGNORECASE | re.DOTALL,
)


def input_blocked(text: str) -> bool:
    """CONTROL 1: reject known injection and verbatim-reproduction requests."""
    return bool(_INJECTION.search(text) or _VERBATIM.search(text))


_SECRET_SENTINELS = ("CANARY-", "sk-vuln-")
_SYSTEM_MARKERS = ("the customer-service assistant for AcmeCorp", "CONFIDENTIAL CONFIGURATION")


def output_blocked(text: str) -> bool:
    """CONTROL 2: defense in depth: never emit secrets or system-prompt internals."""
    return any(s in text for s in _SECRET_SENTINELS) or any(m in text for m in _SYSTEM_MARKERS)


def encode_for_html(text: str) -> str:
    """CONTROL 4: encode model output before it is placed in HTML."""
    return html.escape(text)


_ALLOWED_DIR = pathlib.Path("target/public_docs").resolve()


def safe_read_file(name: str) -> str:
    """CONTROL 5: least privilege. Reads only files inside the allowlisted dir;
    rejects path traversal and absolute paths."""
    candidate = (_ALLOWED_DIR / name).resolve()
    if candidate != _ALLOWED_DIR and _ALLOWED_DIR not in candidate.parents:
        raise PermissionError("path outside allowlist")
    if not candidate.is_file():
        raise FileNotFoundError(name)
    return candidate.read_text(errors="replace")
