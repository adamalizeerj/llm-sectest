"""Scan engine: load payloads, run the OWASP battery, score, return a Report."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from llm_sectest.client import TargetClient, TargetConfig
from llm_sectest.config import RunConfig
from llm_sectest.oracles import Sentinels
from llm_sectest.payloads import AttackCase, load_categories


@dataclass
class CaseResult:
    case_id: str
    technique: str
    channel: str
    succeeded: bool
    attempts_used: int
    response_excerpt: str


@dataclass
class Finding:
    owasp: str
    name: str
    severity: str
    status: str
    note: str | None
    winning_case: str | None
    winning_technique: str | None
    winning_payload: str | None
    response_excerpt: str | None
    case_results: list[CaseResult] = field(default_factory=list)


@dataclass
class Report:
    metadata: dict
    findings: list[Finding]
    summary: dict


def _excerpt(text: str, n: int = 300) -> str:
    return " ".join(text.split())[:n]


def _run_case(client: TargetClient, case: AttackCase, s: Sentinels, attempts: int):
    last = ""
    for i in range(attempts):
        resp = client.chat_html(case.payload) if case.channel == "html" else client.chat(case.payload)
        last = resp
        if case.oracle(resp, s):
            return True, i + 1, resp
    return False, attempts, last


def _summarize(findings: list[Finding]) -> dict:
    by_status: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for f in findings:
        by_status[f.status] = by_status.get(f.status, 0) + 1
        if f.status == "vulnerable":
            by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
    return {
        "total_categories": len(findings),
        "vulnerable": by_status.get("vulnerable", 0),
        "not_exploited": by_status.get("not_exploited", 0),
        "by_severity_vulnerable": by_sev,
    }


def run_scan(config: RunConfig, sentinels: Sentinels | None = None) -> Report:
    sentinels = sentinels or Sentinels()
    client = TargetClient(TargetConfig(
        base_url=config.base_url, chat_path=config.chat_path,
        html_path=config.html_path, timeout=config.timeout))
    if not client.reachable():
        raise ConnectionError(f"target not reachable at {config.base_url}")

    findings: list[Finding] = []
    for cat in load_categories(config.payloads_glob):
        case_results: list[CaseResult] = []
        winner: AttackCase | None = None
        win_resp: str | None = None
        for case in cat.cases:
            ok, n, resp = _run_case(client, case, sentinels, config.attempts)
            case_results.append(CaseResult(
                case.id, case.technique, case.channel, ok,
                n if ok else config.attempts, _excerpt(resp)))
            if ok:
                winner, win_resp = case, resp
                break  # short-circuit: category is proven exploitable
        findings.append(Finding(
            owasp=cat.owasp, name=cat.name, severity=cat.severity,
            status="vulnerable" if winner else "not_exploited", note=cat.note,
            winning_case=winner.id if winner else None,
            winning_technique=winner.technique if winner else None,
            winning_payload=winner.payload if winner else None,
            response_excerpt=_excerpt(win_resp) if win_resp else None,
            case_results=case_results,
        ))

    metadata = {
        "tool": "llm-sectest",
        "owasp_version": "OWASP Top 10 for LLM Applications 2025",
        "target": config.base_url,
        "model": config.model_label,
        "attempts_per_payload": config.attempts,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    return Report(metadata=metadata, findings=findings, summary=_summarize(findings))
