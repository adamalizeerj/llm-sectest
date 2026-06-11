"""Render a Report to structured JSON and a human-readable Markdown document."""
from __future__ import annotations

import json
from dataclasses import asdict

from llm_sectest.engine import Report


def to_json(report: Report) -> str:
    return json.dumps({
        "metadata": report.metadata,
        "summary": report.summary,
        "findings": [asdict(f) for f in report.findings],
    }, indent=2)


def to_markdown(report: Report) -> str:
    m, s = report.metadata, report.summary
    out: list[str] = []
    out.append("# LLM Security Test Report")
    out.append("")
    out.append(f"- Tool: {m['tool']}")
    out.append(f"- Standard: {m['owasp_version']}")
    out.append(f"- Target: {m['target']}")
    out.append(f"- Model: {m['model']}")
    out.append(f"- Attempts per payload: {m['attempts_per_payload']}")
    out.append(f"- Generated (UTC): {m['timestamp_utc']}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"{s['vulnerable']} of {s['total_categories']} OWASP categories exploited "
               f"through the model interface.")
    out.append("")
    out.append("## OWASP coverage")
    out.append("")
    out.append("| OWASP | Category | Severity | Status | Winning technique |")
    out.append("|-------|----------|----------|--------|-------------------|")
    for f in report.findings:
        out.append(f"| {f.owasp} | {f.name} | {f.severity} | {f.status} "
                   f"| {f.winning_technique or '-'} |")
    out.append("")
    out.append("## Findings")
    for f in report.findings:
        out.append("")
        out.append(f"### {f.owasp} {f.name} ({f.severity})")
        out.append("")
        out.append(f"Status: {f.status}")
        if f.note:
            out.append("")
            out.append(f"Note: {f.note}")
        if f.status == "vulnerable":
            out.append("")
            out.append(f"Winning payload ({f.winning_case}, technique: {f.winning_technique}):")
            out.append("")
            out.append("```")
            out.append(f.winning_payload or "")
            out.append("```")
            out.append("")
            out.append("Model response excerpt:")
            out.append("")
            out.append("```")
            out.append(f.response_excerpt or "")
            out.append("```")
    out.append("")
    return "\n".join(out)
