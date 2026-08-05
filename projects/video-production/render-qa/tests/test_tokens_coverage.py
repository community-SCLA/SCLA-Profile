#!/usr/bin/env python3
"""test_tokens_coverage.py — a token nobody reads is a red test.

tokens.yml (then the prose spec's frontmatter) carried `spacing.frame-padding: 120` from the day the
system was built. `tokens.py` grew a `frame_padding()` accessor for it. Nothing
ever called that accessor, and the block above it claimed the four
spacing tokens were "LOADED, not quoted: every checker imports from it." The
number was enforced by nothing at all, and the doc said the opposite.

This suite makes that non-recurring, in both directions:

  1. Every normative scalar in tokens.yml has a tokens.py accessor.
     (Scope: `typography.min-size` and `spacing` — the two blocks tokens.yml
     itself annotates as loaded. Colours, the type scale and the voice pin are
     descriptive: they are consumed by template CSS and by synth_narration's
     provider args, not by a Python gate, and claiming otherwise would be the
     same lie in the other direction.)

  2. Every accessor tokens.py exposes has at least one NON-TEST consumer in the
     pipeline. A gate is the only thing that makes a number real; an accessor
     read only by its own test is an orphan wearing a seatbelt.

Run:  python3 tests/test_tokens_coverage.py   (exit 0 = all pass)
"""
import re
import sys
from pathlib import Path

RQ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RQ / "src"))
import tokens  # noqa: E402

failures = []

# frontmatter key -> the tokens.py accessor that must expose it
ACCESSOR_FOR = {
    ("typography", "min-size", "body"):  "min_size",
    ("typography", "min-size", "label"): "min_size",
    ("spacing", "frame-padding"):        "frame_padding",
    ("spacing", "safe-area"):            "safe_area",
    ("spacing", "content-bottom"):       "content_bottom",
}
# spacing.footer-reserve is deliberately absent: no gate reads it directly since
# the template lane retired (2026-08-05) — tokens._footer_reserve() exists only
# to derive content_bottom(), which IS mapped above. spacing.card-gutter lost
# its checker in the same retirement and is an honest Convention in tokens.yml.

# Accessors that are structural rather than a frontmatter scalar.
#
# `slugify` is here because it loads no token at all: it is a pure string helper
# that `programs_problems()` uses to round-trip a display name back to its slug.
# Exempting it is not a bypass of the orphan rule — it is directly unit-tested by
# tests/test_programs.py, and the rule exists to catch a *number* that no gate
# reads, which is not what this is. Do not add a real accessor to this set to
# make the suite go quiet; that is precisely how frame_padding() sat unread.
STRUCTURAL = {"canvas", "load", "tokens_path", "px", "summary", "main", "slugify"}

# Files that may NOT count as a consumer: a token read only by its own test is
# still an orphan. tokens.py itself is excluded for the same reason.
def is_consumer(path: Path) -> bool:
    return (path.name != "tokens.py"
            and "tests" not in path.parts
            and not path.name.startswith("test_"))


# ---------------------------------------------------------------------------
# 1. Every normative frontmatter scalar has an accessor, and it returns a real
#    number rather than a default that happens to look right.
data = tokens.load()
spec = tokens.tokens_path().read_text(encoding="utf-8")
# Reuse tokens.py's own splitter rather than re-deriving the file's shape here:
# a second implementation is a second thing to drift. Handles both a bare
# tokens.yml and the `---`-fenced form a workspace copy may carry.
frontmatter = tokens._split_frontmatter(spec)

declared = set()
block = None
for line in frontmatter.splitlines():
    if re.match(r"^\w[\w-]*:", line):
        block = line.split(":", 1)[0]
        sub = None
    elif re.match(r"^  [\w-]+:", line) and block:
        sub = line.strip().split(":", 1)[0]
        if (block, sub) in ACCESSOR_FOR:
            declared.add((block, sub))
    elif re.match(r"^    [\w-]+:", line) and block:
        leaf = line.strip().split(":", 1)[0]
        if (block, sub, leaf) in ACCESSOR_FOR:
            declared.add((block, sub, leaf))

for key in sorted(ACCESSOR_FOR, key=str):
    name = ACCESSOR_FOR[key]
    dotted = ".".join(key)
    if key not in declared:
        failures.append(f"{dotted} is mapped to tokens.{name}() but no longer "
                        f"appears in tokens.yml — the map has rotted")
        continue
    fn = getattr(tokens, name, None)
    if not callable(fn):
        failures.append(f"tokens.yml declares {dotted} but tokens.py exposes no "
                        f"{name}() to load it")
        continue
    try:
        value = fn()
    except Exception as exc:                      # noqa: BLE001
        failures.append(f"tokens.{name}() raised on the live tokens.yml: {exc}")
        continue
    nums = value if isinstance(value, tuple) else (value,)
    if not all(isinstance(v, (int, float)) and v == v and v > 0 for v in nums):
        failures.append(f"tokens.{name}() returned {value!r} — not a usable "
                        f"number for {dotted}")


# ---------------------------------------------------------------------------
# 2. Every accessor has a non-test consumer. This is the assertion that would
#    have caught frame_padding() sitting unread for the life of the system.
accessors = sorted(
    name for name in dir(tokens)
    if callable(getattr(tokens, name)) and not name.startswith("_")
    and name not in STRUCTURAL
    and getattr(getattr(tokens, name), "__module__", "") == "tokens")

sources = [p for p in sorted((RQ / "src").glob("*.py")) if is_consumer(p)]
for name in accessors:
    call = re.compile(rf"\btokens\.{re.escape(name)}\s*\(")
    users = [p.name for p in sources if call.search(p.read_text(encoding="utf-8"))]
    if not users:
        failures.append(
            f"tokens.{name}() has NO non-test consumer — the tokens.yml number it "
            f"loads is enforced by nothing. Wire it into a checker or delete "
            f"the accessor and say so in tokens.yml; do not leave it looking "
            f"loaded. (This is exactly how spacing.frame-padding sat unread.)")

# Report the wiring so a reader can see it, not just trust it.
print("tokens.yml wiring:")
for name in accessors:
    call = re.compile(rf"\btokens\.{re.escape(name)}\s*\(")
    users = [p.name for p in sources if call.search(p.read_text(encoding="utf-8"))]
    print(f"  {name+'()':<20} -> {', '.join(users) if users else 'NOBODY'}")

if failures:
    print(f"\nFAIL ({len(failures)})")
    for f in failures:
        print("  " + f)
    sys.exit(1)
print(f"test_tokens_coverage: {len(ACCESSOR_FOR)} normative scalar(s) loaded, "
      f"{len(accessors)} accessor(s) consumed by a real gate")
