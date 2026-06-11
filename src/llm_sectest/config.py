"""Run configuration for a scan. Target endpoint is config, not code."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunConfig:
    base_url: str = "http://localhost:8000"
    chat_path: str = "/api/chat"
    html_path: str = "/chat"
    model_label: str = "llama3.2:3b"
    attempts: int = 5
    payloads_glob: str = "payloads/*.yaml"
    output_dir: str = "reports"
    timeout: float = 120.0
