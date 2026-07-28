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

# Slots that are structural/optional rather than on-screen copy: absence is fine.
EXEMPT = {
    "theme", "sceneIndex", "sceneDuration", "reveal", "winner", "winnerAfter",
    "ring", "icon",
}
CUE_RX = re.compile(r"(Cues?|Cue)$")


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


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ws = Path(argv[0]).resolve()
    as_json = "--json" in argv
    index = ws / "index.html"
    if not index.is_file():
        print(f"no index.html at {ws}", file=sys.stderr)
        return 2

    findings = []
    for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
        if 'class="clip"' not in line:
            continue
        sid = re.search(r'id="(scene-[\w-]+)"', line)
        src = re.search(r'data-composition-src="([^"]+)"', line)
        if not (sid and src):
            continue
        vv = re.search(r'data-variable-values="([^"]*)"', line) \
            or re.search(r"data-variable-values='([^']*)'", line)
        import html as _html
        try:
            authored = json.loads(_html.unescape(vv.group(1))) if vv else {}
        except Exception:
            authored = {}

        comp = ws / src.group(1)
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
        if missing:
            findings.append({
                "scene": sid.group(1),
                "template": comp.name,
                "unfilled": missing,
                "would_render": {s: schema[s] for s in missing},
            })

    if as_json:
        print(json.dumps({"findings": findings}, indent=2))
        return 1 if findings else 0

    print("[slots] unused template slots must be blanked with \"\"")
    if not findings:
        print("  ok — every declared slot is either authored or explicitly blanked")
        return 0
    for f in findings:
        print(f"  ! {f['scene']} ({f['template']}) leaves {len(f['unfilled'])} slot(s) unfilled:")
        for s in f["unfilled"]:
            print(f"      {s} -> would render placeholder: {f['would_render'][s]!r}")
    total = sum(len(f["unfilled"]) for f in findings)
    print(f"  FAIL: {total} unfilled slot(s) across {len(findings)} scene(s).")
    print('  Fix: add "<slot>": "" to that clip\'s data-variable-values for each unused slot.')
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
