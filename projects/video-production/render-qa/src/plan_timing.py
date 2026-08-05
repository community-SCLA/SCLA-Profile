#!/usr/bin/env python3
"""Create timing.json from audio_meta.json using one production policy.

This replaces per-workspace make_timing.py files. It normalizes provider audio,
pads the final clip, updates word timestamps and writes an idempotent timeline.
"""
from __future__ import annotations

import json
import sys
import wave
from array import array
from pathlib import Path

from synth_narration import MAX_INSCENE_GAP, compress_gaps, read_wav, trim_clip
from tokens import load


def write_wav(path: Path, params, data: array) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(params.nchannels)
        handle.setsampwidth(2)
        handle.setframerate(params.framerate)
        handle.writeframes(data.tobytes())


def policy(ws: Path) -> dict[str, float]:
    raw = load(ws).get("timing") or {}
    required = ("lead", "gap", "visual-lead", "final-hold", "video-hold")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"tokens.yml timing is missing: {', '.join(missing)}")
    return {key: float(raw[key]) for key in required}


def hygiene(ws: Path, voice: dict, *, final_hold: float, is_last: bool) -> float:
    path = ws / voice["path"]
    params, data = read_wav(path)
    rate, channels = params.framerate, params.nchannels
    words = [{"text": w["text"], "start": float(w["start"]),
              "end": float(w["end"])} for w in voice.get("words", [])]
    if not words:
        return round(len(data) / channels / rate, 3)
    data, words, cut_s, cuts = compress_gaps(
        data, words, rate, channels, MAX_INSCENE_GAP)
    kept, trim_offset = trim_clip(data, rate, channels, trim_tail=not is_last)
    words = [{"text": w["text"],
              "start": round(w["start"] - trim_offset, 3),
              "end": round(w["end"] - trim_offset, 3)} for w in words]
    if is_last:
        wanted = int(round((max(w["end"] for w in words) + final_hold) * rate))
        have = len(kept) // channels
        if have < wanted:
            kept += array("h", bytes((wanted - have) * 2 * channels))
    write_wav(path, params, kept)
    duration = round(len(kept) / channels / rate, 3)
    voice["duration_s"] = duration
    voice["words"] = [{"id": f"w{i}", **word} for i, word in enumerate(words)]
    if cuts:
        print(f"{voice['id']}: capped {cuts} gap(s), -{cut_s:.2f}s")
    return duration


def build(ws: Path) -> dict:
    settings = policy(ws)
    meta_path, request_path = ws / "audio_meta.json", ws / "audio_request.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    request = json.loads(request_path.read_text(encoding="utf-8"))
    order = [line["id"] for line in request.get("lines", [])]
    voices = {voice["id"]: voice for voice in meta.get("voices", [])}
    if not order or set(order) != set(voices):
        raise ValueError("audio request ids and audio metadata ids differ")

    receipt = meta.get("scla_timing") or {}
    if receipt.get("hygiene_version"):
        if float(receipt.get("final_hold", -1)) != settings["final-hold"]:
            raise ValueError("final-hold changed after audio hygiene; resynthesize audio")
    else:
        for index, beat_id in enumerate(order):
            hygiene(ws, voices[beat_id], final_hold=settings["final-hold"],
                    is_last=index == len(order) - 1)
        meta["scla_timing"] = {"hygiene_version": 1,
                               "final_hold": settings["final-hold"]}
    meta["total_duration_s"] = round(sum(voices[x]["duration_s"] for x in order), 3)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    rows, cursor = [], settings["lead"]
    for beat_id in order:
        voice = voices[beat_id]
        rows.append({"id": beat_id, "audio_start": round(cursor, 3),
                     "audio_dur": round(float(voice["duration_s"]), 3)})
        cursor += float(voice["duration_s"]) + settings["gap"]
    total = round(rows[-1]["audio_start"] + rows[-1]["audio_dur"] +
                  settings["video-hold"], 3)
    for index, row in enumerate(rows):
        row["vis_start"] = (0.0 if index == 0 else
                            round(row["audio_start"] - settings["visual-lead"], 3))
    for index, row in enumerate(rows):
        end = rows[index + 1]["vis_start"] if index + 1 < len(rows) else total
        row["vis_dur"] = round(end - row["vis_start"], 3)
    result = {"total": total, "rows": rows}
    (ws / "timing.json").write_text(json.dumps(result, indent=2) + "\n",
                                     encoding="utf-8")
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: plan_timing.py <workspace>", file=sys.stderr)
        return 2
    try:
        result = build(Path(argv[1]).resolve())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[plan_timing] FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"[plan_timing] OK: {len(result['rows'])} beats, {result['total']:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
