"""HTTP client for a target LLM chat application under test."""
from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass
class TargetConfig:
    base_url: str = "http://localhost:8000"
    chat_path: str = "/api/chat"
    html_path: str = "/chat"
    timeout: float = 120.0


class TargetClient:
    """Black-box client: talks to the target only over HTTP, like a real attacker."""

    def __init__(self, config: TargetConfig | None = None) -> None:
        self.cfg = config or TargetConfig()

    def chat(self, message: str) -> str:
        url = self.cfg.base_url + self.cfg.chat_path
        r = httpx.post(url, json={"message": message}, timeout=self.cfg.timeout)
        r.raise_for_status()
        return r.json()["reply"]

    def chat_html(self, message: str) -> str:
        url = self.cfg.base_url + self.cfg.html_path
        r = httpx.get(url, params={"message": message}, timeout=self.cfg.timeout)
        r.raise_for_status()
        return r.text

    def reachable(self) -> bool:
        try:
            httpx.get(self.cfg.base_url + "/", timeout=5)
            return True
        except Exception:
            return False
