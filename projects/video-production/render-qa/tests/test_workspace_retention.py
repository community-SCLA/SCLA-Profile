#!/usr/bin/env python3
"""Lifecycle tests for delivered-workspace retention."""

import shutil
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "scripts" / "archive-lesson.sh"
root = Path(tempfile.mkdtemp(prefix="scla-retention-test-"))
passed = failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  ok  {label}")
    else:
        failed += 1
        print(f"  FAIL {label}: {detail}")


try:
    (root / "scripts").mkdir()
    shutil.copy2(SOURCE, root / "scripts" / SOURCE.name)
    vp = root / "projects" / "video-production"
    run = vp / "run.sh"
    run.parent.mkdir(parents=True)
    run.write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' '{\"agent_queue\":[],\"owner_queue\":[]}'\n",
        encoding="utf-8",
    )
    lessons = vp / "renders-hyperframes"
    (vp / "renders-mp4" / "program-a").mkdir(parents=True)
    ledger = vp / "lesson-scripts" / "published.tsv"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("# base\tprogram\trender_date\twistia_url\n", encoding="utf-8")

    unpublished = lessons / "m1_unpublished"
    (unpublished / "source-revisions" / "old").mkdir(parents=True)
    (unpublished / "snapshots-stale-review").mkdir()
    result = subprocess.run(
        ["bash", str(root / "scripts" / SOURCE.name), unpublished.name, "--in-place"],
        capture_output=True,
        text=True,
    )
    check("unpublished workspace refuses cleanup", result.returncode != 0, result.stderr)
    check(
        "unpublished recovery evidence survives",
        (unpublished / "source-revisions" / "old").is_dir()
        and (unpublished / "snapshots-stale-review").is_dir(),
    )

    published = lessons / "m2_published"
    for relative in (
        "source-revisions/old",
        "snapshots",
        "snapshots-before-owner-review",
        "snapshots-stale-pass",
        "qa",
        "renders",
        "assets/voice",
    ):
        (published / relative).mkdir(parents=True)
    (published / "assets" / "voice" / "narration.wav").write_bytes(b"voice")
    (published / "index.html").write_text("<main>editable</main>", encoding="utf-8")
    ledger.write_text(
        "# base\tprogram\trender_date\twistia_url\n"
        "m2_published\tprogram-a\t2026-08-10\thttps://example.wistia.com/medias/abc123\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["bash", str(root / "scripts" / SOURCE.name), published.name, "--in-place"],
        capture_output=True,
        text=True,
    )
    check("Wistia ledger authorizes delivered cleanup", result.returncode == 0, result.stderr)
    check("published source revisions are pruned", not (published / "source-revisions").exists())
    check(
        "all published snapshot generations are pruned",
        not any(p.name.startswith("snapshots") for p in published.iterdir()),
    )
    check(
        "canonical source and current assets survive",
        (published / "index.html").is_file()
        and (published / "assets" / "voice" / "narration.wav").is_file(),
    )

    active = lessons / "m3_active-revision"
    (active / "source-revisions" / "needed").mkdir(parents=True)
    ledger.write_text(
        ledger.read_text(encoding="utf-8")
        + "m3_active-revision\tprogram-a\t2026-08-01\thttps://example.wistia.com/medias/oldcut\n",
        encoding="utf-8",
    )
    run.write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' "
        "'{\"agent_queue\":[{\"stem\":\"m3_active-revision\"}],\"owner_queue\":[]}'\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["bash", str(root / "scripts" / SOURCE.name), active.name, "--in-place"],
        capture_output=True,
        text=True,
    )
    check("old Wistia row cannot prune an active revision", result.returncode != 0)
    check("active revision checkpoint survives", (active / "source-revisions" / "needed").is_dir())
finally:
    shutil.rmtree(root, ignore_errors=True)

print(f"{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
