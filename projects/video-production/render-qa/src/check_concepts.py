#!/usr/bin/env python3
"""Gate concept diversity and selection evidence before composition authoring.

New control-v3 workspaces carry ``concepts/CONCEPT-BOARD.json``.  The artifact
keeps the pitch round inspectable: three visible boards, materially different
carriers/layout families, milestone-level visual events, and an independent
selector's scored decision.  A prose-only CONCEPT.md is not selection evidence.
"""

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    rule_id: str
    message: str


def _norm(value) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _words(value) -> set[str]:
    return {w for w in _norm(value).split() if len(w) > 2}


def _similarity(left, right) -> float:
    a, b = _words(left), _words(right)
    return len(a & b) / max(1, len(a | b))


def _finding(rule_id, message):
    return Finding(rule_id, message)


def validate(workspace: Path) -> list[Finding]:
    workspace = Path(workspace)
    if not (workspace / ".scla-control-v3").exists():
        return []
    path = workspace / "concepts" / "CONCEPT-BOARD.json"
    if not path.is_file():
        return [_finding("concept-evidence-missing",
                         "new builds require concepts/CONCEPT-BOARD.json")]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [_finding("concept-evidence-invalid", f"unreadable concept board: {exc}")]

    findings = []
    options = payload.get("options") or []
    if len(options) < 3:
        findings.append(_finding("concept-options-too-few",
                                 "show at least three concept options"))
        return findings

    ids = [_norm(x.get("id")) for x in options]
    if any(not x for x in ids) or len(set(ids)) != len(ids):
        findings.append(_finding("concept-option-id", "concept option IDs must be unique"))

    carriers = [_norm(x.get("carrier")) for x in options]
    layouts = [_norm(x.get("layout_family")) for x in options]
    if any(not x for x in carriers + layouts):
        findings.append(_finding("concept-description-missing",
                                 "every option needs a carrier and layout_family"))
    if len(set(carriers)) != len(carriers) or len(set(layouts)) != len(layouts):
        findings.append(_finding(
            "concept-options-not-distinct",
            "options repeat a carrier or layout family; variants of one template count as one idea"))

    board_hashes = []
    for option in options:
        oid = option.get("id", "?")
        board = option.get("board")
        board_path = workspace / str(board or "")
        try:
            board_path.relative_to(workspace)
        except ValueError:
            findings.append(_finding("concept-board-missing", f"{oid}: board escapes workspace"))
            continue
        if not board or not board_path.is_file() or board_path.suffix.lower() not in {
                ".png", ".jpg", ".jpeg", ".webp", ".svg"}:
            findings.append(_finding("concept-board-missing",
                                     f"{oid}: board must point to a visible image or SVG"))
        else:
            board_hashes.append(hashlib.sha256(board_path.read_bytes()).hexdigest())

        milestones = option.get("milestones") or []
        if len(milestones) < 5:
            findings.append(_finding("concept-milestones-too-few",
                                     f"{oid}: show at least five milestone frames"))
        events = [_norm(x.get("visual_event")) for x in milestones]
        if any(not x for x in events) or len(set(events)) != len(events):
            findings.append(_finding("concept-events-repeated",
                                     f"{oid}: milestone visual events must be named and distinct"))

    if len(board_hashes) != len(set(board_hashes)):
        findings.append(_finding("concept-boards-identical",
                                 "two concept boards are byte-identical"))

    # Catch renamed copies whose prose differs only cosmetically.
    for i, left in enumerate(options):
        left_story = " ".join(str(x.get("visual_event", ""))
                              for x in left.get("milestones") or [])
        for right in options[i + 1:]:
            right_story = " ".join(str(x.get("visual_event", ""))
                                   for x in right.get("milestones") or [])
            if _similarity(left_story, right_story) >= 0.72:
                findings.append(_finding(
                    "concept-options-not-distinct",
                    f"{left.get('id')} and {right.get('id')} describe substantially the same progression"))

    selection = payload.get("selection") or {}
    author = _norm(payload.get("authored_by"))
    selector = _norm(selection.get("selected_by"))
    if not author or not selector or author == selector:
        findings.append(_finding("concept-selector-not-independent",
                                 "authored_by and selection.selected_by must name different agents"))
    selected = _norm(selection.get("selected_id"))
    scores = selection.get("scores") or []
    scored = {_norm(row.get("id")): row for row in scores}
    if selected not in ids or set(scored) != set(ids):
        findings.append(_finding("concept-selection-incomplete",
                                 "selection must score every option and name one selected ID"))
    else:
        dimensions = ("clarity", "progression", "variation", "teaching_value")
        totals = {}
        for oid, row in scored.items():
            try:
                values = [int(row[name]) for name in dimensions]
            except (KeyError, TypeError, ValueError):
                findings.append(_finding("concept-selection-incomplete",
                                         f"{oid}: all four integer scores are required"))
                continue
            if any(v < 1 or v > 5 for v in values):
                findings.append(_finding("concept-selection-incomplete",
                                         f"{oid}: scores must be from 1 to 5"))
            totals[oid] = sum(values)
        if totals and totals.get(selected) != max(totals.values()):
            findings.append(_finding("concept-selection-contradicts-score",
                                     "selected concept is not a highest-scoring option"))
    rejected = selection.get("rejected") or []
    rejected_ids = {_norm(x.get("id")) for x in rejected if _norm(x.get("reason"))}
    if set(ids) - {selected} - rejected_ids:
        findings.append(_finding("concept-selection-incomplete",
                                 "every unselected option needs a specific rejection reason"))
    if len(_norm(selection.get("rationale"))) < 30:
        findings.append(_finding("concept-selection-incomplete",
                                 "selection needs an evidence-based rationale"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = validate(args.workspace)
    if args.json:
        print(json.dumps({"pass": not findings,
                          "findings": [x.__dict__ for x in findings]}, indent=2))
    elif findings:
        for item in findings:
            print(f"!! [{item.rule_id}] {item.message}")
    else:
        print("[concepts] PASS — visible, distinct options and independent selection")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
