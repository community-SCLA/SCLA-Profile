#!/usr/bin/env python3
"""Shared helpers for the SCLA video pipeline tools.

Transcript loading, token normalization, duplicate-safe phrase matching
(forward-pointer, index-based — the text-equality matching that misfired on
duplicate words like "process." on 2026-07-10 is deliberately not used here),
and scene-slot parsing/rewriting for HyperFrames index.html files.
"""

import html
import json
import re
import subprocess
from pathlib import Path

WORD_RE = re.compile(r"[^0-9a-z]+")


def norm_token(text: str) -> str:
    """Lowercase, strip punctuation — 'somewhere.' -> 'somewhere'."""
    return WORD_RE.sub("", text.lower())


def norm_phrase(phrase: str):
    """Phrase -> list of normalized tokens (empties dropped)."""
    return [t for t in (norm_token(w) for w in phrase.split()) if t]


def load_transcript(path: Path):
    words = json.loads(Path(path).read_text())
    for i, w in enumerate(words):
        w["idx"] = i
        w["norm"] = norm_token(w["text"])
    return words


def find_phrase(words, phrase: str, lo: int, hi: int = None, label: str = ""):
    """Find the first occurrence of a phrase (contiguous normalized tokens)
    in words[lo:hi]. Returns (first_idx, last_idx). Raises with candidates on miss.
    """
    toks = norm_phrase(phrase)
    if not toks:
        raise MatchError(f"{label}: anchor phrase {phrase!r} is empty after normalization")
    hi = len(words) if hi is None else hi
    n = len(toks)
    for i in range(lo, hi - n + 1):
        if all(words[i + j]["norm"] == toks[j] for j in range(n)):
            return i, i + n - 1
    window = " ".join(w["text"] for w in words[lo:hi])
    raise MatchError(
        f"{label}: anchor phrase {phrase!r} not found in transcript window "
        f"[word {lo}..{hi}] — window text: \"{window[:400]}\""
    )


class MatchError(Exception):
    pass


def ffprobe_duration(path: Path, stream: str = None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream, "-show_entries", "stream=duration"]
    else:
        cmd += ["-show_entries", "format=duration"]
    cmd += ["-of", "csv=p=0", str(path)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()
    try:
        return float(out[0])
    except (IndexError, ValueError):
        return None


SCENE_TAG_RE = re.compile(r"<div\b[^>]*data-composition-src[^>]*>", re.S)
AUDIO_TAG_RE = re.compile(r"<audio\b[^>]*>", re.S)
ROOT_TAG_RE = re.compile(r"<div\b[^>]*id=\"root\"[^>]*>", re.S)


def get_attr(tag: str, name: str):
    """Attribute value from a tag string; handles single- or double-quoted.
    Anchored so `id` never matches inside `data-hf-id`."""
    m = re.search(rf"""(?<![\w-]){re.escape(name)}=("([^"]*)"|'([^']*)')""", tag)
    if not m:
        return None
    return m.group(2) if m.group(2) is not None else m.group(3)


def set_attr(tag: str, name: str, value: str, quote: str = '"'):
    """Replace an attribute's value in a tag string (attr must exist)."""
    pattern = rf"""((?<![\w-]){re.escape(name)}=)("[^"]*"|'[^']*')"""
    if not re.search(pattern, tag):
        raise MatchError(f"attribute {name} not present in tag: {tag[:120]}")
    return re.sub(pattern, lambda m: m.group(1) + quote + value + quote, tag, count=1)


def _load_json_attr(raw):
    """json.loads a raw attribute value, HTML-unescaping entity-encoded quotes
    first. Returns None for a missing/empty attribute."""
    if not raw:
        return None
    return json.loads(html.unescape(raw))


def parse_scenes(index_html: str):
    """All scene slots in document order, with their raw tag text."""
    scenes = []
    for m in SCENE_TAG_RE.finditer(index_html):
        tag = m.group(0)
        vv = get_attr(tag, "data-variable-values")
        narration = get_attr(tag, "data-narration")
        scenes.append({
            # per-scene narration text (verbatim script span; HTML-escaped in
            # the attribute — &quot; for inner double quotes). None = legacy
            # single-take authoring.
            "narration": html.unescape(narration) if narration else None,
            "tag": tag,
            "span": m.span(),
            "id": get_attr(tag, "id") or get_attr(tag, "data-composition-id") or "?",
            "comp": get_attr(tag, "data-composition-id") or "?",
            "start": float(get_attr(tag, "data-start") or "nan"),
            "duration": float(get_attr(tag, "data-duration") or "nan"),
            "anchor_end": get_attr(tag, "data-anchor-end"),
            # HTML-unescape before json.loads: a double-quote-wrapped attribute
            # entity-encodes its inner quotes as &quot; (any browser/preview
            # serialize pass emits this). No-op on the single-quote+literal form
            # the writer emits, so both encodings parse. (snag 2026-07-14)
            "cue_anchors": _load_json_attr(get_attr(tag, "data-cue-anchors")),
            "variables": _load_json_attr(vv) or {},
        })
    return scenes


def json_attr(value) -> str:
    """JSON for a single-quoted HTML attribute. ASCII apostrophes inside content
    are replaced with U+2019 (house style is typographic anyway) so the
    attribute can never be truncated by its own delimiter."""
    s = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return s.replace("'", "’")
