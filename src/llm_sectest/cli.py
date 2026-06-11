"""Command-line entry point: scan a target and write JSON + Markdown reports."""
from __future__ import annotations

import argparse
import os
import pathlib

from rich.console import Console
from rich.table import Table

from llm_sectest.config import RunConfig
from llm_sectest.engine import run_scan
from llm_sectest.report import to_json, to_markdown


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="llm-sectest",
        description="OWASP Top 10 for LLMs (2025) security scanner")
    p.add_argument("--base-url", default=os.environ.get("TARGET_BASE_URL", "http://localhost:8000"))
    p.add_argument("--model", default=os.environ.get("TARGET_MODEL", "llama3.2:3b"))
    p.add_argument("--attempts", type=int, default=int(os.environ.get("LLM_SECTEST_ATTEMPTS", "5")))
    p.add_argument("--payloads", default="payloads/*.yaml")
    p.add_argument("--out", default="reports")
    args = p.parse_args(argv)

    config = RunConfig(base_url=args.base_url, model_label=args.model,
                       attempts=args.attempts, payloads_glob=args.payloads,
                       output_dir=args.out)
    console = Console()
    console.print(f"[bold]Scanning[/bold] {config.base_url} "
                  f"({config.attempts} attempts/payload)...")
    report = run_scan(config)

    outdir = pathlib.Path(config.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "report.json").write_text(to_json(report))
    (outdir / "report.md").write_text(to_markdown(report))

    table = Table(title="OWASP Top 10 for LLMs - Findings")
    for col in ("OWASP", "Category", "Severity", "Status"):
        table.add_column(col)
    for f in report.findings:
        color = "red" if f.status == "vulnerable" else "yellow"
        table.add_row(f.owasp, f.name, f.severity, f"[{color}]{f.status}[/{color}]")
    console.print(table)
    console.print(f"Reports written to {outdir / 'report.json'} and {outdir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
