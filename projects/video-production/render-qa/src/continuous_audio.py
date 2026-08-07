#!/usr/bin/env python3
"""Batch beat narration into long HeyGen requests, then restore beat clips.

The provider sees one request for a normal SCLA lesson (or a small number of
semantic chunks above the request limit). The rest of the pipeline still gets
one local wav and one word list per beat, so timing and QA remain deterministic.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import wave
from array import array
from pathlib import Path


DEFAULT_MAX_CHARS = 4800
SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
NON_ALNUM = re.compile(r"[^0-9a-z]+")

# A beat clip cut from the middle of a continuous take is a raw sample-index
# slice — no silence guaranteed at either edge, unlike synth_narration.py's
# trim_clip (which cuts at scanned silence and is guarded/faded on purpose).
# Ramp each interior edge to ~0 over EDGE_FADE so the clip doesn't start or
# end mid-waveform — same idiom as compile_timeline._fade_edges /
# synth_narration._fade_edges. Never fade the outer edges of the whole take
# (first beat's head, last beat's tail): synth_narration.trim_clip's docstring
# records the owner catching exactly that loss — "the audio didn't fully
# complete the last word... it got cut off" — when a real edge was faded.
EDGE_FADE = 0.005


def normalized(value: str) -> str:
    return NON_ALNUM.sub("", value.lower())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def request_lines(request: dict) -> list[dict]:
    lines = request.get("lines")
    if not isinstance(lines, list) or not lines:
        raise ValueError("audio_request.json declares no narration lines")
    cleaned = []
    seen = set()
    for index, line in enumerate(lines, 1):
        if not isinstance(line, dict):
            raise ValueError(f"narration line {index} is not an object")
        beat_id = str(line.get("id") or "")
        text = str(line.get("text") or "").strip()
        if not SAFE_ID.fullmatch(beat_id):
            raise ValueError(f"unsafe or missing beat id: {beat_id!r}")
        if beat_id in seen:
            raise ValueError(f"duplicate beat id: {beat_id}")
        if not text:
            raise ValueError(f"empty narration text for {beat_id}")
        seen.add(beat_id)
        cleaned.append({"id": beat_id, "text": text})
    return cleaned


def make_chunks(lines: list[dict], max_chars: int) -> list[dict]:
    if max_chars < 100:
        raise ValueError("max-chars must be at least 100")
    groups: list[list[dict]] = []
    current: list[dict] = []
    used = 0
    for line in lines:
        size = len(line["text"])
        if size > max_chars:
            raise ValueError(
                f"beat {line['id']} is {size} characters; split that beat below {max_chars}")
        added = size + (1 if current else 0)
        if current and used + added > max_chars:
            groups.append(current)
            current, used = [], 0
            added = size
        current.append(line)
        used += added
    if current:
        groups.append(current)
    chunks = []
    for index, group in enumerate(groups, 1):
        chunk_id = "narration" if len(groups) == 1 else f"narration-{index:02d}"
        chunks.append({"id": chunk_id, "text": " ".join(x["text"] for x in group),
                       "beats": group})
    return chunks


def prepare(workspace: Path, output: Path, max_chars: int) -> dict:
    request = read_json(workspace / "audio_request.json")
    chunks = make_chunks(request_lines(request), max_chars)
    provider_request = dict(request)
    provider_request["lines"] = [{"id": x["id"], "text": x["text"]} for x in chunks]
    provider_request["scla_continuous"] = {
        "version": 1, "max_chars": max_chars,
        "chunks": [{"id": x["id"], "beat_ids": [b["id"] for b in x["beats"]]}
                   for x in chunks],
    }
    atomic_json(output, provider_request)
    print(f"[continuous_audio] prepared {len(chunks)} provider request(s) "
          f"for {sum(len(x['beats']) for x in chunks)} beats")
    return provider_request


def wav_data(path: Path):
    with wave.open(str(path), "rb") as handle:
        params = handle.getparams()
        raw = handle.readframes(params.nframes)
    if params.sampwidth != 2:
        raise ValueError(f"{path.name}: expected 16-bit PCM")
    return params, raw


def _fade_edges(seg, chan, fade, fade_in, fade_out):
    """Ramp the head (fade_in) and/or tail (fade_out) of an int16 frame array to
    ~0 over `fade` frames, so a raw mid-take cut doesn't start or end on an
    arbitrary sample value. Same idiom as compile_timeline._fade_edges /
    synth_narration._fade_edges, including the half-segment cap so a short
    beat between two splices never double-scales its middle."""
    n = len(seg) // chan
    if n == 0 or fade <= 0:
        return
    f = min(fade, n // 2 if (fade_in and fade_out) else n)
    if f <= 0:
        return
    if fade_in:
        for p in range(f):
            g = (p + 1) / (f + 1)
            base = p * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)
    if fade_out:
        for p in range(f):
            g = (f - p) / (f + 1)
            base = (n - f + p) * chan
            for c in range(chan):
                seg[base + c] = int(seg[base + c] * g)


def write_slice(path: Path, params, raw: bytes, start_s: float, end_s: float,
                 fade_in: bool = False, fade_out: bool = False) -> float:
    rate, channels, width = params.framerate, params.nchannels, params.sampwidth
    total_frames = len(raw) // (channels * width)
    first = max(0, min(total_frames, int(round(start_s * rate))))
    last = max(first + 1, min(total_frames, int(round(end_s * rate))))
    frame_width = channels * width
    if width != 2:
        raise ValueError(f"{path.name}: expected 16-bit PCM")
    seg = array("h")
    seg.frombytes(raw[first * frame_width:last * frame_width])
    if fade_in or fade_out:
        _fade_edges(seg, channels, int(round(EDGE_FADE * rate)), fade_in, fade_out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(width)
        handle.setframerate(rate)
        handle.writeframes(seg.tobytes())
    return (last - first) / rate


def map_spans(beats: list[dict], words: list[dict], chunk_id: str) -> list[tuple[int, int]]:
    usable = []
    for word in words:
        token = normalized(str(word.get("text") or ""))
        if token:
            usable.append({**word, "norm": token})
    spans, cursor = [], 0
    for beat in beats:
        target = normalized(beat["text"])
        start, combined = cursor, ""
        while cursor < len(usable) and len(combined) < len(target):
            combined += usable[cursor]["norm"]
            cursor += 1
        if combined != target:
            heard = " ".join(x["text"] for x in usable[start:min(cursor + 4, len(usable))])
            raise ValueError(
                f"{chunk_id}/{beat['id']}: provider words do not match narration; "
                f"expected {beat['text']!r}, received near {heard!r}")
        spans.append((start, cursor - 1))
    if any(x["norm"] for x in usable[cursor:]):
        tail = " ".join(x["text"] for x in usable[cursor:cursor + 12])
        raise ValueError(f"{chunk_id}: unmatched provider word tail: {tail!r}")
    words[:] = usable
    return spans


def split(workspace: Path, provider_meta_path: Path, max_chars: int) -> dict:
    request = read_json(workspace / "audio_request.json")
    chunks = make_chunks(request_lines(request), max_chars)
    provider_meta = read_json(provider_meta_path)
    provider_voices = {str(v.get("id")): v for v in provider_meta.get("voices") or []}
    expected = {chunk["id"] for chunk in chunks}
    if set(provider_voices) != expected:
        raise ValueError(
            f"provider returned {sorted(provider_voices)}; expected {sorted(expected)}")

    voices = []
    for chunk in chunks:
        source = provider_voices[chunk["id"]]
        source_path = workspace / str(source.get("path") or "")
        if not source_path.is_file():
            raise ValueError(f"provider audio missing for {chunk['id']}: {source_path}")
        params, raw = wav_data(source_path)
        duration = len(raw) / (params.nchannels * params.sampwidth * params.framerate)
        words = list(source.get("words") or [])
        if not words:
            raise ValueError(f"provider returned no word timestamps for {chunk['id']}")
        spans = map_spans(chunk["beats"], words, chunk["id"])
        for index, (beat, (first, last)) in enumerate(zip(chunk["beats"], spans)):
            word_start = float(words[first]["start"])
            word_end = float(words[last]["end"])
            if index == 0:
                cut_start = 0.0
            else:
                previous_end = float(words[spans[index - 1][1]]["end"])
                cut_start = (previous_end + word_start) / 2.0
            if index + 1 == len(spans):
                cut_end = duration
            else:
                next_start = float(words[spans[index + 1][0]]["start"])
                cut_end = (word_end + next_start) / 2.0
            cut_start = max(0.0, min(cut_start, duration))
            cut_end = max(cut_start + 0.001, min(cut_end, duration))
            rel = f"assets/voice/{beat['id']}.wav"
            actual_duration = write_slice(
                workspace / rel, params, raw, cut_start, cut_end,
                fade_in=index > 0, fade_out=index + 1 != len(spans))
            beat_words = []
            for word_index, word in enumerate(words[first:last + 1]):
                beat_words.append({
                    "id": f"w{word_index}", "text": word["text"],
                    "start": round(float(word["start"]) - cut_start, 3),
                    "end": round(float(word["end"]) - cut_start, 3),
                })
            voices.append({"id": beat["id"], "path": rel,
                           "duration_s": round(actual_duration, 3), "words": beat_words})

    final_meta = dict(provider_meta)
    final_meta["voices"] = voices
    final_meta["total_duration_s"] = round(sum(v["duration_s"] for v in voices), 3)
    final_meta["scla_synthesis"] = {
        "version": 1, "mode": "continuous-chunks", "provider_requests": len(chunks),
        "max_chars": max_chars,
        "chunks": [{"id": x["id"], "beat_ids": [b["id"] for b in x["beats"]]}
                   for x in chunks],
    }
    atomic_json(workspace / "audio_meta.json", final_meta)
    print(f"[continuous_audio] split {len(chunks)} provider request(s) into "
          f"{len(voices)} beat clips")
    return final_meta


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("workspace", type=Path)
    prepare_parser.add_argument("output", type=Path)
    prepare_parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    split_parser = sub.add_parser("split")
    split_parser.add_argument("workspace", type=Path)
    split_parser.add_argument("provider_meta", type=Path)
    split_parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.workspace.resolve(), args.output.resolve(), args.max_chars)
        else:
            split(args.workspace.resolve(), args.provider_meta.resolve(), args.max_chars)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[continuous_audio] FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
