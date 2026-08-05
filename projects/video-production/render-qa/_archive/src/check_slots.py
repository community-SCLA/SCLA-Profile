#!/usr/bin/env python3
"""check_slots.py — every template slot a scene doesn't use must be explicitly blanked.

Scene templates declare their variables in a JSON schema block at the top of
compositions/<name>.html, each with a `default`. A slot omitted from a clip's
data-variable-values renders that DEFAULT — placeholder copy the lesson script
never said. That is worse than a blank frame: it puts plausible, on-brand,
*fabricated* words on screen, and it passes every other gate (the text checks
grade size and restatement, not provenance).

The templates document the fix in their own labels ("Point 4 (empty to hide)"):
pass "" to hide a slot. This check enforces it.

Usage:  python3 check_slots.py <workspace> [--json]
Exit:   0 clean · 1 unfilled slots found · 2 bad args
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import parse_scenes, get_attr

# Values that are placeholder text, not authored copy — a builder copying an
# example or a schema default instead of writing from the script. Matched
# against every non-exempt string slot that will render.
PLACEHOLDER_RX = re.compile(
    r"^\s*(\[\[.*\]\]|\.{3}|…|TODO\b.*|TBD\b.*|<[^>]*>|xxx+)\s*$", re.I)

# Slots that are structural/optional rather than on-screen copy: absence is fine.
EXEMPT = {
    "theme", "sceneIndex", "sceneDuration", "reveal", "winner", "winnerAfter",
    "ring", "icon",
}
CUE_RX = re.compile(r"(Cues?|Cue)$")

# Slots that name an entry in the template's own living-icon library.
ICON_SLOTS = {"icon", "icons"}

# The plural `icons` slot is BANNED outright (owner, 2026-07-29: "add a rule
# that icons should not render to the right of bullet points" / "no future
# renders should include the icons within this style of illustration").
#
# It drew a ~64px glyph at the right edge of every bullet row (scla-points) and
# in the top-right corner of every card (scla-morph). Three ways it went wrong,
# all shipped: it rendered on SOME rows and not others, because the slot is
# positional and a short list left holes (`icons=",insight,"` put one icon
# beside point 2 of three); it drew two near-identical person glyphs in one
# frame (`mentorship` + `mentorship2`, which differ only in which figure is
# gold); and it competed with the row copy for the eye in a family whose whole
# job is a list of words.
#
# The capability is gone from both templates — this rule exists so a re-add,
# or a stale workspace still carrying the variable, fails loudly instead of
# being silently dropped by the compiler. The SINGULAR hero `icon` on
# statement/chips/steps/condition is unaffected; it is one illustration per
# frame, which is the thing the family is for.
BANNED_SLOTS = {"icons"}


def schema_of(comp: Path):
    """Return {slot_id: default} from the template's leading JSON schema block."""
    try:
        text = comp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    out = {}
    for m in re.finditer(
        r'\{"id"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"[^"]*"\s*,\s*"label"\s*:\s*"[^"]*"\s*,\s*"default"\s*:\s*("(?:[^"\\]|\\.)*"|[^,}]+)',
        text,
    ):
        slot, default = m.group(1), m.group(2)
        try:
            default = json.loads(default)
        except Exception:
            default = str(default).strip()
        out[slot] = default
    return out


def icon_library(comp: Path) -> set | None:
    """The top-level keys of the template's `const ICONS = { … }` map, or None
    if it has no library (most templates don't draw icons at all).

    Brace-matched rather than line-matched: the entries are one-liners today,
    and a gate that silently returns an empty set the day one wraps is a gate
    that stops firing without telling anyone.
    """
    try:
        text = comp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    i = text.find("const ICONS")
    if i < 0:
        return None
    j = text.find("{", i)
    if j < 0:
        return None
    depth = 0
    end = -1
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                end = k
                break
    if end < 0:
        return None
    keys, depth = set(), 0
    for m in re.finditer(r"[{}]|(\w+)\s*:", text[j + 1:end]):
        if m.group(0) == "{":
            depth += 1
        elif m.group(0) == "}":
            depth -= 1
        elif depth == 0 and m.group(1):
            keys.add(m.group(1))
    return keys or None


SCENE_INDEX_RX = re.compile(r"^\s*(\d+)")


def scene_index_problems(scenes) -> list:
    """The on-frame badge must be this scene's position, uniquely.

    `sceneIndex` prints "09 / REDESIGN" bottom-right, and it is how the owner
    refers to a frame when reviewing a cut ("on frame 22 do not use the loop").
    m4_visibility-actions numbered 13 scenes 1..11 — two 07s and two 09s, from a
    scene split into `scene-07a`/`scene-07b` that kept one badge — so a whole
    round of frame-numbered feedback could not be resolved against the plan
    without opening every scene. A badge that disagrees with the frame's real
    position is worse than no badge: it is confidently wrong, and it silently
    costs a reviewer's time rather than a builder's.

    Split beats are still fine — they just each take their own number.
    """
    problems = []
    for i, sc in enumerate(scenes, 1):
        raw = str((sc["variables"] or {}).get("sceneIndex", "")).strip()
        if not raw:
            continue
        m = SCENE_INDEX_RX.match(raw)
        if not m:
            problems.append({
                "scene": sc["id"], "template": "-",
                "rule_id": "scene-index-badge", "severity": "error",
                "unfilled": [], "would_render": {}, "placeholder": {},
                "badge": f"{raw!r} does not start with a scene number",
            })
            continue
        if int(m.group(1)) != i:
            problems.append({
                "scene": sc["id"], "template": "-",
                "rule_id": "scene-index-badge", "severity": "error",
                "unfilled": [], "would_render": {}, "placeholder": {},
                "badge": (f"badge says {int(m.group(1)):02d} but this is scene "
                          f"{i} of {len(scenes)} — renumber it {i:02d}"),
            })
    return problems


def check(ws: Path):
    """Grade a workspace. Returns (findings, error) — error is a string when the
    workspace could not be read at all, in which case findings is empty.

    Extracted from main() 2026-07-29 so tests can assert this checker FIRES
    (BUILD-enforcement-rebuild Phase 1) and so the mutation harness can call it
    in-process. main() is a thin printer over this.
    """
    ws = Path(ws).resolve()
    index = ws / "index.html"
    if not index.is_file():
        return [], f"no index.html at {ws}"

    findings = []
    html_text = index.read_text(encoding="utf-8", errors="replace")
    scenes = parse_scenes(html_text)   # multi-line-safe: regex over the whole
    if not scenes:                     # document, not a per-line scan
        return [], "no scene clips found in index.html — nothing to check"
    findings += scene_index_problems(scenes)
    for sc in scenes:
        src = get_attr(sc["tag"], "data-composition-src")
        if not src:
            continue
        authored = sc["variables"]

        comp = ws / src
        schema = schema_of(comp)
        if not schema:
            continue

        missing = [
            s for s, d in schema.items()
            if s not in authored
            and s not in EXEMPT
            and not CUE_RX.search(s)
            and isinstance(d, str) and d.strip()
        ]
        # Placeholder text passed explicitly is the same fabrication with
        # extra steps — [[slot]] defaults, "...", TODO markers must never render.
        placeholder = {
            s: v for s, v in authored.items()
            if s not in EXEMPT and not CUE_RX.search(s)
            and isinstance(v, str) and v.strip() and PLACEHOLDER_RX.match(v)
        }
        # An icon name the template's library doesn't have draws NOTHING, and
        # says nothing about it. scene-17 of the 2026-07-29 criteria build asked
        # scla-points for `map`; `map` existed in scla-statement and scla-steps
        # and not in scla-points, so row 2 of three shipped with a blank where
        # its icon belonged and every gate passed. `ICONS[name]` returning
        # undefined is a typo the browser cannot report — so it is graded here.
        library = icon_library(comp)
        unknown = []
        if library:
            # Banned slots are reported by their own rule; grading them here too
            # would print two findings for one defect and bury the actionable one.
            for slot in (ICON_SLOTS - BANNED_SLOTS) & set(authored):
                for name in str(authored[slot]).split(","):
                    name = name.strip()
                    if name and name not in library:
                        unknown.append(f"{slot}={name!r}")
        # A banned slot is graded on what the SCENE authored, not on what the
        # template declares — the template no longer declares `icons` at all, so
        # a scene still carrying one would otherwise be dropped in silence,
        # which is the failure mode this whole gate exists to prevent.
        banned = sorted(
            s for s in BANNED_SLOTS & set(authored) if str(authored[s]).strip()
        )
        if banned:
            findings.append({
                "scene": sc["id"],
                "template": comp.name,
                "rule_id": "banned-row-icons",
                "severity": "error",
                "unfilled": [],
                "would_render": {},
                "placeholder": {},
                "banned_slots": {s: authored[s] for s in banned},
            })
        if unknown:
            findings.append({
                "scene": sc["id"],
                "template": comp.name,
                "rule_id": "unknown-icon",
                "severity": "error",
                "unfilled": [],
                "would_render": {},
                "placeholder": {},
                "unknown_icons": unknown,
                "library": sorted(library),
            })
        if missing or placeholder:
            findings.append({
                "scene": sc["id"],
                "template": comp.name,
                # Stable keys for machine consumers (2026-07-29). Both classes
                # are the same defect — fabricated copy the script never said —
                # so they share a severity and differ only in how they got there.
                "rule_id": ("unfilled-slot" if missing else "placeholder-slot"),
                "severity": "error",
                "unfilled": missing,
                "would_render": {s: schema[s] for s in missing},
                "placeholder": placeholder,
            })
    return findings, None


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ws = Path(argv[0]).resolve()
    as_json = "--json" in argv

    findings, error = check(ws)
    if error:
        print(error, file=sys.stderr)
        # "no index.html" is a usage error (2); an index with no clips is a
        # real failure (1) — same split main() has always drawn.
        return 2 if error.startswith("no index.html") else 1

    if as_json:
        print(json.dumps({"findings": findings}, indent=2))
        return 1 if findings else 0

    print("[slots] unused template slots must be blanked with \"\"")
    if not findings:
        print("  ok — every declared slot is either authored or explicitly blanked")
        return 0
    for f in findings:
        if f["unfilled"]:
            print(f"  ! {f['scene']} ({f['template']}) leaves {len(f['unfilled'])} slot(s) unfilled:")
            for s in f["unfilled"]:
                print(f"      {s} -> would render placeholder: {f['would_render'][s]!r}")
        for s, v in f.get("placeholder", {}).items():
            print(f"  ! {f['scene']} ({f['template']}) slot {s} carries placeholder text: {v!r}")
        for s, v in f.get("banned_slots", {}).items():
            print(f"  ! {f['scene']} ({f['template']}) authors the banned slot "
                  f"{s}={v!r} — per-row/per-card icons were removed from the "
                  f"templates on 2026-07-29 (owner: icons must not render to "
                  f"the right of bullet points). Drop the slot; if the frame "
                  f"needs an illustration, use the singular hero `icon`.")
        if f.get("badge"):
            print(f"  ! {f['scene']} sceneIndex: {f['badge']}")
        for u in f.get("unknown_icons", []):
            print(f"  ! {f['scene']} ({f['template']}) names an icon the template "
                  f"does not have: {u} — it draws nothing, silently. "
                  f"Library: {', '.join(f['library'])}")
    total = sum(len(f["unfilled"]) + len(f.get("placeholder", {}))
                + len(f.get("unknown_icons", []))
                + len(f.get("banned_slots", {}))
                + (1 if f.get("badge") else 0) for f in findings)
    print(f"  FAIL: {total} bad slot(s) across {len(findings)} scene(s).")
    print('  Fix: pass "" for unused slots; write authored copy (from the script) for placeholder slots.')
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
