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


# ---------------------------------------------------------------------------
# Freeform (agent-native) beat manifest + on-frame text (2026-07-30)
#
# A freeform build carries no data-narration / data-variable-values — those are
# build_index.py's private authoring protocol, not HyperFrames contract. Its
# narration contract is audio_request.json (the audio engine's own input:
# lines[{id,text}]) plus timing.json once computed. This adapter is the §1
# coupling fix from docs/HANDOFF-agent-native-verdict-2026-07-30.md: without
# it, every parse_scenes() consumer exits 0 having graded nothing.
# ---------------------------------------------------------------------------

def load_beats(ws: Path):
    """Scene-shaped beat dicts for a freeform workspace, or None if no
    audio_request.json exists. Shaped like parse_scenes() entries so every
    narration rule runs on them unchanged; `duration` is the beat's visual
    span from timing.json when present (NaN before timings are computed)."""
    req = Path(ws) / "audio_request.json"
    if not req.exists():
        return None
    lines = (json.loads(req.read_text(encoding="utf-8")) or {}).get("lines") or []
    rows = {}
    tp = Path(ws) / "timing.json"
    if tp.exists():
        t = json.loads(tp.read_text(encoding="utf-8"))
        rows = {r.get("id"): r for r in (t.get("rows") or [])}
    beats = []
    for i, ln in enumerate(lines):
        if isinstance(ln, str):
            bid, text = f"s{i + 1:02d}", ln
        else:
            bid = ln.get("id") or f"s{i + 1:02d}"
            text = ln.get("text") or ""
        r = rows.get(bid) or {}
        beats.append({
            "narration": text, "tag": "", "span": (0, 0), "id": bid,
            "comp": "?", "anchor_end": None, "cue_anchors": None,
            "variables": {},
            "start": float(r.get("vis_start", "nan")),
            "duration": float(r.get("vis_dur", "nan")),
        })
    return beats


def load_words(ws: Path):
    """Flat [{start, end, text}] narration words on an ABSOLUTE timeline, or []
    if this workspace carries none.

    Three shapes, in preference order:
      1. assets/voice/transcript.json      — Whisper/kokoro fallback, flat
      2. assets/voice/narration.words.json — HeyGen default path, flat
      3. audio_meta.json + timing.json     — the FREEFORM shape: one wav and one
         word list PER BEAT, each timed from its own clip zero, so every word
         must be offset by that beat's `audio_start` from timing.json.

    Shape 3 is why this helper exists. check_presence.py looked only for the two
    flat files; a freeform build has neither, so `words` came back empty and its
    `not words` fallback made EVERY static run gradeable regardless of speech —
    the gate ran stricter than designed and could not have reported why
    (HANDOFF-agent-native-verdict-2026-07-30 §2: "survives, stricter AND
    blind"). A deliberate silent hold — the 1.8s FINAL_HOLD every lesson ends
    on — is exactly what that mode would eventually fail.
    """
    ws = Path(ws)
    voice = ws / "assets" / "voice"
    for name in ("transcript.json", "narration.words.json"):
        p = voice / name
        if p.exists():
            try:
                flat = json.loads(p.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
            return [w for w in flat
                    if isinstance(w, dict) and "start" in w and "end" in w]

    meta, timing = ws / "audio_meta.json", ws / "timing.json"
    if not meta.exists():
        return []
    try:
        m = json.loads(meta.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    offsets = {}
    if timing.exists():
        try:
            t = json.loads(timing.read_text(encoding="utf-8"))
            offsets = {r.get("id"): float(r.get("audio_start", 0.0))
                       for r in (t.get("rows") or [])}
        except (ValueError, OSError, TypeError):
            offsets = {}
    words = []
    for v in (m.get("voices") or []):
        off = offsets.get(v.get("id"), 0.0)
        for w in (v.get("words") or []):
            try:
                words.append({"text": w.get("text", ""),
                              "start": off + float(w["start"]),
                              "end": off + float(w["end"])})
            except (KeyError, TypeError, ValueError):
                continue
    words.sort(key=lambda w: w["start"])
    return words


def speech_in(words, a: float, b: float) -> bool:
    """Does any narration word overlap [a, b)? True when there are no words at
    all is NOT the contract — callers decide what an absent transcript means,
    because 'silently grade everything' and 'silently grade nothing' are both
    ways for a gate to lie about its coverage."""
    return any(w["start"] < b and w["end"] > a for w in words)


_STYLE_SCRIPT_RE = re.compile(r"<(style|script)\b[^>]*>.*?</\1\s*>", re.S | re.I)


def _clean_text(fragment: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


def onframe_strings(ws: Path):
    """[(file, role, text)] for every visible markup string in a freeform
    build — index.html plus compositions/*.html, including markup inside
    <template> (where sub-composition content lives).

    role is "heading" for <h1>–<h3> or any element declaring
    data-role="heading" (the freeform contract's one required annotation —
    Title Case is graded on these), "text" for every other text node. Copy
    built up in JS string literals is invisible to this scan, which is why the
    freeform contract requires on-frame copy to live in markup."""
    ws = Path(ws)
    files = []
    if (ws / "index.html").exists():
        files.append(ws / "index.html")
    files += sorted(ws.glob("compositions/*.html"))
    out = []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        headings = set()
        for m in re.finditer(r"<(h[1-3])\b[^>]*>(.*?)</\1\s*>", raw, re.S | re.I):
            t = _clean_text(m.group(2))
            if t and t not in headings:
                headings.add(t)
                out.append((f.name, "heading", t))
        for m in re.finditer(
                r"""<([a-zA-Z][\w-]*)\b[^>]*data-role\s*=\s*["']heading["']"""
                r"""[^>]*>(.*?)</\1\s*>""", raw, re.S | re.I):
            t = _clean_text(m.group(2))
            if t and t not in headings:
                headings.add(t)
                out.append((f.name, "heading", t))
        body = _STYLE_SCRIPT_RE.sub(" ", raw)
        body = re.sub(r"<[^>]+>", "\x00", body)
        for chunk in body.split("\x00"):
            t = re.sub(r"\s+", " ", html.unescape(chunk)).strip()
            if t and t not in headings:
                out.append((f.name, "text", t))
    return out


def sample_units(ws: Path):
    """The sampling grid every time-sampled gate walks: one unit per BEAT.

    Template path: scene clips already are beats (one narration span each), so
    the clips are the grid. Freeform path: a clip is an ACT (the agent-native
    reference has 3 clips on a 200s video), so sampling per clip starves every
    sampler — 27 → 3 layout samples, 81 → 9 verify stills (HANDOFF §2). There
    the grid is timing.json's beat rows via load_beats(). Falls back to clips
    when no usable beat timing exists; callers treat an empty grid as
    ungradeable, never as clean."""
    ws = Path(ws)
    scenes = parse_scenes((ws / "index.html").read_text(
        encoding="utf-8", errors="replace"))

    def timed(units):
        out = []
        for u in units:
            start, dur = u.get("start"), u.get("duration")
            if not isinstance(start, (int, float)) or not isinstance(dur, (int, float)):
                continue
            if start != start or dur != dur or dur <= 0:  # NaN / placeholder
                continue
            out.append(u)
        return out

    if not any(s["narration"] is not None for s in scenes):
        beats = timed(load_beats(ws) or [])
        if beats:
            return beats
    return timed(scenes)


def json_attr(value) -> str:
    """JSON for a single-quoted HTML attribute. ASCII apostrophes inside content
    are replaced with U+2019 (house style is typographic anyway) so the
    attribute can never be truncated by its own delimiter."""
    s = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return s.replace("'", "’")


# ---------------------------------------------------------------------------
# Typed findings (2026-07-29)
# ---------------------------------------------------------------------------
class Finding(str):
    """A finding string that also carries a stable `rule_id` and `severity`.

    The checkers grew as text tools: each appends a formatted sentence to a
    `problems` list, and everything downstream — printing, joining, the
    substring assertions in tests — treats those as plain strings. Machine
    consumers had nothing stable to key on, so anything reading a finding had
    to match on prose that changes whenever the wording improves.

    Subclassing `str` means a Finding IS the sentence: every existing print,
    join, `in` test and f-string keeps working untouched, while `--json` can
    read the tag. Crucially the tag is attached AT THE POINT THE FINDING IS
    CREATED, beside the rule that produced it — never inferred afterwards from
    the text, which is the mistake this whole build exists to stop repeating.

        problems.append(Finding("dangling-conjunction", f"{sid}: ..."))

    Severity is "error" unless stated. Nothing in the pipeline branches on it
    yet — exit codes remain the verdict (they are the one part of this pipeline
    that has never lied); it is here so a consumer can rank findings without
    parsing English.
    """
    __slots__ = ("rule_id", "severity")

    def __new__(cls, rule_id: str, text: str, severity: str = "error"):
        obj = super().__new__(cls, text)
        obj.rule_id = rule_id
        obj.severity = severity
        return obj


def typed(findings) -> list:
    """[{rule_id, severity, detail}] for a list of Finding-or-plain-str.

    An untagged string reports rule_id "unclassified" rather than being dropped
    or guessed at: a machine consumer must be able to SEE the coverage hole.
    """
    out = []
    for f in findings:
        out.append({
            "rule_id": getattr(f, "rule_id", "unclassified"),
            "severity": getattr(f, "severity", "error"),
            "detail": str(f),
        })
    return out
