"""Load data-driven payload sets from YAML and resolve oracle specs to callables."""
from __future__ import annotations

import glob
from dataclasses import dataclass, field
from typing import Any, Callable

import yaml

from llm_sectest.oracles import (
    Sentinels,
    file_leaked,
    marker_echoed,
    reflected_unescaped,
    secret_disclosed,
    system_prompt_leaked,
)


@dataclass
class AttackCase:
    id: str
    technique: str
    payload: str
    oracle: Callable[[str, Sentinels], bool]
    channel: str = "chat"


@dataclass
class Category:
    owasp: str
    name: str
    severity: str = "Medium"
    note: str | None = None
    cases: list[AttackCase] = field(default_factory=list)


def build_oracle(spec: dict[str, Any]) -> Callable[[str, Sentinels], bool]:
    t = spec.get("type")
    if t == "marker":
        marker = spec["marker"]
        return lambda resp, s: marker_echoed(resp, marker)
    if t == "secret":
        return secret_disclosed
    if t == "system_prompt":
        return system_prompt_leaked
    if t == "file":
        return file_leaked
    if t == "reflected":
        marker = spec["marker"]
        return lambda resp, s: reflected_unescaped(resp, marker)
    raise ValueError(f"unknown oracle type: {t!r}")


def load_categories(glob_pattern: str = "payloads/*.yaml") -> list[Category]:
    files = sorted(glob.glob(glob_pattern))
    if not files:
        raise FileNotFoundError(f"no payload files matched {glob_pattern!r}")
    categories: list[Category] = []
    for path in files:
        with open(path) as fh:
            data = yaml.safe_load(fh) or {}
        for c in data.get("categories", []):
            cases = [
                AttackCase(
                    id=case["id"],
                    technique=case["technique"],
                    payload=case["payload"],
                    oracle=build_oracle(case["oracle"]),
                    channel=case.get("channel", "chat"),
                )
                for case in c.get("cases", [])
            ]
            categories.append(Category(
                owasp=c["owasp"], name=c["name"],
                severity=c.get("severity", "Medium"),
                note=c.get("note"), cases=cases,
            ))
    return categories
