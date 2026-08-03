#!/usr/bin/env python3
"""Certification gate for the SCLA lesson-video studio (stage 6 of PROCESS.md).

    python3 verify-certification.py --lesson <path/to/lessons/<program>/<stem>>

Grades `qa/certification.md` — the record the ORCHESTRATOR writes after the
check print and screening panel ran against the rendered MP4. It proves the
record is complete and internally honest; it cannot prove the runs happened —
that is why only the orchestrator, who read the Ringer run artifacts and
re-ran the verifiers, may write it.

Required shape:
  # Certification — <stem>
  ## Check Print  one line per lane — presence, layout, timing, fidelity —
                  each carrying PASS
  ## Screening    one line per persona (>=3), each ending in
                  'keep watching: yes|no'; a majority must be yes
  ## Open Findings   the word 'none' (a P0/P1 still open means NOT certified)
  ## Run          the Ringer run name(s) and a YYYY-MM-DD date

Exit 0 only when everything passes; every failure prints its reason.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LANES = ("presence", "layout", "timing", "fidelity")

fails: list[str] = []


def fail(msg: str) -> None:
    fails.append(msg)


def section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
                  text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lesson", required=True, type=Path,
                    help="lessons/<program>/<stem> directory")
    a = ap.parse_args()

    lesson = a.lesson.resolve()
    cert = lesson / "qa" / "certification.md"
    if not cert.exists():
        print(f"FAIL: {cert} missing — a lesson is certified only when the "
              f"check print + screening verdict is on disk")
        return 1
    text = cert.read_text(encoding="utf-8")

    if not re.search(r"^#\s+Certification", text, re.IGNORECASE | re.MULTILINE):
        fail(f"{cert}: must open with '# Certification — <stem>'")

    checkprint = section(text, "Check Print")
    if not checkprint:
        fail(f"{cert}: no '## Check Print' section")
    else:
        for lane in LANES:
            line = next((ln for ln in checkprint.splitlines()
                         if re.search(rf"\b{lane}\b", ln, re.IGNORECASE)), None)
            if line is None:
                fail(f"{cert}: Check Print has no line for the {lane} lane — all "
                     f"four lanes must have run")
            elif not re.search(r"\bPASS\b", line):
                fail(f"{cert}: {lane} lane line does not say PASS: {line.strip()!r}")

    screening = section(text, "Screening")
    if not screening:
        fail(f"{cert}: no '## Screening' section")
    else:
        votes = re.findall(r"keep watching:\s*(yes|no)\b", screening, re.IGNORECASE)
        if len(votes) < 3:
            fail(f"{cert}: Screening records {len(votes)} 'keep watching:' "
                 f"verdict(s) — the panel is at least 3 personas")
        elif sum(v.lower() == "yes" for v in votes) * 2 <= len(votes):
            fail(f"{cert}: screening panel majority would NOT keep watching "
                 f"({votes}) — not certifiable")

    open_findings = section(text, "Open Findings")
    if not open_findings:
        fail(f"{cert}: no '## Open Findings' section — say 'none' explicitly "
             f"or the lesson is not certified")
    elif not re.fullmatch(r"(none|0)\.?", open_findings.strip(), re.IGNORECASE):
        fail(f"{cert}: Open Findings is not 'none' — an open finding means "
             f"the fix loop is not done: {open_findings[:200]!r}")

    run = section(text, "Run")
    if not re.search(r"\S", run):
        fail(f"{cert}: no '## Run' section naming the Ringer run(s)")
    elif not re.search(r"20\d\d-\d\d-\d\d", run):
        fail(f"{cert}: Run section carries no YYYY-MM-DD date")

    if fails:
        print(f"FAIL — {len(fails)} problem(s):")
        for f in fails:
            print(f"  • {f}")
        return 1
    print("PASS — certification record complete: 4 check-print lanes PASS, "
          "screening majority yes, no open findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
