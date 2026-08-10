#!/usr/bin/env python3
"""Differential proof that owner-rejected concept sameness fires forever."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from check_concepts import validate  # noqa: E402
from firing import fires  # noqa: E402

PASS = FAIL = 0


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label} {detail}")


root = Path(tempfile.mkdtemp(prefix="scla-concepts-"))
try:
    (root / ".scla-control-v3").touch()
    (root / "concepts").mkdir()
    fixtures = HERE / "fixtures" / "owner-rejections"
    registry = json.loads((fixtures / "registry.json").read_text())
    check("owner rejection registry is not empty", bool(registry["rejections"]))
    for row in registry["rejections"]:
        payload = json.loads((fixtures / row["fixture"]).read_text())
        (root / "concepts" / "CONCEPT-BOARD.json").write_text(json.dumps(payload))
        for option in payload["options"]:
            board = root / option["board"]
            board.write_text(f'<svg xmlns="http://www.w3.org/2000/svg"><text>{option["id"]}</text></svg>')
        findings = validate(root)
        matched = any(x.rule_id == row["rule_id"] for x in findings)
        fires(check, row["checker"], row["rule_id"], row["id"], matched,
              repr(findings))

    # Differential baseline: genuinely different carriers/layouts and events
    # remain legal. This prevents the fixture from becoming an always-red gate.
    clean = json.loads((fixtures / registry["rejections"][0]["fixture"]).read_text())
    carriers = ["flowing opportunity pipeline", "assembling studio toolkit",
                "weekly capacity landscape"]
    layouts = ["full-width route map", "central exploded workbench",
               "calendar landscape with guardrails"]
    verbs = ["route", "assemble", "rebalance"]
    for i, option in enumerate(clean["options"]):
        option["carrier"] = carriers[i]
        option["layout_family"] = layouts[i]
        for j, milestone in enumerate(option["milestones"]):
            milestone["visual_event"] = f"{verbs[i]} mechanism {j} through state {i}-{j}"
    (root / "concepts" / "CONCEPT-BOARD.json").write_text(json.dumps(clean))
    findings = validate(root)
    check("distinct visible concepts pass", not findings, repr(findings))
finally:
    shutil.rmtree(root)

print(f"{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
