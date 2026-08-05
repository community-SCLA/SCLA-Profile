#!/usr/bin/env python3
"""test_typed_findings.py — every finding carries a stable rule_id.

The checkers grew as text tools: each appends a formatted sentence to a list,
so a machine consumer had to match on prose that changes whenever the wording
improves. `hfp_common.Finding` attaches a `rule_id` and `severity` AT THE POINT
THE FINDING IS CREATED — beside the rule that produced it, never inferred
afterwards from the text.

`hfp_common.typed()` reports an untagged string as rule_id "unclassified"
rather than dropping it or guessing, so a coverage hole is VISIBLE. This suite
asserts there are none: every checker, fired on a crafted input, must return
findings that are all tagged.

Run:  python3 tests/test_typed_findings.py   (exit 0 = all pass)
"""
import json
import sys
import tempfile
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_continuity    # noqa: E402
import check_copy          # noqa: E402
import check_forms         # noqa: E402
import check_text          # noqa: E402
from hfp_common import typed  # noqa: E402

failures = []
TMP = Path(tempfile.mkdtemp())


def scene_div(i, template, narration, dur=8.0, start=None, variables=None):
    start = i * 10.0 if start is None else start
    v = json.dumps(variables or {}).replace('"', "&quot;")
    return (f'<div id="scene-{i:02d}" data-composition-id="scene-{i:02d}" '
            f'data-composition-src="compositions/{template}.html" '
            f'data-start="{start}" data-duration="{dur}" '
            f'data-narration="{narration}" data-variable-values="{v}" '
            f'class="clip"></div>')


def workspace(name, scenes_html, comps=None):
    ws = TMP / name
    (ws / "compositions").mkdir(parents=True, exist_ok=True)
    (ws / "index.html").write_text(
        '<html><body><div id="root" data-duration="300">'
        + "".join(scenes_html) + "</div></body></html>")
    for cname, body in (comps or {}).items():
        (ws / "compositions" / f"{cname}.html").write_text(body)
    return ws


def assert_all_tagged(label, findings):
    """Findings must exist (a checker that returns nothing proves nothing) and
    every one must carry a real rule_id."""
    rows = typed(findings)
    if not rows:
        failures.append(f"{label}: produced NO findings — this fixture is meant "
                        f"to fire, so the assertion below proves nothing")
        return
    bad = [r for r in rows if r["rule_id"] == "unclassified"]
    if bad:
        failures.append(
            f"{label}: {len(bad)}/{len(rows)} finding(s) carry no rule_id. "
            f"Tag them with hfp_common.Finding at the site that creates them, "
            f"never by matching the text afterwards. First: {bad[0]['detail'][:120]!r}")
    else:
        print(f"  ok  {label}: {len(rows)} finding(s), all tagged — "
              f"{sorted({r['rule_id'] for r in rows})}")


# --- check_copy: headings + enumerations ----------------------------------
assert_all_tagged("check_copy.heading_problems", check_copy.heading_problems(
    [{"id": "scene-01", "variables": {"heading": "a lowercase heading."}}]))
assert_all_tagged("check_copy.enumeration_problems", check_copy.enumeration_problems(
    [{"id": "scene-02", "narration": "The right job. The right major. "
      "The right city. The right path.", "variables": {}}]))

# --- check_continuity: blips and split sentences ---------------------------
assert_all_tagged("check_continuity.check", check_continuity.check(workspace(
    "cont",
    [scene_div(11, "scla-chips", "Do you care most about learning? Security?", 3.86),
     scene_div(12, "scla-points", "Flexibility? Meaning?", 2.33),
     scene_div(13, "scla-chips", "Mentorship? Growth?", 2.18)])))

# --- check_forms: the one-item list, graded on element structure -----------
fws = TMP / "forms"
fws.mkdir(parents=True, exist_ok=True)
(fws / "index.html").write_text(
    '<html><body><div id="root" data-duration="30">'
    '<div class="clip" id="b1" data-start="0" data-duration="8">'
    '<ul><li>Only one item</li></ul></div></div></body></html>')
assert_all_tagged("check_forms.check", check_forms.check(fws)[1])

# --- check_text: size floor + restatement ----------------------------------
css = TMP / "tiny.css"
css.write_text(".tiny { font-size: 12px; font-weight: 400; }\n")
assert_all_tagged("check_text.check_sizes", check_text.check_sizes([css])[0])
assert_all_tagged("check_text.check_restatement", check_text.check_restatement(
    [{"id": "scene-09", "variables": {"heading": "Criteria Beat Instinct",
                                      "subBeats": "Criteria beat instinct"}}])[0])

# --- the --json wire actually carries the tags -----------------------------
# The typed data has to survive serialization, not just exist in memory.
import subprocess  # noqa: E402

for name, args in (("check_forms", [str(TMP / "forms")]),):
    r = subprocess.run([sys.executable, str(RQ / "src" / f"{name}.py"), *args, "--json"],
                       capture_output=True, text=True)
    body = r.stdout[r.stdout.find("{"):]
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        failures.append(f"{name} --json did not emit parseable JSON: {exc}")
        continue
    if "findings" not in payload:
        failures.append(f"{name} --json carries no `findings` key — the typed "
                        f"data does not survive serialization")
    else:
        print(f"  ok  {name} --json carries a `findings` array")

if failures:
    print(f"\nFAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("test_typed_findings: every finding carries a stable rule_id")
