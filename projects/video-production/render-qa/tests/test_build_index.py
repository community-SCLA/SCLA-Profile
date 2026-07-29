#!/usr/bin/env python3
"""Pinning tests for build_index.py — the scenes.json -> index.html compiler.

Five pins, each guarding a real property the module doc claims:

  1. DETERMINISM  — same scenes.json, built twice (two fresh workspaces),
     produces byte-identical index.html. Pins the FNV-1a data-hf-id minting:
     no randomness, no timestamps, no dict-order leakage.
  2. ROUND-TRIP    — build -> --extract recovers a manifest semantically
     equal to the input (modulo documented drops: per-scene "note" is
     provenance-only and never round-trips; top-level "program"/"header"
     are free-form and not re-derivable from compiled markup).
  3. CANON HEAD/TAIL — the compiled index.html carries the approved
     boilerplate verbatim, AND the same strings are cross-pinned against
     scripts/batch-prepare.sh's scaffold heredoc (the other place this canon
     is generated from). A drift in either copy fails loudly and names which
     side broke.
  4. PLACEHOLDERS  — every compiled scene div carries the compiler-owned
     timing placeholders (data-start="0" data-duration="1") and a minted
     data-hf-id — never a real number, never missing.
  5. CLONES        — a template used by a second scene slot gets its own
     `__i2` file on disk (the 2026-07-27 template-collision fix), and that
     slot's data-composition-src points at the clone, not the shared file.

Does NOT touch renders-hyperframes/ (gitignored, absent in CI) — the fixture
copies real, tracked templates from design-system/compositions/.

Run:  python3 tests/test_build_index.py   (exit 0 = all pass)
"""
import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
RENDER_QA = TESTS_DIR.parent
sys.path.insert(0, str(RENDER_QA / "src"))
import build_index as bi  # noqa: E402

REPO_ROOT = RENDER_QA.parents[2]
DS_COMPOSITIONS = RENDER_QA.parents[0] / "design-system" / "compositions"
BATCH_PREPARE = REPO_ROOT / "scripts" / "batch-prepare.sh"
TEMPLATES = ["scla-title", "scla-statement", "scla-chips"]

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


# ------------------------------------------------------------------ fixture
# A minimal, valid 4-scene manifest: one title, TWO statement scenes (forces
# the __i2 clone), one chips scene. Deliberately exercises both cue shapes
# (a scalar iconCue, a list chipCues) and an attr-escaping character (&) in
# narration, to pin esc_attr <-> html.unescape round-tripping too.
MANIFEST = {
    "theme": "summit",
    "program": "Early Career Boost",
    "header": ["fixture manifest for test_build_index.py — not a real lesson"],
    "scenes": [
        {
            "id": "scene-01-title",
            "template": "scla-title",
            "note": "Opens on program identity.",
            "narration": "Welcome to Building Better Habits.",
            "vars": {"eyebrow": "Early Career Boost", "title": "Building Better Habits",
                      "meta": "", "sceneIndex": "01 / TITLE"},
        },
        {
            "id": "scene-02-statement",
            "template": "scla-statement",
            "narration": "Growth requires clarity & follow-through.",
            "cues": {"iconCue": "requires clarity"},
            "vars": {"kicker": "The idea", "statement": "Growth requires clarity and follow-through.",
                      "lines": "", "icon": "compass"},
        },
        {
            "id": "scene-03-statement",
            "template": "scla-statement",
            "narration": "Small habits compound over time.",
            "vars": {"kicker": "The idea", "statement": "Small habits compound over time.",
                      "lines": ""},
        },
        {
            "id": "scene-04-chips",
            "template": "scla-chips",
            "narration": "Focus on consistency, feedback, and reflection.",
            "cues": {"chipCues": ["consistency", "feedback", "reflection"]},
            "vars": {"label": "Focus areas", "heading": "Three habits that compound",
                      "chips": "Consistency,Feedback,Reflection"},
        },
    ],
}


def make_fixture(tmp: Path, manifest: dict) -> Path:
    comps = tmp / "compositions"
    comps.mkdir(parents=True)
    for name in TEMPLATES:
        shutil.copy(DS_COMPOSITIONS / f"{name}.html", comps / f"{name}.html")
    (tmp / "scenes.json").write_text(json.dumps(manifest, ensure_ascii=False))
    return tmp


def quiet_build(ws):
    with contextlib.redirect_stdout(io.StringIO()):
        bi.build(ws)


def quiet_extract(ws):
    with contextlib.redirect_stdout(io.StringIO()):
        bi.extract(ws)


def scene_divs(text):
    """[{attr: value, ...}, ...] for every class="clip" div, via the module's
    OWN regexes — the test reads compiled output the same way extract() does."""
    out = []
    for m in bi.CLIP_RE.finditer(text):
        out.append({k: v[1:-1] for k, v in bi.ATTR_RE.findall(m.group("attrs"))})
    return out


workdirs = [Path(tempfile.mkdtemp(prefix="build_index_test_")) for _ in range(2)]
try:
    ws1, ws2 = (make_fixture(d, MANIFEST) for d in workdirs)

    # --------------------------------------------------------- 1. DETERMINISM
    print("== determinism: same scenes.json, two fresh workspaces ==")
    quiet_build(ws1)
    quiet_build(ws2)
    html1 = (ws1 / "index.html").read_text()
    html2 = (ws2 / "index.html").read_text()
    check("compiled index.html is byte-identical across builds", html1 == html2,
          f"{len(html1)} vs {len(html2)} bytes" if html1 != html2 else "")
    clone1 = (ws1 / "compositions" / "scla-statement__i2.html").read_text()
    clone2 = (ws2 / "compositions" / "scla-statement__i2.html").read_text()
    check("cloned template file is byte-identical across builds", clone1 == clone2)
    # Re-build ws1 in place (idempotency, not just cross-workspace equality).
    quiet_build(ws1)
    check("re-building the SAME workspace reproduces the same bytes",
          (ws1 / "index.html").read_text() == html1)

    # ----------------------------------------------------------- 5. CLONES
    print("== clones: second slot on a shared template ==")
    divs1 = scene_divs(html1)
    check("compiled output has exactly 4 scene divs", len(divs1) == 4, str(len(divs1)))
    clone_path = ws1 / "compositions" / "scla-statement__i2.html"
    check("scla-statement__i2.html clone file exists on disk", clone_path.exists())
    d3 = next((d for d in divs1 if d.get("id") == "scene-03-statement"), None)
    check("scene-03-statement found in compiled output", d3 is not None)
    if d3 is not None:
        check("second scla-statement slot's data-composition-src points at the clone",
              d3.get("data-composition-src") == "compositions/scla-statement__i2.html",
              d3.get("data-composition-src"))
    d2 = next((d for d in divs1 if d.get("id") == "scene-02-statement"), None)
    check("first scla-statement slot keeps the shared (uncloned) file",
          d2 is not None and d2.get("data-composition-src") == "compositions/scla-statement.html",
          d2.get("data-composition-src") if d2 else "scene not found")
    other_slots_clean = all(
        d.get("data-composition-src") in ("compositions/scla-title.html", "compositions/scla-chips.html")
        for d in divs1 if d.get("id") in ("scene-01-title", "scene-04-chips"))
    check("single-use templates (title, chips) are never cloned", other_slots_clean)

    # ------------------------------------------------------- 4. PLACEHOLDERS
    print("== placeholders: timing is compiler-owned, never typed here ==")
    all_placeholder = all(d.get("data-start") == "0" and d.get("data-duration") == "1" for d in divs1)
    check("every scene div has data-start=\"0\" data-duration=\"1\"", all_placeholder,
          str([(d.get("id"), d.get("data-start"), d.get("data-duration")) for d in divs1]))
    all_hf_id = all(d.get("data-hf-id", "").startswith("hf-") for d in divs1)
    check("every scene div has a minted data-hf-id", all_hf_id,
          str([(d.get("id"), d.get("data-hf-id")) for d in divs1]))
    ids = [d.get("data-hf-id") for d in divs1]
    check("data-hf-id values are unique across scenes", len(ids) == len(set(ids)), str(ids))
    root_m = re.search(r'<div data-hf-id="(hf-[^"]+)" id="root"[^>]*data-duration="1"[^>]*>', html1)
    check("root div also carries a minted data-hf-id and data-duration placeholder",
          root_m is not None, "root <div> tag: " + repr(re.search(r'<div data-hf-id[^>]*id="root"[^>]*>', html1)))

    # --------------------------------------------------------- 2. ROUND-TRIP
    print("== round-trip: build -> --extract recovers the manifest ==")
    quiet_extract(ws1)
    extracted = json.loads((ws1 / "scenes.json").read_text())
    check("extracted theme matches input theme", extracted.get("theme") == MANIFEST["theme"],
          extracted.get("theme"))
    check("extracted scene count matches input", len(extracted.get("scenes", [])) == len(MANIFEST["scenes"]),
          len(extracted.get("scenes", [])))

    def normalize(sc):
        d = {"id": sc["id"], "template": sc["template"],
             "narration": sc.get("narration", ""), "vars": sc.get("vars") or {}}
        if sc.get("cues"):
            d["cues"] = sc["cues"]
        return d

    want = [normalize(sc) for sc in MANIFEST["scenes"]]
    got = [normalize(sc) for sc in extracted.get("scenes", [])]
    for i, (w, g) in enumerate(zip(want, got)):
        check(f"scene {i+1} ({w['id']}) round-trips semantically equal", w == g,
              f"want {w} got {g}")
    check("extracted scenes drop the input-only \"note\" field (documented default)",
          all("note" not in sc for sc in extracted.get("scenes", [])))

    # ------------------------------------------------- 3. CANON HEAD/TAIL PIN
    print("== canon: HEAD/TAIL boilerplate, cross-pinned against batch-prepare.sh ==")
    scaffold_text = BATCH_PREPARE.read_text()
    CANON_STRINGS = [
        ("html/body #000 background",
         'html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }'),
        ("rail track CSS (bottom:48px, #cccedf, opacity .28)",
         '#hf-rail-track { position: absolute; left: 0; bottom: 48px; width: 1920px; height: 4px; '
         'background: #cccedf; opacity: .28; }'),
        ("Inter body font rule",
         'body { font-family: "Inter", sans-serif; }'),
        ("JetBrains Mono code/pre rule",
         'code, pre, .monospace { font-family: "JetBrains Mono", monospace; }'),
        ("rail script reads dataset.duration",
         'document.getElementById("root").dataset.duration'),
    ]
    for label, needle in CANON_STRINGS:
        in_compiled = needle in html1
        in_scaffold = needle in scaffold_text
        if in_compiled and in_scaffold:
            check(f"canon pin: {label}", True)
        else:
            missing = []
            if not in_compiled:
                missing.append("build_index.py's compiled index.html")
            if not in_scaffold:
                missing.append("scripts/batch-prepare.sh")
            check(f"canon pin: {label}", False, f"missing from: {', '.join(missing)}")

    # The narration <audio id="narration-audio"> element: build_index.py
    # inserts data-hf-id BEFORE id (stamped, document order), so the literal
    # attribute order differs from the un-stamped scaffold — match on the
    # audio tag containing the id attribute, not on strict adjacency.
    audio_re = re.compile(r'<audio\b[^>]*\bid="narration-audio"[^>]*>')
    audio_in_compiled = audio_re.search(html1) is not None
    audio_in_scaffold = audio_re.search(scaffold_text) is not None
    if audio_in_compiled and audio_in_scaffold:
        check("canon pin: narration <audio id=\"narration-audio\"> element", True)
    else:
        missing = []
        if not audio_in_compiled:
            missing.append("build_index.py's compiled index.html")
        if not audio_in_scaffold:
            missing.append("scripts/batch-prepare.sh")
        check("canon pin: narration <audio id=\"narration-audio\"> element", False,
              f"missing from: {', '.join(missing)}")

finally:
    for d in workdirs:
        shutil.rmtree(d, ignore_errors=True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
