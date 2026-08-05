#!/usr/bin/env python3
"""Pin an audio request to the production voice declared in tokens.yml."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tokens import load


def expected(ws: Path) -> dict:
    voice = load(ws).get("voice") or {}
    return {"provider": voice.get("provider"), "voice": voice.get("voice_id"),
            "speed": float(voice.get("speed", 1.0))}


def apply(ws: Path, check_only: bool = False) -> list[str]:
    path = ws / "audio_request.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    want = expected(ws)
    problems = []
    for key, value in want.items():
        actual = request.get(key)
        if key == "speed" and actual is not None:
            actual = float(actual)
        if actual != value:
            problems.append(f"{key}: {actual!r} != production {value!r}")
    if not check_only:
        request.update(want)
        path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return problems


def stamp_meta(ws: Path) -> None:
    """Record the effective request beside the provider's response.

    The shared audio engine reports provider and voice but historically omitted
    speed. The wrapper calls this only after synthesis succeeds, making the
    metadata a complete receipt for the request that produced the files.
    """
    request = json.loads((ws / "audio_request.json").read_text(encoding="utf-8"))
    meta_path = ws / "audio_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["speed"] = float(request["speed"])
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stamp-meta", action="store_true")
    args = parser.parse_args()
    ws = args.workspace.resolve()
    if args.stamp_meta:
        stamp_meta(ws)
        print("[audio_contract] metadata receipt written")
        return 0
    problems = apply(ws, args.check)
    if args.check and problems:
        print("[audio_contract] FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("[audio_contract] OK" if args.check else "[audio_contract] production voice pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
