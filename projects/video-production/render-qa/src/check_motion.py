#!/usr/bin/env python3
"""check_motion.py — settled content may not re-animate in place.

THE DEFECT THIS OWNS. The owner banned in-place "keep-alive" motion on
2026-07-14 ("I fully want ripples off") and reaffirmed it 2026-07-15. Within a
day a session restored it — not by ignoring the rule, but because
`check_presence.py` fails a scene that holds pixel-static for 5s, and adding a
bob is a two-line fix while re-authoring the scene is not. Three MP4s shipped
with the banned motion and one was published. The ban was written in frame.md,
in the rules file, and in comments inside the very templates that violated it.
Prose lost to a gate three times over.

So the ban is no longer a rule about what an author should choose. The motion
is deleted from the templates, and this checker exists to keep it deleted:
re-adding it is a red gate, not a judgement call. That is the whole point —
the owner asked for the feature to be unselectable, not better policed.

WHAT IT GRADES. Every GSAP tween in a composition that carries `yoyo` or a
non-zero `repeat` — i.e. every tween that plays a motion more than once, which
is what "keep-alive" means mechanically. The target selector decides the
verdict:

  * DECORATION (ghost layers, ring furniture, canvas texture) — allowed.
    design-contract.md sanctions background depth-drift parallax and ring-breath by name.
  * ANYTHING ELSE — a finding. Text, chips, rows, nodes, numbers, CTAs, cards
    and the living-icon hero are content. design-contract.md's allow-list covers
    "the light templates' GHOST layers"; it has never covered a content hero.

TWO RULES:

  keep-alive-motion   A repeating tween targets a non-decorative element.
  undeclared-target   A repeating tween's target cannot be resolved to a
                      literal selector (a variable, a computed array). Not a
                      violation of the ban — a violation of gradeability. A
                      checker that cannot see the target must not report clean;
                      that is the `nothing-graded` lesson from check_geometry.

There is NO name-based allow-list. An exemption is DECLARED, on the tween or on
the helper call site, as a trailing `/* motion-allow: <reason> */` comment —
stated, never inferred. Until 2026-08-04 this gate also exempted any selector
whose id/class contained one of nine substrings ("ghost", "ring", "-bg", …).
That encoded SCLA template naming into the checker, so it did two bad things at
once: agent-authored HTML that follows no such convention got no exemption it
could earn, and any template element that happened to be NAMED decoratively got
one it never asked for. The living-icon bob survived review for two weeks partly
because `scla-condition` routed it through the same `drift()` helper as the
genuinely decorative `#cd-ghost` — a name read as an intention.

Hence the one asymmetry worth stating: for a helper-routed tween the
declaration must sit on the CALL SITE, never in the helper body. A helper body
serves every caller, so an allow there is a blanket exemption — precisely the
`drift()` failure above. `grade()` therefore ignores a helper body's own
declaration when resolving call sites, and each call answers for itself.

Usage:  python3 check_motion.py <workspace-or-design-system> [--json]
Exit:   0 clean · 1 violation · 2 bad args / nothing to grade
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, typed

# A tween call: tl.fromTo(<target>, ...) / tl.to(...) / tl.from(...).
# Captures the target expression and the option soup that follows it.
TWEEN = re.compile(
    r"\btl\s*\.\s*(?:fromTo|to|from)\s*\(\s*(?P<target>"
    r'"[^"]*"|\'[^\']*\'|\[[^\]]*\]|[A-Za-z_$][\w$.]*)'
    r"(?P<rest>.*?)(?=\btl\s*\.|\Z)", re.S)

# Does this tween repeat? `repeat: 0` and `repeat: -1` are both meaningful:
# 0 is a one-shot (fine), -1 is infinite (never deterministic — the framework
# bans it outright, but grade it here too rather than assume).
REPEAT = re.compile(r"\brepeat\s*:\s*(-?\d+|[A-Za-z_$][\w$.]*\s*\([^)]*\)|"
                    r"[A-Za-z_$][\w$.]*)")
YOYO = re.compile(r"\byoyo\s*:\s*true\b")
ALLOW = re.compile(r"/\*\s*motion-allow\s*:\s*([^*]+?)\s*\*/", re.I)

# Compound selectors ("#root .big", ".panel > .line") are ordinary in freeform
# HTML; a single-token pattern degraded them to undeclared-target — a failure,
# but the wrong rule with a misleading message.
SELECTOR = re.compile(r"""["']([#.][\w$\s.#>-]*[\w$-])["']""")

# A tween target is often a helper parameter: every template wraps its
# depth-drift in `var drift = function (sel, ax, ay, per) { tl.fromTo(sel, …) }`
# and then calls `drift("#t-ring-1", …)`. Following the parameter to its call
# sites is not a convenience — it is the point. `scla-condition` passed the
# living-icon hero through the same helper as the genuinely decorative
# `#cd-ghost`, and that is a large part of why a content tween read as
# background motion for two weeks. A gate that stops at the helper body sees
# one anonymous `sel` and grades neither.
HELPER = re.compile(
    r"\b(?:var|const|let)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*function\s*"
    r"\((?P<params>[^)]*)\)")


def _targets(expr: str) -> list[str]:
    """Literal selectors named by a tween's target expression."""
    return SELECTOR.findall(expr)


def _helper_args(html: str, ident: str):
    """If `ident` is a helper's first parameter, return (helper, [(selector,
    declared)]) for the selectors it is actually called with.

    `declared` is per CALL SITE — whether that individual call carries a
    trailing `/* motion-allow: … */` on its own line. A declaration inside the
    helper body is deliberately NOT consulted: the body serves every caller, so
    honouring it there would exempt content and decoration alike through one
    comment. That is the `drift()` blanket exemption this gate exists to stop.
    """
    for m in HELPER.finditer(html):
        params = [p.strip() for p in m.group("params").split(",") if p.strip()]
        if not params or params[0] != ident:
            continue
        name = m.group("name")
        # The first argument may be a string OR an array literal — scla-outro
        # drifts its ring pairs as `drift(["#o-ring-l1", "#o-ring-l2"], …)`, and
        # a string-only pattern reported that template `undeclared-target`
        # while it was in fact perfectly readable.
        out = []
        for c in re.finditer(
                rf"\b{re.escape(name)}\s*\(\s*(\[[^\]]*\]|\"[^\"]*\"|'[^']*')",
                html):
            eol = html.find("\n", c.end())
            tail = html[c.end():] if eol < 0 else html[c.end():eol]
            declared = bool(ALLOW.search(tail))
            out += [(s, declared) for s in SELECTOR.findall(c.group(1))]
        return name, out
    return None, []


def _strip_comments(js: str) -> str:
    """Blank out `//` line comments, keeping line structure.

    A checker that reads comments grades intent, not behaviour. This gate
    matched `drift("#cd-iconwrap", …)` inside the comment RECORDING ITS
    REMOVAL and reported the template still in violation — the same
    comment-blindness that let `check-enforcement.py`'s invokers() count a
    checker mentioned in a comment as invoked. `/* motion-allow: … */` is read
    before this runs, so declared exceptions survive.
    """
    out = []
    for line in js.splitlines():
        i = line.find("//")
        # not a URL scheme, and not inside a string is close enough here: the
        # templates never build "//" inside a tween's option object.
        if i >= 0 and not line[max(0, i - 1):i] == ":":
            line = line[:i]
        out.append(line)
    return "\n".join(out)


def grade(raw_html: str):
    """Findings for one composition's script."""
    findings = []
    # Only `//` comments are stripped, so a declared `/* motion-allow: … */`
    # exception survives into the graded text and is still honoured below.
    html = _strip_comments(raw_html)
    for m in TWEEN.finditer(html):
        rest = m.group("rest")
        # Only the option object of THIS tween — stop at its closing paren
        # depth. `rest` runs to the next tl. call, which is close enough
        # because options always precede it, but a stray later `yoyo` would
        # false-positive; cut at the first newline that starts a new statement.
        opts = rest.split(";")[0]
        rep = REPEAT.search(opts)
        repeats = bool(YOYO.search(opts)) or bool(
            rep and rep.group(1) not in ("0",))
        if not repeats:
            continue

        target = m.group("target").strip()
        # A declaration on THIS tween covers the selectors this tween names
        # literally. It is not consulted for helper routing (see _helper_args).
        declared = bool(ALLOW.search(m.group(0)))
        sels = [(s, declared) for s in _targets(target)]
        via = None
        if not sels and re.fullmatch(r"[A-Za-z_$][\w$]*", target):
            via, sels = _helper_args(html, target)
            if not sels and declared:
                # An opaque target the author has explicitly spoken for.
                continue
        elif not sels and declared:
            continue
        if not sels:
            findings.append({
                "rule": "undeclared-target",
                "detail": (f"a repeating tween targets {target!r}, which "
                           f"is not a literal selector — the gate cannot tell "
                           f"content from decoration, and must not report clean "
                           f"on what it could not read"),
            })
            continue
        for sel, sel_declared in sels:
            if sel_declared:
                continue
            where = (f"on the {via}() call site" if via
                     else "on the tween")
            findings.append({
                "rule": "keep-alive-motion",
                "detail": (f"{sel} is re-animated in place (repeating tween"
                           f"{f' via {via}()' if via else ''}) — "
                           f"settled content never wobbles, drifts, ripples or "
                           f"re-marks (owner 2026-07-14, reaffirmed 07-15). If "
                           f"the scene holds static, re-author it: cue a new "
                           f"beat or split the scene. If {sel} is genuinely "
                           f"background decoration, say so {where} with "
                           f"/* motion-allow: <reason> */"),
            })
    return findings


def compositions(target: Path) -> list[Path]:
    """Template sets grade their scla-*.html; a freeform workspace has no
    naming convention, so every composition is graded, plus index.html when it
    carries script (the freeform host owns timelines too). The scla-* glob is
    tried first so a design-system checkout never grades its demo scaffolding.
    (Was scla-*.html ONLY, which made this gate exit 2 — "nothing to grade" —
    on every freeform build; HANDOFF-agent-native-verdict §2.)"""
    for sub in ("compositions", "."):
        d = target / sub
        if d.is_dir():
            found = sorted(d.glob("scla-*.html"))
            if found:
                return found
    comps = target / "compositions"
    found = sorted(comps.glob("*.html")) if comps.is_dir() else []
    idx = target / "index.html"
    if idx.exists() and "<script" in idx.read_text(encoding="utf-8",
                                                   errors="replace"):
        found.append(idx)
    return found


def check(target: Path):
    comps = compositions(target)
    if not comps:
        return None, [f"no scla-*.html compositions under {target}"]
    report = {"templates": [], "graded": 0}
    problems = []
    for comp in comps:
        html = comp.read_text(encoding="utf-8", errors="replace")
        tweens = len(TWEEN.findall(html))
        findings = grade(html)
        report["graded"] += tweens
        report["templates"].append({"file": comp.name, "tweens": tweens,
                                    "findings": findings})
        for f in findings:
            problems.append(Finding(
                f["rule"], f"{comp.name} [{f['rule']}] {f['detail']}"))
    return report, problems


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    target = Path(args[0]).resolve()
    report, problems = check(target)
    if report is None:
        for p in problems:
            print(f"  !! {p}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps({"pass": not problems, "problems": problems,
                          "findings": typed(problems), "report": report},
                         indent=2))
    else:
        print(f"[motion] {report['graded']} tween(s) across "
              f"{len(report['templates'])} template(s)")
        for p in problems:
            print(f"  !! {p}")
        print("MOTION: " + ("PASS" if not problems
                            else f"FAIL ({len(problems)})"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
