#!/usr/bin/env python3
"""Content identity for a HyperFrames build workspace.

The pipeline's stage receipts must identify the exact source they approved.
This module deliberately hashes authored and render-affecting inputs, including
the voice binaries that make one rendered cut audibly distinct.  Regenerable
evidence, caches, and logs remain outside the revision.  Source checkpoints use
``checkpoint_files`` to copy authored inputs normally while storing voice
binaries once in a shared content-addressed blob store.
Render-affecting symlinks are refused because their target bytes are not an
immutable workspace-local input.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


EXCLUDED_DIRS = {
    ".cache",
    ".hyperframes",
    ".thumbnails",
    ".waveform-cache",
    "cache",
    "caches",
    "node_modules",
    "output",
    "qa",
    "renders",
    "snapshots",
    "source-revisions",
    ".source-revisions",
    "verify",
}
EXCLUDED_FILES = {
    ".build-log.tsv",
    ".DS_Store",
}
VOICE_BINARY_SUFFIXES = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".opus",
    ".wav",
}


def _is_voice_binary(relative: Path) -> bool:
    parts = relative.parts
    return (
        len(parts) >= 3
        and parts[0] == "assets"
        and parts[1] == "voice"
        and relative.suffix.lower() in VOICE_BINARY_SUFFIXES
    )


def revision_files(workspace: Path) -> list[Path]:
    """Return sorted authored/runtime inputs that define a rendered cut.

    Paths are returned under ``workspace``. Generated review evidence and
    caches are excluded. Narration binaries and non-voice media such as
    illustrations, logos, fonts, and BGM remain part of the revision.
    """

    workspace = Path(workspace)
    if not workspace.is_dir():
        raise FileNotFoundError(f"workspace not found: {workspace}")

    selected: list[Path] = []
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace)
        if any(part in EXCLUDED_DIRS for part in relative.parts[:-1]):
            continue
        # A link target can keep the same path while its bytes change, and an
        # out-of-workspace target cannot be frozen safely by source_checkpoint.
        # Fail closed instead of assigning a stable revision to mutable bytes.
        # Generated/cache directory links remain excluded by name.
        if path.is_symlink():
            if (relative.name in EXCLUDED_DIRS
                    or relative.name in EXCLUDED_FILES
                    or relative.suffix.lower() == ".log"):
                continue
            raise ValueError(
                f"render-affecting symlink is not revision-safe: {path}; "
                "freeze it as a regular file inside the workspace"
            )
        if path.is_dir():
            continue
        if relative.name in EXCLUDED_FILES or relative.suffix.lower() == ".log":
            continue
        if path.is_file():
            selected.append(path)
    return sorted(selected, key=lambda path: path.relative_to(workspace).as_posix())


def checkpoint_files(workspace: Path) -> list[Path]:
    """Return revision files copied directly into a source checkpoint.

    Regular voice binaries are stored separately in ``source-revisions/.blobs``
    so identical narration is not copied into every revision. Render-affecting
    symlinks are rejected by :func:`revision_files`; their target bytes could
    otherwise change without changing the link text.
    """

    workspace = Path(workspace)
    return [
        path
        for path in revision_files(workspace)
        if not _is_voice_binary(path.relative_to(workspace))
    ]


def workspace_revision(workspace: Path) -> str:
    """Return the SHA-256 identity of one workspace's render-affecting inputs."""

    workspace = Path(workspace)
    digest = hashlib.sha256()
    for path in revision_files(workspace):
        relative = path.relative_to(workspace).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        if path.is_symlink():
            payload = os.readlink(path).encode("utf-8", errors="surrogateescape")
            digest.update(b"L")
            digest.update(len(payload).to_bytes(8, "big"))
            digest.update(payload)
            if os.readlink(path).encode("utf-8", errors="surrogateescape") != payload:
                raise ValueError(f"source changed while it was being hashed: {path}")
            continue
        digest.update(b"F")
        before = path.stat()
        digest.update(before.st_size.to_bytes(8, "big"))
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        before_identity = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        after_identity = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if before_identity != after_identity:
            raise ValueError(f"source changed while it was being hashed: {path}")
    return digest.hexdigest()


def read_revision_marker(workspace: Path) -> str | None:
    """Read a JSON PREFLIGHT-OK source revision; reject legacy markers."""

    marker = Path(workspace) / "qa" / "PREFLIGHT-OK"
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    revision = payload.get("source_revision") if isinstance(payload, dict) else None
    return revision.strip() if isinstance(revision, str) and revision.strip() else None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: workspace_revision.py WORKSPACE", file=sys.stderr)
        return 2
    try:
        print(workspace_revision(Path(argv[1])))
    except (OSError, ValueError) as exc:
        print(f"workspace_revision.py: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
