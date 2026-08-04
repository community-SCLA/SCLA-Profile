#!/usr/bin/env python3
"""test_firing_coverage.py — the firing mandate.

Every `render-qa/check_*.py` must be covered by at least one test asserting a
POSITIVE finding. A checker that cannot be shown to fire is not a gate; it is a
file that runs.

On 2026-07-29 this repo had 10 checker modules and 4 firing fixtures.
`check_slots`, `check_boundaries`, `check_layout`, `check_presence` and
`check_geometry`'s size rules had none; `check_text` had only a token-import
assertion; `check_copy.titlecase()` was armed with zero fixture proving it ever
returned a finding — and frame.md actively contradicted it. All of that read as
covered, because "covered" meant "a test file mentions it".

HOW IT WORKS. This suite runs every sibling `test_*.py` as a subprocess with
`SCLA_FIRING_REGISTRY` pointing at a scratch file. `tests/firing.fires()` — the
wrapper each positive-finding assertion uses — appends its `(checker, rule)` key
when, and only when, the assertion PASSES. This suite then reads the union and
compares it to REQUIRED below.

The association is declared EXPLICITLY, at the assertion site, and never
inferred from imports. Inference is precisely how `scripts/check-enforcement.py`
`invokers()` acquired its false negatives: an import proves a module was loaded,
not that anything grades anything.

Consequences, both intended:
  - Delete a firing assertion  -> its key vanishes from the registry -> RED.
  - Break the checker it covers -> the assertion fails -> that suite goes RED
    and the key is never recorded -> RED here too.

Run:  python3 tests/test_firing_coverage.py   (exit 0 = all pass)
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RQ = HERE.parent

# ---------------------------------------------------------------------------
# The mandate. Every key here must be recorded by a passing firing assertion.
# Adding a rule to a checker without adding a row is allowed; deleting the
# fixture that backs a row is not.
REQUIRED = {
    "check_boundaries": ["mid-sentence-cut", "mid-word-cut", "insufficient-air",
                         "final-hold", "tail-after-last-scene"],
    "check_capacity":   ["maxlines"],
    "check_continuity": ["blip", "split-list", "split-sentence",
                         "freeform-opens-lowercase", "nothing-graded"],
    "check_copy":       ["conjunction", "dangling", "dangling-fragment",
                         "titlecase", "heading-period", "part-reference",
                         # the freeform (agent-native) path, re-armed via the
                         # beat-manifest adapter — HANDOFF-agent-native §1
                         "freeform-conjunction", "freeform-retired-name",
                         "freeform-titlecase", "freeform-heading-period",
                         "placeholder", "no-headings", "nothing-graded"],
    # the pre-render freeze gate (freeform lane) — the same rule check_presence
    # applies to the delivered MP4, run over snapshot stills before the render
    # is spent. twin-beats WARNS by design (STD-38) but must still be proven to
    # fire, or it rots into the vacuous PASS it exists to replace.
    "check_diversity":  ["static-span", "grid-too-sparse", "twin-beats",
                         "nothing-graded"],
    "check_geometry":   ["text-collision", "nothing-graded", "safe-area-breach",
                         "footer-breach", "padding-breach", "card-gutter"],
    # the pixel bounds gate (freeform lane) — same three bands, real pixels
    "check_ink":        ["safe-area", "padding", "footer"],
    # the brand gate (freeform lane) — colors + typeface from tokens.yml
    "check_brand":      ["off-color", "off-font", "missing-font-asset",
                         "nothing-graded"],
    # the content-FORM gate (freeform lane) — the two owner rules rehomed off
    # template slots onto element structure, BUILD-PLAN step 1.3a
    "check_forms":      ["one-item-list", "one-card", "nothing-graded"],
    "check_motion":     ["keep-alive-motion", "undeclared-target",
                         "freeform-keep-alive"],
    "check_slots":      ["unfilled", "placeholder", "unknown-icon",
                         "banned-row-icons", "scene-index-badge"],
    "check_text":       ["min-size", "restatement"],
    "check_variety":    ["consecutive-run", "min-forms", "artwork", "share",
                         "canvas-run", "canvas-seconds", "two-region",
                         "one-item-list", "one-card"],
}

# Checkers that cannot be fired from a pure-Python fixture: they need a live
# browser or a rendered MP4. They are TRACKED AS UNCOVERED here — named, counted
# and printed on every run — rather than silently skipped. Silent skipping is how
# run_tests.py lost five whole suites: they were runnable, and nothing ran them.
SLOW = {
    "check_layout":   "needs a live browser — shells out to the pinned "
                      "`npx hyperframes inspect` against a served workspace",
    "check_presence": "needs a rendered MP4 + ffmpeg — samples real pixels at 2fps",
}

failures = []
notes = []


# ---------------------------------------------------------------------------
# 1. Collect the registry by running every sibling suite with recording on.
registry = set()
registry_path = Path(tempfile.mkdtemp()) / "firing.tsv"
registry_path.write_text("")
env = dict(os.environ, SCLA_FIRING_REGISTRY=str(registry_path))

suites = [p for p in sorted(HERE.glob("test_*.py")) if p.name != Path(__file__).name]
for path in suites:
    r = subprocess.run([sys.executable, str(path)], env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        failures.append(f"{path.name} FAILED while collecting firing coverage — "
                        f"fix that suite first:\n{r.stdout[-800:]}")

for line in registry_path.read_text().splitlines():
    if "\t" in line:
        checker, rule = line.split("\t", 1)
        registry.add((checker.strip(), rule.strip()))


# ---------------------------------------------------------------------------
# 2. Every checker module must be accounted for — in REQUIRED or in SLOW.
modules = sorted(p.stem for p in (RQ / "src").glob("check_*.py"))
for mod in modules:
    if mod not in REQUIRED and mod not in SLOW:
        failures.append(
            f"{mod}.py exists but is covered by nothing and is not declared "
            f"slow. Write a fixture asserting it returns a finding, or add it "
            f"to SLOW with the reason it cannot be fired in-process.")
for mod in sorted(set(REQUIRED) | set(SLOW)):
    if mod not in modules:
        failures.append(f"{mod} is declared here but no {mod}.py exists — "
                        f"the coverage map has rotted")
for mod in sorted(set(REQUIRED) & set(SLOW)):
    failures.append(f"{mod} is in BOTH REQUIRED and SLOW — pick one")


# ---------------------------------------------------------------------------
# 3. Every required (checker, rule) must have fired.
for mod in sorted(REQUIRED):
    for rule in REQUIRED[mod]:
        if (mod, rule) not in registry:
            failures.append(
                f"NO FIRING PROOF for {mod}:{rule} — no passing "
                f"firing.fires(\"{mod}\", \"{rule}\", ...) assertion ran. "
                f"Either the fixture was deleted or the checker stopped firing.")


# ---------------------------------------------------------------------------
# 4. A slow checker that starts firing should be promoted, not left in SLOW.
for mod in sorted(SLOW):
    if any(c == mod for c, _ in registry):
        notes.append(f"{mod} is declared SLOW but recorded a firing proof — "
                     f"move it into REQUIRED")


# ---------------------------------------------------------------------------
# 5. The wrapper itself must be the only way a proof gets recorded. If a suite
#    calls firing.record() directly that is fine (test_variety.py does, inside
#    its own loop), but nothing may write the registry without going through
#    tests/firing.py.
for path in suites:
    src = path.read_text()
    if re.search(r"SCLA_FIRING_REGISTRY", src):
        failures.append(f"{path.name} touches SCLA_FIRING_REGISTRY directly — "
                        f"proofs must go through tests/firing.py")


# ---------------------------------------------------------------------------
covered = sum(len(v) for v in REQUIRED.values())
print(f"firing coverage: {len(REQUIRED)}/{len(modules)} checker module(s) "
      f"proven to fire, {covered} rule-level proof(s) required, "
      f"{len(registry)} recorded")
for mod, why in sorted(SLOW.items()):
    print(f"  UNCOVERED (tier: slow) {mod} — {why}")
for n in notes:
    print(f"  note: {n}")

if failures:
    print(f"\nFAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("test_firing_coverage: every armed checker is proven to fire")
