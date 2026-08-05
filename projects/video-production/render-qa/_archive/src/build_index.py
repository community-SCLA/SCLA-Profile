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
slot gets its OWN template file (`scla-points__i2.html`, same suffix scheme as
instance_templates.py), since HyperFrames keys a sub-composition's timeline and
element ids to the file, not the slot (see instance_templates.py).

HEAD/TAIL mirror the approved canon (pilot
better-decisions-come-from-better-criteria_early-career-boost_2026-07-28,
Motion v2 + follow-on fixes, 2026-07-28): black host background, Inter body /
JetBrains Mono code fonts, the 48px-bottom progress rail as two SIBLING
host-root divs, and the `narration-audio` tag. Compiled output is byte-identical
to the canon head/tail modulo the generated-file banner and `data-hf-id` values.

`data-hf-id`: the HyperFrames CLI (0.7.79, dist/cli.js `ensureHfIds`/
`stampFileHfIds`/`persistHfIdsIfNeeded`) stamps every body element missing one
and WRITES THE RE-SERIALIZED FILE BACK TO DISK — so if this compiler omitted
them, the first `lint`/`validate`/render would rewrite the generated index.html
(quote style, self-closing tags, injected ids — see preflight.py's
_style_script_digest note). We stamp them ourselves with an exact port of the
CLI's algorithm (FNV-1a over the element's content key, `hf-` + last 4 base36
chars), so ids are deterministic across rebuilds and the tool finds nothing to
add. Once present, the tool never re-mints an id, so timing rewrites by
compile_timeline.py don't churn them.

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

# HEAD/TAIL are the canon boilerplate (see module docstring). @TOKENS@ are
# substituted by build() — .replace, not .format, so the CSS braces stay flat.
HEAD = """<!DOCTYPE html>
<!--
@HEADER@
  Generated from scenes.json by render-qa/src/build_index.py — edit the manifest,
  not this file. All timing numbers are compiler-owned (compile_timeline.py).
-->
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1920, height=1080">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      body { font-family: "Inter", sans-serif; }
      code, pre, .monospace { font-family: "JetBrains Mono", monospace; }

      /* Host-root progress rail — spans the whole runtime, not scene motion.
         Not a scene clip, so the deterministic gates ignore it. */
      #hf-rail-track { position: absolute; left: 0; bottom: 48px; width: 1920px; height: 4px; background: #cccedf; opacity: .28; }
      #hf-rail-fill  { position: absolute; left: 0; bottom: 48px; width: 1920px; height: 4px; background: #eaab2d;
                       transform-origin: left center; transform: scaleX(0); }
    </style>
  </head>
  <body>
    <!-- data-duration is COMPILER-OWNED. Leave the placeholder; never type a real number. -->
    <div data-hf-id="@ROOT_HF@" id="root" data-composition-id="main" data-start="0" data-duration="@TOTAL@" data-width="1920" data-height="1080">

"""

TAIL = """      <div data-hf-id="@TRACK_HF@" id="hf-rail-track"></div>
      <div data-hf-id="@FILL_HF@" id="hf-rail-fill"></div>

      <!-- id + data-start are REQUIRED. Without them lint warns "audio will be
           SILENT in renders" — and the render really is silent. -->
      <audio data-hf-id="@AUDIO_HF@" id="narration-audio" src="assets/voice/narration.wav" data-audio-track="" data-start="0"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });

      // Rail span is read from the compiler-owned data-duration — never hand-typed.
      const total = parseFloat(document.getElementById("root").dataset.duration) || 0;
      tl.fromTo("#hf-rail-fill", { scaleX: 0 }, { scaleX: 1, duration: total, ease: "none" }, 0);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

PLACEHOLDER = "0"


def esc_attr(s):
    """Escape for a double-quoted HTML attribute. `>` is escaped too: a raw
    `>` inside an attribute value would truncate every [^>]-based tag regex
    in this pipeline (SCENE_TAG_RE, CLIP_RE, instance_templates.CLIP_RE)."""
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


# ── data-hf-id minting — exact port of hyperframes 0.7.79 dist/cli.js ──────
# (fnv1a / toHfId / contentKey / mintHfId). Port verified against the canon
# pilot: the rail divs' ids reproduce byte-for-byte (hf-sw2m / hf-1r7q).

def _fnv1a(s: str) -> int:
    """FNV-1a over UTF-16 code units (JS charCodeAt semantics)."""
    h = 2166136261
    for lo_hi in zip(*[iter(s.encode("utf-16-le"))] * 2):
        h ^= lo_hi[0] | (lo_hi[1] << 8)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _to_hf_id(h: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while h:
        s = digits[h % 36] + s
        h //= 36
    s = s or "0"
    return "hf-" + (s[-4:] if len(s) >= 4 else s.rjust(4, "0"))


def mint_hf_id(tag: str, attrs, assigned: set, text: str = "") -> str:
    """attrs = [(name, DECODED value)] excluding data-hf-* — the CLI reads DOM
    attribute values, so pass raw strings, not their HTML-escaped forms."""
    key = f"{tag}|" + "".join(sorted(f"{n}\0{v}" for n, v in attrs)) + f"|{text}"
    hf = _to_hf_id(_fnv1a(key))
    dup = 0
    while hf in assigned:
        dup += 1
        if dup > 10000:
            digits = "0123456789abcdefghijklmnopqrstuvwxyz"
            n, s = _fnv1a(key), ""
            while n:
                s = digits[n % 36] + s
                n //= 36
            hf = f"hf-{s or '0'}-{dup}"
            break
        hf = _to_hf_id(_fnv1a(f"{key}#{dup}"))
    assigned.add(hf)
    return hf


def cue_placeholder(value):
    """Cue values are compiler-owned; only the key's shape matters here."""
    if isinstance(value, list):
        return ",".join([PLACEHOLDER] * len(value))
    return PLACEHOLDER


def _compact(obj) -> str:
    """Attribute JSON: compact separators, real unicode — the canon form."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


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

    # hf-ids are minted in document order (the CLI's walkElements order):
    # root first, then each scene div, then rail track/fill, then the audio.
    assigned = set()
    root_attrs = [("id", "root"), ("data-composition-id", "main"),
                  ("data-start", "0"), ("data-duration", "1"),
                  ("data-width", "1920"), ("data-height", "1080")]
    root_hf = mint_hf_id("div", root_attrs, assigned)

    parts = [HEAD.replace("@HEADER@", "\n".join("  " + h for h in header_lines))
                 .replace("@ROOT_HF@", root_hf)
                 .replace("@TOTAL@", "1")]

    used = {}
    for sc in scenes:
        sid, template = sc["id"], sc["template"]
        src = f"{template}.html"
        # One template FILE per slot — the collision fix, by construction.
        # Suffix scheme matches instance_templates.py (__i2, __i3, …).
        n = used.get(template, 0) + 1
        used[template] = n
        if n > 1:
            suffix = f"__i{n}"
            text, _ = clone(comps / src, suffix)
            src = f"{template}{suffix}.html"
            (comps / src).write_text(text)

        cues = sc.get("cues") or {}
        variables = dict(sc.get("vars") or {})
        for key, value in cues.items():
            variables.setdefault(key, cue_placeholder(value))
        variables["theme"] = theme
        variables["sceneDuration"] = PLACEHOLDER

        # (name, DECODED value) in canon attribute order; data-hf-id is minted
        # from these and then serialized first, exactly as the CLI would.
        attrs = [
            ("class", "clip"),
            ("id", sid),
            ("data-composition-id", sid),
            ("data-composition-src", f"compositions/{src}"),
            ("data-start", "0"),
            ("data-duration", "1"),
            ("data-track-index", "1"),
            ("data-narration", sc["narration"]),
            ("data-variable-values", _compact(variables)),
        ]
        if cues:
            attrs.append(("data-cue-anchors", _compact(cues)))
        hf = mint_hf_id("div", attrs, assigned)

        if sc.get("note"):
            parts.append(f"      <!-- {sc['note']} -->\n")
        serialized = " ".join(f'{k}="{esc_attr(v)}"' for k, v in attrs)
        parts.append(f'      <div data-hf-id="{hf}" {serialized}></div>\n\n')

    track_hf = mint_hf_id("div", [("id", "hf-rail-track")], assigned)
    fill_hf = mint_hf_id("div", [("id", "hf-rail-fill")], assigned)
    audio_hf = mint_hf_id("audio", [("id", "narration-audio"),
                                    ("src", "assets/voice/narration.wav"),
                                    ("data-audio-track", ""),
                                    ("data-start", "0")], assigned)
    parts.append(TAIL.replace("@TRACK_HF@", track_hf)
                     .replace("@FILL_HF@", fill_hf)
                     .replace("@AUDIO_HF@", audio_hf))
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
