#!/usr/bin/env python3
"""test_brand.py — firing proofs for check_brand.py, the brand gate.

Brand colors and the brand typeface are two of the owner's five floor
invariants for the freeform lane, and the lane's adoption brief left both to
prose. Every case below proves the gate fires on off-brand input; the clean
fixture (palette colors at various alphas + the brand face) proves it does not
nag on-brand work.

Run:  python3 tests/test_brand.py   (exit 0 = all pass)
"""
import shutil
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))

import check_brand

sys.path.insert(0, str(Path(__file__).resolve().parent))
from firing import fires as _fires

PASS = FAIL = 0
TMP = Path(tempfile.gettempdir()) / "scla-brand-tests"


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}  {detail}")


def fires(checker, rule, label, cond, detail=""):
    return _fires(check, checker, rule, label, cond, detail)


CLEAN = """<template>
  <style>
    @font-face { font-family: 'Proxima Nova'; src: url('../assets/fonts/proxima-nova-700.woff2'); }
    #root { background: #0a1e2f; font-family: 'Proxima Nova', system-ui, sans-serif; }
    .big  { color: #ffffff; }
    .sub  { color: rgba(255, 255, 255, 0.78); }
    .rule { background: #eaab2d; }
  </style>
  <div id="root"><div class="big" style="border-color: #3393d6">Hello</div></div>
</template>"""


def ws_with(comp_html, fonts=True):
    ws = TMP / "ws"
    shutil.rmtree(ws, ignore_errors=True)
    (ws / "compositions").mkdir(parents=True)
    (ws / "compositions" / "main.html").write_text(comp_html)
    (ws / "index.html").write_text('<div id="root" data-duration="10"></div>')
    if fonts:
        (ws / "assets" / "fonts").mkdir(parents=True)
        (ws / "assets" / "fonts" / "proxima-nova-700.woff2").write_bytes(b"\0")
    return ws


def rules_of(problems):
    return [getattr(p, "rule_id", "?") for p in (problems or [])]


_, problems = check_brand.check(ws_with(CLEAN))
check("brand palette at any alpha + the brand face passes",
      not problems, str(problems))

_, problems = check_brand.check(ws_with(CLEAN.replace("#eaab2d", "#ff6600")))
fires("check_brand", "off-color",
      "an off-palette hex fires off-brand-color",
      "off-brand-color" in rules_of(problems), str(problems))

_, problems = check_brand.check(ws_with(CLEAN.replace(
    "'Proxima Nova', system-ui, sans-serif", "Georgia, serif")))
fires("check_brand", "off-font",
      "a font stack leading with a non-brand face fires off-brand-font",
      "off-brand-font" in rules_of(problems), str(problems))

_, problems = check_brand.check(ws_with(CLEAN), )
_, problems = check_brand.check(ws_with(CLEAN, fonts=False))
fires("check_brand", "missing-font-asset",
      "an @font-face src with no vendored file fires missing-font-asset",
      "missing-font-asset" in rules_of(problems), str(problems))

allowed = CLEAN.replace(
    ".rule { background: #eaab2d; }",
    ".vig { background: rgba(6, 20, 32, 0.72); /* brand-allow: vignette */ }")
_, problems = check_brand.check(ws_with(allowed))
check("a declared /* brand-allow */ exception is honoured",
      not problems, str(problems))

bare = ws_with("<template><style>#root { opacity: 1; }</style></template>")
_, problems = check_brand.check(bare)
fires("check_brand", "nothing-graded",
      "a build with no gradeable color or font fails loud, never passes",
      "nothing-graded" in rules_of(problems), str(problems))

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
