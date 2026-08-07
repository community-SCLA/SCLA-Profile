#!/usr/bin/env python3
"""One-command post-render gate + shared QA evidence generator.

Run immediately after `npm run render`. Does three jobs in one pass:

  1. Container truth — ffprobe the MP4: video/audio stream durations vs the
     composition's root duration (±0.15s), resolution 1920×1080, both streams
     present.
  2. Presence v2 — runs check_presence.py with --workspace (entrance-grace,
     content-pixel blank detection, stagnation tripwire, audio-vs-video).
  3. Frame evidence — extracts per-scene strategic frames (start+0.3s,
     midpoint, end−0.3s) at full resolution into <workspace>/qa/frames/,
     named f<time>s_<sceneid>_<pos>.png. This is THE shared frame set: the
     QA lanes and the human gate read these instead of each re-extracting
     their own (one ffmpeg pass instead of four).

Exit 0 = render verified, evidence ready; exit 1 = deterministic defect found
(do not launch agent lanes — fix and re-render first).

Usage:  verify_render.py <workspace> [<video.mp4>] [--json]
        (default MP4: newest file in <workspace>/renders/)
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hfp_common import ffprobe_duration, parse_scenes, sample_units
from workspace_revision import workspace_revision

CHECK_PRESENCE = Path(__file__).resolve().parent / "check_presence.py"
DUR_TOL = 0.15


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    ws = Path(args[0]).resolve()
    if len(args) > 1:
        mp4 = Path(args[1]).resolve()
    else:
        renders = sorted((ws / "renders").glob("*.mp4"),
                         key=lambda p: p.stat().st_mtime)
        if not renders:
            print(f"no MP4 in {ws / 'renders'}", file=sys.stderr)
            sys.exit(2)
        mp4 = renders[-1]

    # Bind every verified MP4 to the exact authored/runtime inputs that
    # produced it. A stem name alone is not a rendition identity: source can
    # be edited in place after a render, and publish must never upload the old
    # MP4 on the strength of a marker for a different cut.
    source_revision = workspace_revision(ws)
    render_marker = ws / "qa" / "RENDER-START.json"
    try:
        render_receipt = json.loads(render_marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        render_receipt = None
        render_problem = f"missing or unreadable {render_marker.name} ({exc})"
    else:
        if not isinstance(render_receipt, dict):
            render_problem = f"{render_marker.name} is not a JSON object"
        elif render_receipt.get("source_revision") != source_revision:
            render_problem = (
                "render started from a different source revision "
                f"({render_receipt.get('source_revision') or 'missing'} != "
                f"{source_revision})"
            )
        elif not isinstance(render_receipt.get("encode_review_required"), bool):
            render_problem = (
                f"{render_marker.name} has no immutable encode-review policy"
            )
        elif (not isinstance(render_receipt.get("attempt"), int)
              or render_receipt.get("attempt") < 1):
            render_problem = f"{render_marker.name} has no valid render attempt"
        else:
            raw_render_mp4 = render_receipt.get("mp4")
            if not isinstance(raw_render_mp4, str) or not raw_render_mp4:
                render_problem = f"{render_marker.name} has no rendered MP4 path"
            else:
                receipt_mp4 = Path(raw_render_mp4)
                if not receipt_mp4.is_absolute():
                    receipt_mp4 = ws / receipt_mp4
                if receipt_mp4.resolve() != mp4:
                    render_problem = (
                        "verification target differs from render-start receipt "
                        f"({mp4} != {receipt_mp4.resolve()})"
                    )
                else:
                    completed_sha = render_receipt.get("completed_sha256")
                    completed_bytes = render_receipt.get("completed_bytes")
                    completed_at = render_receipt.get("completed_at")
                    try:
                        digest = hashlib.sha256()
                        with mp4.open("rb") as source:
                            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                                digest.update(chunk)
                        rendered_sha = digest.hexdigest()
                        rendered_bytes = mp4.stat().st_size
                    except OSError as exc:
                        render_problem = f"rendered MP4 cannot be read ({exc})"
                    else:
                        if (not isinstance(completed_at, str) or not completed_at
                                or not isinstance(completed_bytes, int)
                                or completed_bytes != rendered_bytes
                                or completed_sha != rendered_sha):
                            render_problem = (
                                "render is incomplete or its bytes changed after the "
                                "renderer completed"
                            )
                        else:
                            render_problem = None
    if render_problem:
        # Do not spend minutes grading bytes whose provenance is already
        # invalid, and never leave an older publishable marker behind.
        (ws / "qa" / "VERIFIED").unlink(missing_ok=True)
        result = {
            "verdict": "FAIL",
            "sections": {
                "render_source": {"pass": False, "output": render_problem},
            },
        }
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print(f"VERIFY-RENDER VERDICT: FAIL   ({mp4.name})")
            print(f"\n[!! ] render_source\n  {render_problem}")
        sys.exit(1)

    sections, failed = {
        "mp4": str(mp4),
        "render_source": {
            "pass": True,
            "output": f"render task bound to {source_revision}",
        },
    }, False
    html = (ws / "index.html").read_text()
    scenes = parse_scenes(html)
    root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', html)
    root_dur = float(root.group(1)) if root else None

    # 1. container truth
    v_dur = ffprobe_duration(mp4, "v:0")
    a_dur = ffprobe_duration(mp4, "a:0")
    probs = []
    if v_dur is None:
        probs.append("no video stream")
    if a_dur is None:
        probs.append("no audio stream")
    if v_dur and root_dur and abs(v_dur - root_dur) > DUR_TOL:
        probs.append(f"video stream {v_dur:.2f}s vs root {root_dur:.2f}s "
                     f"(>±{DUR_TOL}s)")
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True).stdout.strip()
    if res and res != "1920,1080":
        probs.append(f"resolution {res} != 1920,1080")
    sections["container"] = {"pass": not probs,
                             "output": "\n".join(probs) or
                                       f"video={v_dur}s audio={a_dur}s root={root_dur}s {res}"}
    failed |= bool(probs)

    # 2. presence v2
    qa_dir = ws / "qa" / "presence"
    p = subprocess.run([sys.executable, str(CHECK_PRESENCE), str(mp4),
                        str(qa_dir), "--workspace", str(ws)],
                       capture_output=True, text=True)
    sections["presence"] = {"pass": p.returncode == 0,
                            "output": (p.stdout + p.stderr).strip()}
    failed |= p.returncode != 0

    # 3. shared frame evidence — purge first: stale frames from an earlier cut
    # misled a QA lane on 2026-07-10; only this render's evidence may live here
    frames_dir = ws / "qa" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("*.png"):
        old.unlink()
    # One unit per BEAT: on the freeform path a scene clip is an act, and
    # per-clip extraction collapsed 81 stills to 9 on a longer video
    # (HANDOFF-agent-native-verdict §2). Template clips are already beats.
    units = sample_units(ws)
    extracted = []
    for sc in units:
        end = sc["start"] + sc["duration"]
        for pos, t in (("early", sc["start"] + 0.3),
                       ("mid", sc["start"] + sc["duration"] / 2),
                       ("late", end - 0.3)):
            t = max(0.0, min(t, (v_dur or end) - 0.05))
            name = f"f{t:07.2f}s_{sc['id']}_{pos}.png"
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                 str(frames_dir / name)], check=False)
            if (frames_dir / name).is_file() and (frames_dir / name).stat().st_size > 0:
                extracted.append(name)
    sections["frames"] = {"pass": bool(units) and len(extracted) == 3 * len(units),
                          "output": f"{len(extracted)} frames ({len(units)} "
                                    f"beats x3) -> {frames_dir}"}
    failed |= not units or len(extracted) != 3 * len(units)

    # 4. monotony — do consecutive beats draw the same picture? The stills above
    # are already on disk and already one-per-beat, so this costs no extra
    # ffmpeg. It is deliberately NOT the freeze rule: this grid is per-beat and
    # far too sparse to measure a 5s hold (check_diversity says so itself, and
    # presence above owns that question authoritatively from the 2fps sampling).
    # Reported, never fatal — the twin threshold is uncalibrated against the
    # owner's reference video, and blocking a ship on an unpinned taste number is
    # how a gate earns its way into being switched off (STD-38).
    # check_diversity's per-pair `twin-beats` finding is retired (BUILD-PLAN
    # B2, 2026-08-04): the owner-approved reference cut scores WORSE on it (2
    # pairs) than the rejected one (0), so a per-pair defect here would have
    # pushed every future build toward the boring cut. `twin_share` — the same
    # underlying measurement, reported rather than flagged per pair — is what
    # replaces it; check_pace.py's `twin-share` rule is the actual (pre-render,
    # blocking) anti-gaming gate. This section stays purely informational.
    try:
        from check_diversity import check as diversity_check
        _rep, _probs, _warns = diversity_check(frames_dir, ws=ws)
        share = _rep.get("twin_share") if _rep else None
        if share is None:
            output = "not graded (stills carry no beat labels)"
        else:
            output = (f"twin_share {share*100:.0f}% of consecutive beat pairs "
                      f"draw the same picture — ADVISORY, not blocking")
        sections["monotony"] = {"pass": True, "output": output}
    except Exception as exc:                       # never fail a ship on advice
        sections["monotony"] = {"pass": True,
                                "output": f"not graded ({exc.__class__.__name__}: {exc})"}

    verdict = "FAIL" if failed else "PASS"

    # The VERIFIED marker is the publish contract: batch-ship.sh --publish
    # uploads exactly the file named here (hash-checked) and refuses to run
    # without it. Written only on PASS; a stale marker is removed on FAIL so
    # a failed re-render can never be published on the strength of an old one.
    marker = ws / "qa" / "VERIFIED"
    if failed:
        marker.unlink(missing_ok=True)
    else:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({
            "mp4": str(mp4), "sha256": rendered_sha,
            "bytes": mp4.stat().st_size,
            "video_s": v_dur,
            "source_revision": source_revision,
            "encode_review_required": render_receipt["encode_review_required"],
            "render_attempt": render_receipt["attempt"],
            "render_task_key": render_receipt.get("task_key"),
            "render_backend": render_receipt.get("backend"),
            "render_started_at": render_receipt.get("started_at"),
        }, indent=2) + "\n")

    if as_json:
        print(json.dumps({"verdict": verdict, "sections": sections}, indent=2))
    else:
        print(f"VERIFY-RENDER VERDICT: {verdict}   ({mp4.name})")
        for name, sec in sections.items():
            if not isinstance(sec, dict):
                continue
            mark = "ok " if sec["pass"] else "!! "
            print(f"\n[{mark}] {name}")
            print("  " + sec["output"].replace("\n", "\n  "))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
