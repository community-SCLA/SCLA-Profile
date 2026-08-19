#!/usr/bin/env python3
"""check_motion.py — reject motion that fakes visual interest.

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
    the house motion language sanctions background depth-drift parallax and ring-breath by name.
  * ANYTHING ELSE — a finding. Text, chips, rows, nodes, numbers, CTAs, cards
    and the living-icon hero are content. The sanctioned-motion allow-list covers
    "the light templates' GHOST layers"; it has never covered a content hero.

FOUR RULES:

  keep-alive-motion   A repeating tween targets a non-decorative element.
  undeclared-target   A repeating tween's target cannot be resolved to a
                      literal selector (a variable, a computed array). Not a
                      violation of the ban — a violation of gradeability. A
                      checker that cannot see the target must not report clean;
                      that is the standing `nothing-graded` lesson.
  playback-progress-indicator
                      A thin progress/seek/playhead rail is positioned as
                      playback chrome. These full-runtime bars manufacture
                      pixel movement without developing the lesson's visual
                      idea, so they are forbidden even when renamed and even
                      when they carry no repeating motion.
  temporal-progress-motion
                      A line grows linearly from 0 to 100% for a whole scene or
                      composition. Position does not matter: a top-edge trace
                      is the same fake-motion device as a bottom progress bar.

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
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import Finding, typed

# A tween call on any named timeline: tl.fromTo(...), timeline.to(...), etc.
# This used to recognise only the literal identifier `tl`, so freeform builds
# using `const timeline = gsap.timeline(...)` graded zero tweens and passed.
# Captures the target expression and the option soup that follows it.
TWEEN = re.compile(
    r"\b[A-Za-z_$][\w$]*\s*\.\s*(?:fromTo|to|from)\s*\(\s*(?P<target>"
    r'"[^"]*"|\'[^\']*\'|\[[^\]]*\]|[A-Za-z_$][\w$.]*)'
    r"(?P<rest>.*?)(?=\b[A-Za-z_$][\w$]*\s*\.\s*"
    r"(?:fromTo|to|from)\s*\(|\Z)", re.S)

# Does this tween repeat? `repeat: 0` and `repeat: -1` are both meaningful:
# 0 is a one-shot (fine), -1 is infinite (never deterministic — the framework
# bans it outright, but grade it here too rather than assume).
REPEAT = re.compile(r"\brepeat\s*:\s*(-?\d+|[A-Za-z_$][\w$.]*\s*\([^)]*\)|"
                    r"[A-Za-z_$][\w$.]*)")
YOYO = re.compile(r"\byoyo\s*:\s*true\b")
ALLOW = re.compile(r"/\*\s*motion-allow\s*:\s*([^*]+?)\s*\*/", re.I)

# Owner hard stop, 2026-08-08: a thin playback-progress rail along the bottom
# of the frame may not be used to satisfy motion/presence gates.  This is
# intentionally structural as well as name-aware: the real failures arrived as
# `.progress`, `.progress-rail`, `.progress-fill`, and `data-role="progress"`.
# No `motion-allow` escape exists for this rule.  A lesson concept that needs a
# path must draw it as content, away from the bottom playback-chrome position.
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
HTML_TAG = re.compile(r"<[A-Za-z][^>]*>", re.S)
HTML_ATTR = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.S)
PROGRESS_NAME = re.compile(
    r"(?:^|[-_])(progress|playhead|scrub(?:ber)?|seek(?:bar)?|completion|"
    r"track|rail|meter)(?:$|[-_])",
    re.I,
)
CSS_LENGTH = re.compile(r"^(-?\d+(?:\.\d+)?)px$", re.I)
ROOT_DURATION = re.compile(
    r"<main\b[^>]*\bdata-duration\s*=\s*['\"](?P<duration>\d+(?:\.\d+)?)['\"]",
    re.I | re.S,
)

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


def _css_props(body: str) -> dict[str, str]:
    """Small declaration parser for the literal CSS used by compositions."""
    out = {}
    for declaration in body.split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        out[name.strip().lower()] = value.strip().lower()
    return out


def _px(value: str | None) -> float | None:
    match = CSS_LENGTH.fullmatch((value or "").strip())
    return float(match.group(1)) if match else None


def _semantic_progress_selectors(raw_html: str) -> set[str]:
    """Selectors whose element names or explicit role identify playback progress."""
    selectors = set()
    for tag in HTML_TAG.findall(raw_html):
        attrs = {m.group(1).lower(): m.group(3)
                 for m in HTML_ATTR.finditer(tag)}
        role_is_progress = (attrs.get("data-role", "").lower() == "progress")
        ident = attrs.get("id", "")
        if ident and (role_is_progress or PROGRESS_NAME.search(ident)):
            selectors.add(f"#{ident}")
        for cls in attrs.get("class", "").split():
            if role_is_progress or PROGRESS_NAME.search(cls):
                selectors.add(f".{cls}")
    return selectors


def _is_bottom_rail(props: dict[str, str]) -> bool:
    """True for a thin, wide, absolutely positioned bottom-edge element."""
    if props.get("position") not in {"absolute", "fixed"}:
        return False
    bottom = _px(props.get("bottom"))
    height = _px(props.get("height"))
    if bottom is None or not 0 <= bottom <= 180:
        return False
    if height is None or not 0 < height <= 12:
        return False
    spans_frame = (
        "left" in props and "right" in props
        or props.get("width") in {"100%", "100vw"}
        or (_px(props.get("width")) or 0) >= 400
        or (props.get("width") or "").startswith("calc(")
    )
    return spans_frame


def playback_progress_findings(raw_html: str):
    """Find bottom playback rails without mistaking content maps for chrome."""
    semantic = _semantic_progress_selectors(raw_html)
    findings = []
    seen = set()
    for block in STYLE_BLOCK.findall(raw_html):
        for selector_group, body in CSS_RULE.findall(block):
            props = _css_props(body)
            if not _is_bottom_rail(props):
                continue
            for selector in selector_group.split(","):
                selector = selector.strip()
                tokens = set(re.findall(r"[.#][\w-]+", selector))
                named = any(PROGRESS_NAME.search(token[1:]) for token in tokens)
                explicit = bool(tokens & semantic)
                if not (named or explicit):
                    continue
                if selector in seen:
                    continue
                seen.add(selector)
                findings.append({
                    "rule": "playback-progress-indicator",
                    "detail": (
                        f"{selector} is a thin playback-progress rail along "
                        "the bottom edge. Remove it; full-runtime progress "
                        "movement does not count as visual development. Give "
                        "the lesson beat-specific, meaning-driven motion instead"
                    ),
                })

    # Inline-styled variants have no stylesheet selector to inspect.  Grade
    # them by their own semantic id/class/data-role plus the same geometry.
    for tag in HTML_TAG.findall(raw_html):
        attrs = {m.group(1).lower(): m.group(3)
                 for m in HTML_ATTR.finditer(tag)}
        if "style" not in attrs or not _is_bottom_rail(_css_props(attrs["style"])):
            continue
        names = [attrs.get("id", ""), *attrs.get("class", "").split()]
        if attrs.get("data-role", "").lower() != "progress" and not any(
                PROGRESS_NAME.search(name) for name in names if name):
            continue
        label = f"#{attrs['id']}" if attrs.get("id") else tag.split(">", 1)[0] + ">"
        if label in seen:
            continue
        seen.add(label)
        findings.append({
            "rule": "playback-progress-indicator",
            "detail": (
                f"{label} is an inline-styled playback-progress rail along "
                "the bottom edge. Remove it; add meaning-driven scene motion"
            ),
        })
    return findings


def temporal_progress_findings(raw_html: str):
    """Reject a renamed line that grows for a scene/composition's duration.

    Meaning-bearing connectors reveal at a cue and settle. A temporal progress
    line is mechanically different: linear easing, 0-to-100% growth, and a
    duration tied to the scene or nearly the whole composition. This catches
    the real `signal-trace`, `.track i`, and `.rail-fill` escapes without
    rejecting a quick arrow or path reveal.
    """
    root_match = ROOT_DURATION.search(raw_html)
    root_duration = (float(root_match.group("duration"))
                     if root_match else None)
    findings = []
    seen = set()
    # Production GSAP statements terminate with semicolons. Keeping a whole
    # statement preserves Math.max(... duration ...) expressions.
    for statement in _strip_comments(raw_html).split(";"):
        if not re.search(r"\.(?:fromTo|to)\s*\(", statement):
            continue
        if not re.search(r"\bease\s*:\s*['\"]none['\"]", statement, re.I):
            continue
        grows_scale = bool(
            re.search(r"\bscaleX\s*:\s*0(?:\.0+)?\b", statement)
            and re.search(r"\bscaleX\s*:\s*1(?:\.0+)?\b", statement))
        grows_width = bool(re.search(
            r"\bwidth\s*:\s*['\"]100%['\"]", statement, re.I))
        if not (grows_scale or grows_width):
            continue
        duration_expr = re.search(
            r"\bduration\s*:\s*(Math\.max\([^;]+|[A-Za-z_$][\w$]*|"
            r"\d+(?:\.\d+)?)", statement)
        if not duration_expr:
            continue
        expr = duration_expr.group(1)
        duration_bound = bool(re.search(r"\bduration\b", expr))
        if not duration_bound:
            try:
                seconds = float(expr)
            except ValueError:
                seconds = 0.0
            duration_bound = bool(root_duration and seconds >= root_duration * .8)
        if not duration_bound:
            continue
        target = re.search(r"\.(?:fromTo|to)\s*\(\s*([^,]+)", statement)
        label = target.group(1).strip() if target else "line"
        key = (label, expr)
        if key in seen:
            continue
        seen.add(key)
        findings.append({
            "rule": "temporal-progress-motion",
            "detail": (
                f"{label} grows linearly from 0 to 100% for the scene/video "
                "duration. That is a playback/completion indicator, not "
                "meaning-bearing motion. Remove it and make the narrated idea "
                "develop through cue-timed elements that establish and settle"
            ),
        })
    return findings


def repopulation_findings(raw_html: str):
    """Reject one generated carrier copied into every scene.

    This is the exact 2026-08-10 failure: twenty-one scenes contained useful,
    distinct diagrams in markup, then a loop hid them and appended the same
    five-node map to every `.visual`. Re-entering that clone satisfied motion
    while the lesson itself did not develop. A persistent carrier is welcome;
    rebuilding a fresh copy of it inside every scene is not.
    """
    collections = re.finditer(
        r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
        r"(?:gsap\.utils\.toArray|document\.querySelectorAll)\("
        r"[\"']\.scene[\"']\)", raw_html)
    for collection in collections:
        name = collection.group("name")
        starts = [m.start() for m in re.finditer(
            rf"\b{re.escape(name)}\.forEach\s*\(", raw_html)]
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else min(
                len(raw_html), start + 12000)
            block = raw_html[start:end]
            if not re.search(r"\.querySelector\(\s*[\"']\.visual[\"']\s*\)",
                             block):
                continue
            if "document.createElement" not in block:
                continue
            if not re.search(r"\b(?:visual|sceneVisual)\.append\s*\(", block):
                continue
            return [{
                "rule": "repopulated-carrier",
                "detail": (
                    f"{name}.forEach() creates and appends the same generated "
                    "carrier inside every scene visual. Re-entering a clone "
                    "does not count as scene development. Keep one carrier "
                    "persistent across related narration and transform, "
                    "highlight, or complete its meaning-bearing parts in place"
                ),
            }]
    return []


class _SceneVisuals(HTMLParser):
    """Collect the authored `.visual` subtree for each top-level clip."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.current = None
        self.scene_level = None
        self.visual_level = None
        self.scenes = []

    @staticmethod
    def _classes(attrs):
        return set(dict(attrs).get("class", "").split())

    @staticmethod
    def _token(tag, attrs, skeleton=False):
        kept = []
        for name, value in attrs:
            if name in {"id", "data-start", "data-duration", "data-beat-id"}:
                continue
            if skeleton and name == "data-state":
                continue
            if skeleton and name == "class":
                states = {"selected", "active", "current", "focused", "focus"}
                value = " ".join(x for x in (value or "").split()
                                 if x not in states)
            kept.append((name, value or ""))
        return ("<", tag, tuple(sorted(kept)))

    def handle_starttag(self, tag, attrs):
        classes = self._classes(attrs)
        if self.current is None and tag == "section" and "clip" in classes:
            values = dict(attrs)
            self.current = {
                "id": values.get("id") or values.get("data-beat-id") or "?",
                "duration": values.get("data-duration") or "?",
                "continuity": values.get("data-continuity") or "",
                "exact_tokens": [],
                "skeleton_tokens": [],
            }
            self.scene_level = len(self.stack)
        if (self.current is not None and self.visual_level is None
                and "visual" in classes):
            self.visual_level = len(self.stack)
        if self.current is not None and self.visual_level is not None:
            self.current["exact_tokens"].append(self._token(tag, attrs))
            self.current["skeleton_tokens"].append(
                self._token(tag, attrs, skeleton=True))
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if self.current is not None and self.visual_level is not None:
            self.current["exact_tokens"].append(self._token(tag, attrs))
            self.current["exact_tokens"].append(("/", tag))
            self.current["skeleton_tokens"].append(
                self._token(tag, attrs, skeleton=True))
            self.current["skeleton_tokens"].append(("/", tag))

    def handle_data(self, data):
        if self.current is None or self.visual_level is None:
            return
        value = re.sub(r"\s+", " ", data).strip()
        if value:
            self.current["exact_tokens"].append(("text", value))
            self.current["skeleton_tokens"].append(("text", value))

    def handle_endtag(self, tag):
        if self.current is not None and self.visual_level is not None:
            self.current["exact_tokens"].append(("/", tag))
            self.current["skeleton_tokens"].append(("/", tag))
        if self.stack:
            self.stack.pop()
        if (self.current is not None and self.visual_level is not None
                and len(self.stack) == self.visual_level):
            self.visual_level = None
        if (self.current is not None and self.scene_level is not None
                and len(self.stack) == self.scene_level):
            self.current["exact_signature"] = tuple(
                self.current.pop("exact_tokens"))
            self.current["skeleton_signature"] = tuple(
                self.current.pop("skeleton_tokens"))
            self.scenes.append(self.current)
            self.current = None
            self.scene_level = None
            self.visual_level = None


def repeated_scene_carrier_findings(raw_html: str):
    """Reject adjacent beat clips that clone the same authored illustration.

    A persistent carrier belongs in one shared scene while its meaning-bearing
    state develops. Copying the same subtree into several short clips makes
    entrances and scene count look like development even when the viewer sees
    the same picture again.
    """
    parser = _SceneVisuals()
    try:
        parser.feed(raw_html)
    except (TypeError, ValueError):
        return []
    scenes = [scene for scene in parser.scenes
              if scene.get("skeleton_signature")]
    continuity_wired = bool(re.search(
        r"(?:dataset\.continuity|getAttribute\(\s*['\"]data-continuity['\"])",
        raw_html))
    findings = []
    i = 0
    while i < len(scenes):
        j = i + 1
        while (j < len(scenes)
               and scenes[j]["skeleton_signature"]
               == scenes[i]["skeleton_signature"]):
            j += 1
        if j - i >= 2:
            group = scenes[i:j]
            exact = {scene["exact_signature"] for scene in group}
            continuity = {scene["continuity"] for scene in group}
            persistent_development = (
                len(exact) >= 2 and len(continuity) == 1
                and "" not in continuity and continuity_wired)
            if not persistent_development:
                ids = ", ".join(scene["id"] for scene in group)
                findings.append({
                    "rule": "repeated-scene-carrier",
                    "detail": (
                        f"adjacent beats {ids} reuse the same .visual carrier "
                        "without one declared continuity group and explicit "
                        "meaning-bearing states. Separate short clips, selected "
                        "classes, and repeated entrances do not create "
                        "development by themselves. Keep one carrier persistent "
                        "with data-continuity and change its authored state, or "
                        "use materially different illustrations"
                    ),
                })
        i = j
    return findings


def batch_emphasis_findings(raw_html: str):
    """Reject paint-only emphasis sprayed across an entire list at once."""
    findings = []
    html = _strip_comments(raw_html)
    for match in TWEEN.finditer(html):
        target = match.group("target").strip()
        selectors = _targets(target)
        if not selectors:
            continue
        selector = selectors[0]
        if not re.search(r"\.(?:card|chip|item|step|node)\b", selector):
            continue
        opts = match.group("rest").split(";")[0]
        if not re.search(r"\bstagger\s*:", opts):
            continue
        if not re.search(r"\b(?:borderColor|backgroundColor|color|boxShadow)\s*:",
                         opts):
            continue
        if re.search(r":nth-(?:child|of-type)\(", selector):
            continue
        findings.append({
            "rule": "batch-list-emphasis",
            "detail": (
                f"{selector} receives one paint-emphasis tween across the "
                "whole group. A fast stagger still reads as every box changing "
                "together. Cue each point from the narration and keep the "
                "currently spoken item visibly active before advancing"
            ),
        })
    return findings


def grade(raw_html: str):
    """Findings for one composition's script."""
    findings = (playback_progress_findings(raw_html)
                + temporal_progress_findings(raw_html)
                + repopulation_findings(raw_html)
                + repeated_scene_carrier_findings(raw_html)
                + batch_emphasis_findings(raw_html))
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
