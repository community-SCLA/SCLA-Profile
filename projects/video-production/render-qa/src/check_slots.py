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
            for slot in ICON_SLOTS & set(authored):
                for name in str(authored[slot]).split(","):
                    name = name.strip()
                    if name and name not in library:
                        unknown.append(f"{slot}={name!r}")
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
        for u in f.get("unknown_icons", []):
            print(f"  ! {f['scene']} ({f['template']}) names an icon the template "
                  f"does not have: {u} — it draws nothing, silently. "
                  f"Library: {', '.join(f['library'])}")
    total = sum(len(f["unfilled"]) + len(f.get("placeholder", {}))
                + len(f.get("unknown_icons", [])) for f in findings)
    print(f"  FAIL: {total} bad slot(s) across {len(findings)} scene(s).")
    print('  Fix: pass "" for unused slots; write authored copy (from the script) for placeholder slots.')
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
