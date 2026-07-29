#!/usr/bin/env python3
"""check-enforcement.py — STD-35: a written rule is a request, not a guarantee.

The Repo Structure Playbook v1.1, STD-35 (MUST):

    A written rule is a request; only a mechanism — a hook, a CI check, a lint,
    branch protection — is a guarantee. Any rule that must hold every single
    time is enforced by a mechanism, not a sentence.
    How to check: list every "always/never" sentence; for each, name the
    mechanism — or the gap.

You cannot make a document enforceable. You CAN make it incapable of lying
about being enforced, which is what this does. Two very different findings:

  BROKEN CLAIM  (hard fail, exit 1) — a doc names a mechanism that does not
      exist, or names a checker that nothing actually invokes. This is the
      dangerous case: a reader (human or agent) trusts the claim, skips the
      manual check, and nothing is watching. False safety is worse than none
      (STD-39's principle, applied to docs; STD-24 requires every claim be
      true).

  UNBACKED RULE (report only, exit 0) — a normative sentence ("never", "must",
      "always", "normative") with no mechanism named and no honest `Convention`
      label. This is the STD-35 gap inventory. It is deliberately NOT a hard
      failure: per STD-38 a drift check starts non-blocking so it teaches
      instead of nags, and per the playbook's own preamble, hardening a
      guideline into a hard rule is itself a defect.

Why this exists: on 2026-07-28 the owner asked "how do we make these things
enforceable?" after a build shipped with four rules ignored. Each traced to
prose — the variety rule lived only in decisions/log.md, the list-conjunction
rule said "prefer", and Title Case was *contradicted* by frame.md. Nothing
anywhere verified that a rule claiming to be normative had a mechanism behind
it. Now something does.

Usage:  python3 scripts/check-enforcement.py [--json] [--strict]
        --strict also exits 1 on UNBACKED rules (opt-in; see STD-38)
Exit:   0 clean (or report-only findings) · 1 broken claims · 2 bad args
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VP = REPO / "projects/video-production"

# Docs that carry normative claims and are therefore graded.
#
# The three skill/log files were added 2026-07-29. They were the largest
# graveyard: `render-lessons/SKILL.md` alone holds dozens of normative lines
# with no mechanism annotation and is read into EVERY build subagent's
# instructions — the single most-read normative doc in the repo was the one
# nothing audited. `decisions/log.md` is graded because a decision that names
# a mechanism is making the same promise a rule does.
GRADED = [
    ".claude/rules/repo-hygiene.md",
    ".claude/rules/video-production.md",
    ".claude/skills/render-lessons/SKILL.md",
    ".claude/skills/refine-scripts/SKILL.md",
    "CLAUDE.md",
    "decisions/log.md",
    "projects/video-production/CLAUDE.md",
    "projects/video-production/design-system/frame.md",
    "projects/video-production/design-system/AGENTS.md",
]

# Roots a backticked path in a doc may be relative to.
PATH_ROOTS = [REPO, VP, VP / "design-system", REPO / ".claude"]

# An annotation block: *(Mechanism: ...)*, *(Gate: ...)*, *(Convention...)*
# Body allows ONE level of nested parens — real annotations cite things like
# "the `.gitignore` credential shield (S14)", and a naive [^)]* truncates at
# that inner paren and then reports the annotation as naming no mechanism.
#
# Mechanism/Gate REQUIRE the colon; only Convention may stand bare. Without
# that, ordinary prose parenthesising the word "gate" was read as an annotation
# naming no mechanism and hard-failed — a heading arrow "→ (gate) → MP4" and a
# log line "(gates answered in session)" both did. A false BROKEN CLAIM is not
# a harmless over-report: it trains readers to wave the audit through, which is
# the exact false-safety failure this script exists to prevent.
ANNOTATION = re.compile(
    r"\((?:(?P<mech>Mechanisms?|Gates?)\s*:|(?P<conv>Convention)\b)"
    r"(?P<body>(?:[^()]|\([^()]*\))*)\)", re.I)

# A backticked path-ish token inside an annotation. `.jsonl` is in the list
# because published.tsv's sibling ledgers are cited as mechanisms and were
# silently unresolvable — an extension missing here reads as "names no
# mechanism", which is the false-negative direction.
PATHISH = re.compile(
    r"`([A-Za-z0-9_./-]+\.(?:py|sh|json|jsonl|tsv|md|mjs|yml|yaml))`")

# lint-refs.sh check N. The separator class must admit a backtick: every real
# citation in the repo is written ``lint-refs.sh` check 11`, and a bare `\s+`
# matched 1 of 6 — so five true citations went unverified while the check they
# named did not exist.
LINTCHECK = re.compile(r"lint-refs(?:\.sh)?[\s`]+check\s+(\d+)", re.I)

# Words that make a sentence a promise rather than advice.
NORMATIVE = re.compile(
    r"\b(never|always|must|may not|no exceptions|normative|"
    r"hard rule|hard fail|required|forbidden|banned)\b", re.I)

# Claims to be enforced that name no mechanism are only interesting in prose,
# not in code fences or tables of contents.
FENCE = re.compile(r"^\s*(```|~~~)")


def resolve(token: str) -> Path | None:
    for root in PATH_ROOTS:
        p = (root / token)
        if p.exists():
            return p
    # bare filename anywhere under render-qa/ or scripts/
    for d in (VP / "render-qa", REPO / "scripts"):
        p = d / Path(token).name
        if p.exists():
            return p
    return None


def invokers() -> dict[str, str]:
    """Map checker filename -> the file that actually invokes it.

    Two false-negative directions, both closed 2026-07-29:

      * the caller list was a fixed six and omitted `hyperframe-guard.sh` and
        `batch-precheck.sh` — two of the pipeline's real gate runners, so a
        checker invoked only from those read as "invoked by nothing".
      * a filename was matched ANYWHERE in a caller, comments included, so a
        checker merely *mentioned* in a comment counted as invoked. That is the
        dangerous direction: it manufactures the exact false safety this script
        exists to catch. Comment lines are stripped before matching.
    """
    found = {}
    for caller in [VP / "render-qa/preflight.py", VP / "render-qa/verify_render.py",
                   REPO / "scripts/batch-ship.sh", REPO / "scripts/lint-refs.sh",
                   REPO / "scripts/batch-prepare.sh", REPO / "scripts/batch-status.sh",
                   REPO / "scripts/hyperframe-guard.sh",
                   REPO / "scripts/batch-precheck.sh"]:
        if not caller.is_file():
            continue
        code = "\n".join(
            ln for ln in caller.read_text(encoding="utf-8",
                                          errors="replace").splitlines()
            if not ln.lstrip().startswith("#"))
        for name in re.findall(r"([a-z_][a-z0-9_-]*\.(?:py|sh))", code):
            found.setdefault(name, str(caller.relative_to(REPO)))
    return found


def lint_checks() -> set[str]:
    f = REPO / "scripts/lint-refs.sh"
    if not f.is_file():
        return set()
    return set(re.findall(r"\[(\d+)/\d+\]", f.read_text(encoding="utf-8")))


def grade():
    broken, unbacked, backed = [], [], []
    callers = invokers()
    checks = lint_checks()

    for rel in GRADED:
        f = REPO / rel
        if not f.is_file():
            broken.append({"file": rel, "line": 0,
                           "problem": "graded doc does not exist"})
            continue
        in_fence = False
        for n, line in enumerate(f.read_text(encoding="utf-8",
                                             errors="replace").splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            annots = list(ANNOTATION.finditer(line))
            if annots:
                for m in annots:
                    kind = ("convention" if m.group("conv")
                            else m.group("mech").lower())
                    body = m.group("body")
                    if kind.startswith("convention"):
                        # An honest label. Nothing to verify.
                        backed.append({"file": rel, "line": n,
                                       "kind": "convention"})
                        continue
                    named = False
                    for tok in PATHISH.findall(body):
                        named = True
                        target = resolve(tok)
                        if target is None:
                            broken.append({
                                "file": rel, "line": n,
                                "problem": f"names mechanism `{tok}` — no such "
                                           f"file exists"})
                            continue
                        # A checker nothing runs is not a mechanism.
                        base = target.name
                        if base.startswith("check_") and base not in callers:
                            broken.append({
                                "file": rel, "line": n,
                                "problem": f"names `{tok}`, which exists but is "
                                           f"invoked by nothing — not a gate"})
                        else:
                            backed.append({"file": rel, "line": n,
                                           "kind": "mechanism", "target": tok,
                                           "invoked_by": callers.get(base)})
                    for num in LINTCHECK.findall(body):
                        named = True
                        if num not in checks:
                            broken.append({
                                "file": rel, "line": n,
                                "problem": f"names lint-refs.sh check {num}, "
                                           f"which does not exist (have: "
                                           f"{','.join(sorted(checks, key=int))})"})
                        else:
                            backed.append({"file": rel, "line": n,
                                           "kind": "lint", "target": f"check {num}"})
                    if not named and not kind.startswith("convention"):
                        broken.append({
                            "file": rel, "line": n,
                            "problem": "claims a mechanism but names none — "
                                       "cite the file, or label it a Convention"})
                continue

            # No annotation on this line: is it making a promise anyway?
            #
            # ANY prose line counts, not just list items and table rows
            # (2026-07-29). The old `-`/`*`/`|` filter is why recall sat near
            # 17%: a normative sentence in a paragraph, a heading, or a YAML
            # frontmatter comment — where `frame.md` keeps some of its most
            # load-bearing claims — was invisible to the inventory. A rule does
            # not stop being a promise because of the character it starts with.
            stripped = line.strip()
            if stripped and stripped != "---" and NORMATIVE.search(stripped):
                unbacked.append({"file": rel, "line": n,
                                 "text": stripped.lstrip("#> ").strip()[:150]})
    return broken, unbacked, backed


def main() -> int:
    argv = sys.argv[1:]
    as_json = "--json" in argv
    strict = "--strict" in argv
    broken, unbacked, backed = grade()

    if as_json:
        print(json.dumps({"broken_claims": broken, "unbacked_rules": unbacked,
                          "backed": len(backed)}, indent=2))
    else:
        print(f"STD-35 enforcement audit — {len(backed)} backed claim(s), "
              f"{len(broken)} broken, {len(unbacked)} unbacked")
        if broken:
            print("\nBROKEN CLAIMS (hard fail — the doc promises a mechanism "
                  "that isn't there):")
            for b in broken:
                print(f"  !! {b['file']}:{b['line']}  {b['problem']}")
        if unbacked:
            print(f"\nUNBACKED RULES (report only — STD-35 gap inventory; "
                  f"{len(unbacked)} normative sentence(s) name no mechanism):")
            for u in unbacked[:40]:
                print(f"   ~ {u['file']}:{u['line']}  {u['text']}")
            if len(unbacked) > 40:
                print(f"   … and {len(unbacked) - 40} more (use --json for all)")
        if not broken and not unbacked:
            print("\nclean: every normative claim names a live mechanism.")
    return 1 if (broken or (strict and unbacked)) else 0


if __name__ == "__main__":
    sys.exit(main())
