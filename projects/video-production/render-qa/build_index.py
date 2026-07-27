#!/usr/bin/env python3
"""Generate a lesson build's `index.html` from a compact `scenes.json` manifest.

Why this exists (2026-07-27): authoring `index.html` by hand is what makes a
build slow. Every scene slot is one 400-700 char line of HTML attributes, and
Motion v2 pacing roughly doubles the scene count — so a re-author meant a
subagent emitting ~150k tokens, ~85% of the build's wall clock, with every
revision re-writing the whole file. The manifest is ~8 lines per scene, so the
authoring model writes content and cue phrases, not markup, and edits stay
surgical.

It also makes the 2026-07-27 template-collision defect unrepresentable: every
slot gets its OWN template file (`scla-points__scene-07-support.html`), since
HyperFrames keys a sub-composition's timeline and element ids to the file, not
the slot (see instance_templates.py).

    python3 build_index.py <workspace> --extract   # index.html -> scenes.json
    python3 build_index.py <workspace>             # scenes.json -> index.html

Manifest shape:

    {
      "theme": "summit",
      "program": "Mid-Career Momentum",
      "header": ["free-form provenance lines for the file comment"],
      "scenes": [
        {
          "id": "scene-02-more",
          "template": "scla-chips",
          "note": "why this scene exists / what it illustrates",
          "narration": "verbatim span of the refined script",
          "cues": {"iconCue": "ready for more",
                   "chipCues": ["more impact", "more recognition"]},
          "vars": {"label": "Why you're here", "heading": "…", "chips": "a,b,c"}
        }
      ]
    }

NO timing numbers appear here or in the generated file: `data-start`,
`data-duration`, `sceneDuration` and every cue value are placeholders that
`compile_timeline.py --apply` owns. Cue KEYS must exist for the compiler to
fill them, so this writes them from `cues` automatically.
"""
import html as html_mod
import json
import re
import sys
from pathlib import Path

from instance_templates import clone

HEAD = """<!DOCTYPE html>
<!--
{header}
  Generated from scenes.json by render-qa/build_index.py — edit the manifest,
  not this file. All timing numbers are compiler-owned (compile_timeline.py).
-->
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        margin: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0d2437;
      }}
      /* Host-root progress rail (frame.md -> "Host-root progress rail").
         Lives at host root, spans whole runtime, driven by the root "main" timeline.
         Not a scene clip — gates ignore it. Track = #cccedf tint; fill = gold. */
      #hf-rail-track {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 4px;
        background: rgba(204, 206, 223, 0.35);
        z-index: 9999;
        pointer-events: none;
      }}
      #hf-rail-fill {{
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 100%;
        background: #eaab2d;
        transform-origin: left center;
        transform: scaleX(0);
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
"""

TAIL = """
      <!-- Host-root progress rail — not a scene clip, so scene coverage ignores it.
           After all scene clips, before the audio tag. -->
      <div id="hf-rail-track">
        <div id="hf-rail-fill"></div>
      </div>

      <audio id="main-audio" src="assets/voice/narration.wav" preload="auto" data-start="0"></audio>
    </div>

    <script>
      (function () {
        // Host-root "main" timeline — drives the progress rail across the whole runtime.
        // Reads the compiler-owned #root data-duration at load time (never hand-typed).
        window.__timelines = window.__timelines || {};
        var root = document.getElementById("root");
        var total = parseFloat(root.getAttribute("data-duration") || "0");
        var tl = gsap.timeline({ paused: true });
        if (total > 0) {
          tl.fromTo(
            "#hf-rail-fill",
            { scaleX: 0 },
            { scaleX: 1, duration: total, ease: "none" },
            0
          );
        }
        window.__timelines["main"] = tl;
      })();
    </script>
  </body>
</html>
"""

PLACEHOLDER = "0"


def esc_attr(s):
    """Escape for a double-quoted HTML attribute."""
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def cue_placeholder(value):
    """Cue values are compiler-owned; only the key's shape matters here."""
    if isinstance(value, list):
        return ",".join([PLACEHOLDER] * len(value))
    return PLACEHOLDER


def build(ws: Path):
    manifest = json.loads((ws / "scenes.json").read_text())
    theme = manifest.get("theme", "summit")
    scenes = manifest["scenes"]
    comps = ws / "compositions"

    header_lines = manifest.get("header") or []
    header_lines = list(header_lines) + [
        f"{len(scenes)} scenes | theme {theme}"
        + (f" | program {manifest['program']}" if manifest.get("program") else ""),
    ]
    parts = [HEAD.format(header="\n".join("  " + h for h in header_lines), total="1")]

    used = {}
    for sc in scenes:
        sid, template = sc["id"], sc["template"]
        src = f"{template}.html"
        # One template FILE per slot — the collision fix, by construction.
        n = used.get(template, 0) + 1
        used[template] = n
        if n > 1:
            suffix = "__" + sid.replace("-", "_")
            text, _ = clone(comps / src, suffix)
            src = f"{template}{suffix}.html"
            (comps / src).write_text(text)

        cues = sc.get("cues") or {}
        variables = dict(sc.get("vars") or {})
        for key, value in cues.items():
            variables.setdefault(key, cue_placeholder(value))
        variables["theme"] = theme
        variables["sceneDuration"] = PLACEHOLDER

        attrs = [
            f'id="{sid}"',
            'class="clip"',
            f'data-composition-id="{sid}"',
            f'data-composition-src="compositions/{src}"',
            'data-start="0"',
            'data-duration="1"',
            'data-track-index="0"',
            f'data-narration="{esc_attr(sc["narration"])}"',
        ]
        if cues:
            attrs.append("data-cue-anchors=\"" + esc_attr(json.dumps(cues)) + '"')
        attrs.append("data-variable-values='" + json.dumps(variables) + "'")

        if sc.get("note"):
            parts.append(f"      <!-- {sc['note']} -->\n")
        parts.append("      <div " + " ".join(attrs) + "></div>\n\n")

    parts.append(TAIL)
    (ws / "index.html").write_text("".join(parts))
    print(f"[build_index] wrote index.html — {len(scenes)} scenes, theme {theme}, "
          f"{sum(1 for t, n in used.items() for _ in range(n - 1))} per-slot template clone(s)")


CLIP_RE = re.compile(r"<div (?P<attrs>[^>]*?class=\"clip\"[^>]*?)></div>")
ATTR_RE = re.compile(r"([\w-]+)=(\"[^\"]*\"|'[^']*')")


def extract(ws: Path):
    """Recover a manifest from a hand-authored index.html (migration path)."""
    text = (ws / "index.html").read_text()
    scenes, theme = [], "summit"
    for m in CLIP_RE.finditer(text):
        a = {k: v[1:-1] for k, v in ATTR_RE.findall(m.group("attrs"))}
        variables = json.loads(html_mod.unescape(a.get("data-variable-values", "{}")))
        cues = json.loads(html_mod.unescape(a["data-cue-anchors"])) if "data-cue-anchors" in a else {}
        theme = variables.pop("theme", theme)
        variables.pop("sceneDuration", None)
        for key in cues:
            variables.pop(key, None)
        template = re.sub(r"^compositions/|__.*$|\.html$", "", a["data-composition-src"])
        scenes.append({
            "id": a["id"],
            "template": template,
            "narration": html_mod.unescape(a.get("data-narration", "")),
            **({"cues": cues} if cues else {}),
            "vars": variables,
        })
    out = {"theme": theme, "scenes": scenes}
    (ws / "scenes.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"[build_index] extracted scenes.json — {len(scenes)} scenes, theme {theme}")


def main():
    argv = sys.argv[1:]
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    extract(ws) if "--extract" in argv else build(ws)


if __name__ == "__main__":
    main()
