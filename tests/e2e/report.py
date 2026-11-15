"""Turn the e2e findings into a Markdown report for the Impeccable review (#207).

python -m tests.e2e.report     # after: pytest -m e2e --no-cov
"""

import json
from collections import defaultdict
from pathlib import Path

ARTIFACTS = Path(__file__).parent / "artifacts"

TITLES = {
    "console-error": "Console errors",
    "failed-request": "Failed requests",
    "horizontal-overflow": "Sideways scroll",
    "contrast": "Text contrast below WCAG AA",
    "focus-visible": "No visible keyboard focus (desktop)",
    "reduced-motion": "Long motion with reduced motion on",
    "tap-target": "Tap targets under 44x44px (mobile)",
}


def build(findings: Path = ARTIFACTS / "findings.jsonl") -> str:
    rows = [json.loads(line) for line in findings.read_text(encoding="utf-8").splitlines()]
    grouped: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    shots: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        grouped[row["check"]][row["detail"]].add(f"{row['page']} ({row['device']})")
        if row.get("screenshot"):
            shots[row["check"]].add(row["screenshot"])
    out = ["# Yearnly e2e design findings", "", f"{len(rows)} findings from `pytest -m e2e`.", ""]
    for check in sorted(grouped, key=lambda c: list(TITLES).index(c) if c in TITLES else 99):
        details = grouped[check]
        out += [f"## {TITLES.get(check, check)} ({len(details)})", ""]
        for detail, pages in sorted(details.items(), key=lambda kv: -len(kv[1])):
            more = f", +{len(pages) - 6} more" if len(pages) > 6 else ""
            where = ", ".join(sorted(pages)[:6]) + more
            out.append(f"- {detail}: {where}")
        out += ["", "Screenshots: " + ", ".join(f"`{s}`" for s in sorted(shots[check])[:6]), ""]
    return "\n".join(out)


if __name__ == "__main__":
    report = ARTIFACTS / "findings.md"
    report.write_text(build(), encoding="utf-8")
    print(report)
