#!/usr/bin/env python3
"""firing.py — the firing registry shared by the gate test suites.

A checker that cannot be *shown* to fire is not a gate. Before 2026-07-29 the
repo had 10 `check_*.py` modules and 4 firing fixtures; `check_copy.titlecase()`
was armed with zero fixture proving it ever returned a finding, and `check_text`
had only a token-import assertion. All of that read as covered.

`fires()` wraps a POSITIVE-finding assertion — "this checker RETURNED a finding
on this crafted input", never "this checker passed on a good one" — and records
the proof under an explicit `(checker, rule)` key declared **at the assertion
site**. Nothing is inferred from imports: inference is exactly how
`scripts/check-enforcement.py`'s `invokers()` acquired its false negatives.

`tests/test_firing_coverage.py` runs every sibling suite with
`SCLA_FIRING_REGISTRY` set, reads the union, and fails if any `(checker, rule)`
it requires is missing — so deleting a firing assertion turns the suite red
rather than quietly lowering a pass count.
"""
import os

REGISTRY = os.environ.get("SCLA_FIRING_REGISTRY")


def record(checker: str, rule: str) -> None:
    if REGISTRY:
        with open(REGISTRY, "a", encoding="utf-8") as fh:
            fh.write(f"{checker}\t{rule}\n")


def fires(check, checker: str, rule: str, label: str, cond, detail: str = ""):
    """Assert a checker returned a finding, and register the proof.

    `check` is the calling suite's own pass/fail counter, so a suite keeps its
    own reporting. Registration happens only when the assertion PASSES — a
    broken checker must not look covered.
    """
    check(f"[fires {checker}:{rule}] {label}", cond, detail)
    if cond:
        record(checker, rule)
    return cond
