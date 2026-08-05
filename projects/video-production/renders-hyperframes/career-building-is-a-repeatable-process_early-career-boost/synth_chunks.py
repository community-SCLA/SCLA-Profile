#!/usr/bin/env python3
"""synth_chunks.py — paced narration synthesis for this workspace.

Same engine, same provider, same pinned voice as a single audio.mjs run
(`.claude/skills/hyperframes-media/scripts/audio.mjs`, HeyGen starfish, Oxana
from tokens.yml). The ONLY thing this adds is PACING: HeyGen's speech endpoint
rate-limits this account at roughly 30 requests per rolling window and returns
HTTP 429; audio.mjs has no backoff, swallows the error and drops the line
("TTS failed — omitted"), so a 38-beat manifest lands ~29/38 no matter how many
times it is re-run — and because audio.mjs REPLACES audio_meta.json's `voices`
array on every run, a retry loses the lines that had already succeeded.

So: synthesize in chunks, sleep between them, and merge each chunk's voices
into audio_meta.json by id. Lines already present with a real wav are skipped,
so a resumed run only asks the provider for what is genuinely missing.

    python3 synth_chunks.py [--chunk 8] [--sleep 75]
"""
import json
import subprocess
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
REPO = WS.parents[3]
ENGINE = REPO / ".claude/skills/hyperframes-media/scripts/audio.mjs"
WITH_SECRETS = REPO / "scripts/with-secrets.sh"


def main():
    argv = sys.argv[1:]

    def opt(name, default, cast=int):
        return cast(argv[argv.index(name) + 1]) if name in argv else default

    chunk_n = opt("--chunk", 8)
    nap = opt("--sleep", 75)

    req = json.loads((WS / "audio_request.json").read_text(encoding="utf-8"))
    meta_path = WS / "audio_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    have = {v["id"]: v for v in (meta.get("voices") or [])
            if (WS / v.get("path", "")).is_file()}

    todo = [ln for ln in req["lines"] if ln["id"] not in have]
    print(f"{len(have)} beat(s) already synthesized, {len(todo)} to go")
    chunks = [todo[i:i + chunk_n] for i in range(0, len(todo), chunk_n)]

    for k, chunk in enumerate(chunks, 1):
        sub = dict(req)
        sub["lines"] = chunk
        rp = WS / f".chunk-request.json"
        op = WS / f".chunk-meta.json"
        rp.write_text(json.dumps(sub, ensure_ascii=False, indent=1))
        if op.exists():
            op.unlink()
        print(f"== chunk {k}/{len(chunks)}: {', '.join(c['id'] for c in chunk)}")
        p = subprocess.run(
            ["bash", str(WITH_SECRETS), "node", str(ENGINE),
             "--request", str(rp), "--hyperframes", str(WS),
             "--out", str(op), "--only", "tts"],
            cwd=WS, capture_output=True, text=True,
            env={**__import__("os").environ, "HYPERFRAMES_TTS_CONCURRENCY": "1"})
        sys.stderr.write(p.stderr)
        got = []
        if op.exists():
            got = json.loads(op.read_text(encoding="utf-8")).get("voices") or []
        for v in got:
            have[v["id"]] = v
        print(f"   +{len(got)} landed ({len(have)}/{len(req['lines'])} total)")
        if k < len(chunks) or len(have) < len(req["lines"]):
            time.sleep(nap)

    order = [ln["id"] for ln in req["lines"]]
    voices = [have[i] for i in order if i in have]
    meta = meta or {}
    meta.update({"tts_provider": "heygen",
                 "voice_id": req.get("voice"),
                 "bgm": None, "sfx": meta.get("sfx", []),
                 "voices": voices,
                 "total_duration_s": round(sum(float(v["duration_s"]) for v in voices), 3)})
    meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    missing = [i for i in order if i not in have]
    print(f"audio_meta.json: {len(voices)}/{len(order)} beats"
          + (f" — MISSING {', '.join(missing)}" if missing else " — complete"))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
