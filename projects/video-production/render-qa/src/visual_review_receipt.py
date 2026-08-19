#!/usr/bin/env python3
"""Validate the evidence behind one SCLA adversarial visual review.

A PASS/ALIVE/PROCEED label is not a review.  This module is the shared reader
for both the write-side control plane and the disk-derived pipeline status, so
an incomplete receipt cannot be accepted by one path after another path
refuses to create it.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from hfp_common import sample_units

FRAME_TIME = re.compile(r"(?:^|-)at-(\d+(?:\.\d+)?)s(?:\.|$)", re.I)
MIN_EVIDENCE_FRAMES = 3
MIN_LAYOUT_FAMILIES = 3
MIN_CHANGE_NOTES = 5


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _concept_author(workspace: Path) -> str:
    for path in (workspace / "concepts" / "CONCEPT-BOARD.json",
                 workspace / "concept.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        author = str(value.get("authored_by") or "").strip().lower()
        if author:
            return author
    return ""


def _frame_rows(workspace: Path, values, label: str):
    """Return (valid rows, errors), proving paths and bytes are still current."""
    rows, errors = [], []
    snapshots = (workspace / "snapshots").resolve()
    for value in values if isinstance(values, list) else []:
        if not isinstance(value, dict):
            errors.append(f"{label} must carry a path and sha256")
            continue
        raw = value.get("path")
        expected = value.get("sha256")
        if not isinstance(raw, str) or not raw:
            errors.append(f"{label} has no path")
            continue
        path = (workspace / raw).resolve()
        try:
            path.relative_to(snapshots)
        except ValueError:
            errors.append(f"{label} is outside snapshots/: {raw}")
            continue
        if not path.is_file():
            errors.append(f"missing {label}: {raw}")
            continue
        actual = _sha256(path)
        if not isinstance(expected, str) or expected != actual:
            errors.append(f"{label} bytes changed after review: {raw}")
            continue
        rows.append({"path": raw, "sha256": actual})
    return rows, errors


def validate_visual_review(workspace: Path, receipt: dict) -> list[str]:
    """Return human-readable contract failures; an empty list is valid."""
    workspace = Path(workspace)
    if not isinstance(receipt, dict):
        return ["visual-review receipt is not a JSON object"]

    errors = []
    reviewer = str(receipt.get("reviewer") or "").strip()
    author = _concept_author(workspace)
    if not author:
        errors.append("concept author is missing; reviewer independence cannot be verified")
    if not reviewer:
        errors.append("reviewer is missing")
    elif author and reviewer.lower() == author:
        errors.append("reviewer is the concept author; adversarial review must be independent")

    evidence, evidence_errors = _frame_rows(
        workspace, receipt.get("evidence_frames"), "evidence frame")
    weakest, weakest_errors = _frame_rows(
        workspace, receipt.get("weakest_frames"), "weakest frame")
    errors.extend(evidence_errors)
    errors.extend(weakest_errors)

    unique_evidence = {row["path"] for row in evidence}
    if len(unique_evidence) < MIN_EVIDENCE_FRAMES:
        errors.append(
            f"need at least {MIN_EVIDENCE_FRAMES} distinct evidence frames; "
            f"found {len(unique_evidence)}")
    if not weakest:
        errors.append("need at least one weakest frame")

    # The contract says to inspect the most crowded settled frame in every
    # scene.  The canonical snapshot grid is one frame per sample unit, so bind
    # the receipt to every unit rather than accepting three cherry-picked
    # frames from a two-minute lesson.
    try:
        units = sample_units(workspace)
    except (OSError, ValueError, json.JSONDecodeError):
        units = []
    evidence_times = []
    for row in evidence:
        match = FRAME_TIME.search(Path(row["path"]).name)
        if match:
            evidence_times.append(float(match.group(1)))
    uncovered = []
    for unit in units:
        lo = float(unit["start"])
        hi = lo + float(unit["duration"])
        if not any(lo <= when <= hi for when in evidence_times):
            uncovered.append(str(unit.get("id") or "?"))
    if uncovered:
        sample = ", ".join(uncovered[:5])
        suffix = "..." if len(uncovered) > 5 else ""
        errors.append(
            f"evidence does not cover {len(uncovered)}/{len(units)} sampled "
            f"beat(s): {sample}{suffix}")

    changes = receipt.get("material_changes")
    if not isinstance(changes, list) or len(
            [x for x in changes if isinstance(x, str) and x.strip()]
            ) < MIN_CHANGE_NOTES:
        errors.append(f"need at least {MIN_CHANGE_NOTES} material-change notes")

    families = receipt.get("layout_families")
    if not isinstance(families, int) or families < MIN_LAYOUT_FAMILIES:
        errors.append(f"need at least {MIN_LAYOUT_FAMILIES} materially different layout families")
    return errors
