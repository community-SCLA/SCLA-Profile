#!/usr/bin/env python3
"""Create an immutable, content-addressed source checkpoint for a workspace.

The canonical workspace is intentionally resumed in place. Before an agent can
change it, this tool captures the exact render-affecting source selected by
``workspace_revision.revision_files`` under::

    source-revisions/<sha256>/

QA evidence, snapshots, and caches are omitted by that shared selector.
Illustrations, fonts, music, HTML, timing, and other authored inputs are copied
into the revision directory. Voice binaries are retained through manifest
references into ``source-revisions/.blobs/<sha256>`` so the exact rendition is
recoverable without duplicating unchanged narration in every checkpoint. A
digest is written once and never overwritten, making repeated resumes with
unchanged source idempotent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from workspace_revision import checkpoint_files, revision_files, workspace_revision


MANIFEST_NAME = "manifest.json"
SCHEMA_VERSION = 2
BLOB_DIR_NAME = ".blobs"
_HEX_DIGITS = frozenset("0123456789abcdef")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path) -> tuple[int, str]:
    """Return a stable file size and digest, refusing an in-flight rewrite."""

    before = path.stat()
    digest = _sha256(path)
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
    return before.st_size, digest


def _manifest_entry(source: Path, relative: Path) -> dict[str, object]:
    if source.is_symlink():
        return {
            "path": relative.as_posix(),
            "kind": "symlink",
            "target": os.readlink(source),
        }
    size, digest = _fingerprint(source)
    return {
        "path": relative.as_posix(),
        "kind": "file",
        "bytes": size,
        "sha256": digest,
    }


def _blob_manifest_entry(source: Path, relative: Path) -> dict[str, object]:
    size, digest = _fingerprint(source)
    return {
        "path": relative.as_posix(),
        "kind": "blob",
        "bytes": size,
        "sha256": digest,
        "blob": f"{BLOB_DIR_NAME}/{digest}",
    }


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _HEX_DIGITS for character in value)
    )


def _entry_relative(entry: dict[str, object]) -> Path:
    raw = entry.get("path")
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise ValueError(f"checkpoint manifest has an unsafe path: {raw!r}")
    relative = Path(raw)
    if (
        relative.is_absolute()
        or relative.as_posix() != raw
        or any(part in ("", ".", "..") for part in relative.parts)
    ):
        raise ValueError(f"checkpoint manifest has an unsafe path: {raw!r}")
    return relative


def _verify_file(path: Path, size: object, digest: object) -> None:
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError(f"checkpoint has an invalid byte count for {path}: {size!r}")
    if not _is_sha256(digest):
        raise ValueError(f"checkpoint has an invalid SHA-256 for {path}: {digest!r}")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"checkpoint file is missing or not regular: {path}")
    actual_size, actual_digest = _fingerprint(path)
    if actual_size != size or actual_digest != digest:
        raise ValueError(f"checkpoint hash mismatch: {path}")


def _verify_symlink(path: Path, target: object) -> None:
    if not isinstance(target, str) or not path.is_symlink():
        raise ValueError(f"checkpoint symlink is missing or invalid: {path}")
    if os.readlink(path) != target:
        raise ValueError(f"checkpoint symlink target mismatch: {path}")


def _read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"checkpoint manifest cannot be read: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"checkpoint manifest is not an object: {path}")
    return payload


def _validate_checkpoint(
    checkpoint: Path,
    revision: str,
    workspace_name: str,
    expected_paths: set[str],
) -> None:
    """Verify that every recovery entry exists and still matches its hash."""

    manifest_path = checkpoint / MANIFEST_NAME
    manifest = _read_manifest(manifest_path)
    if manifest.get("schema_version") not in (1, SCHEMA_VERSION):
        raise ValueError(f"unsupported checkpoint schema: {manifest_path}")
    if manifest.get("revision") != revision:
        raise ValueError(f"checkpoint revision mismatch: {manifest_path}")
    if manifest.get("workspace") != workspace_name:
        raise ValueError(f"checkpoint workspace mismatch: {manifest_path}")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError(f"checkpoint manifest has no file list: {manifest_path}")
    if manifest.get("file_count") != len(entries):
        raise ValueError(f"checkpoint file count mismatch: {manifest_path}")

    actual_paths: set[str] = set()
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise ValueError(f"checkpoint manifest has an invalid entry: {manifest_path}")
        relative = _entry_relative(raw_entry)
        relative_text = relative.as_posix()
        if relative_text in actual_paths:
            raise ValueError(f"checkpoint manifest repeats {relative_text}")
        actual_paths.add(relative_text)

        kind = raw_entry.get("kind")
        if kind == "file":
            _verify_file(
                checkpoint / relative,
                raw_entry.get("bytes"),
                raw_entry.get("sha256"),
            )
        elif kind == "symlink":
            _verify_symlink(checkpoint / relative, raw_entry.get("target"))
        elif kind == "blob":
            digest = raw_entry.get("sha256")
            expected_blob = f"{BLOB_DIR_NAME}/{digest}"
            if raw_entry.get("blob") != expected_blob or not _is_sha256(digest):
                raise ValueError(
                    f"checkpoint manifest has an invalid blob reference for {relative_text}"
                )
            _verify_file(
                checkpoint.parent / expected_blob,
                raw_entry.get("bytes"),
                digest,
            )
        else:
            raise ValueError(
                f"checkpoint manifest has an unknown entry kind for {relative_text}: {kind!r}"
            )

    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        raise ValueError(
            "checkpoint manifest does not recover the exact revision; "
            f"missing={missing}, extra={extra}"
        )


def _verify_workspace_revision(workspace: Path, expected: str) -> None:
    current = workspace_revision(workspace)
    if current != expected:
        raise ValueError(
            "workspace source changed while its checkpoint was being copied; "
            "resume refused so a mixed revision cannot be recorded"
        )


def _publish_blob(staged: Path, blob_root: Path, size: int, digest: str) -> Path:
    """Install a verified blob once without replacing a concurrent writer."""

    blob_root.mkdir(parents=True, exist_ok=True)
    destination = blob_root / digest
    if destination.exists() or destination.is_symlink():
        _verify_file(destination, size, digest)
        return destination
    try:
        os.link(staged, destination)
    except FileExistsError:
        pass
    _verify_file(destination, size, digest)
    return destination


def create_source_checkpoint(workspace: Path) -> Path:
    """Capture ``workspace`` source once and return its revision directory."""

    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise FileNotFoundError(f"workspace not found: {workspace}")

    revision = workspace_revision(workspace)
    if not revision or any(sep in revision for sep in ("/", "\\")):
        raise ValueError(f"unsafe workspace revision: {revision!r}")

    selected = revision_files(workspace)
    expected_paths = {
        path.relative_to(workspace).as_posix()
        for path in selected
    }
    directly_copied = {
        path.relative_to(workspace).as_posix()
        for path in checkpoint_files(workspace)
    }
    if not directly_copied.issubset(expected_paths):
        raise ValueError("workspace source changed while checkpoint files were selected")

    checkpoint_root = workspace / "source-revisions"
    checkpoint = checkpoint_root / revision
    manifest_path = checkpoint / MANIFEST_NAME
    if checkpoint.exists():
        if not manifest_path.is_file():
            raise FileExistsError(
                f"checkpoint exists without a manifest; refusing to overwrite: {checkpoint}"
            )
        _verify_workspace_revision(workspace, revision)
        _validate_checkpoint(checkpoint, revision, workspace.name, expected_paths)
        _verify_workspace_revision(workspace, revision)
        return checkpoint

    checkpoint_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{revision}.", dir=checkpoint_root))
    staged_blob_root = staging / BLOB_DIR_NAME
    blob_root = checkpoint_root / BLOB_DIR_NAME
    entries: list[dict[str, object]] = []
    pending_blobs: dict[str, tuple[Path, int]] = {}
    try:
        for source in selected:
            relative = source.relative_to(workspace)
            relative_text = relative.as_posix()
            if relative_text in directly_copied:
                entry = _manifest_entry(source, relative)
                destination = staging / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination, follow_symlinks=False)
                if entry["kind"] == "symlink":
                    _verify_symlink(destination, entry.get("target"))
                else:
                    _verify_file(destination, entry.get("bytes"), entry.get("sha256"))
                entries.append(entry)
                continue

            if source.is_symlink() or not source.is_file():
                raise ValueError(f"voice blob source is not a regular file: {source}")
            entry = _blob_manifest_entry(source, relative)
            digest = str(entry["sha256"])
            size = int(entry["bytes"])
            existing_blob = blob_root / digest
            if existing_blob.exists() or existing_blob.is_symlink():
                _verify_file(existing_blob, size, digest)
            elif digest not in pending_blobs:
                staged_blob_root.mkdir(parents=True, exist_ok=True)
                staged_blob = staged_blob_root / digest
                shutil.copy2(source, staged_blob)
                _verify_file(staged_blob, size, digest)
                pending_blobs[digest] = (staged_blob, size)
            else:
                staged_blob, staged_size = pending_blobs[digest]
                if staged_size != size:
                    raise ValueError(f"voice blob size mismatch for digest {digest}")
                _verify_file(staged_blob, size, digest)
            entries.append(entry)

        _verify_workspace_revision(workspace, revision)

        for digest, (staged_blob, size) in pending_blobs.items():
            _publish_blob(staged_blob, blob_root, size, digest)
        for entry in entries:
            if entry.get("kind") == "blob":
                _verify_file(
                    checkpoint_root / str(entry["blob"]),
                    entry.get("bytes"),
                    entry.get("sha256"),
                )

        _verify_workspace_revision(workspace, revision)
        if staged_blob_root.exists():
            shutil.rmtree(staged_blob_root)

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "revision": revision,
            "workspace": workspace.name,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "file_count": len(entries),
            "files": entries,
        }
        (staging / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        # Another resume may have completed the same digest while this process
        # was copying.  Never replace it; discard only our private staging dir.
        if checkpoint.exists():
            shutil.rmtree(staging)
            _validate_checkpoint(checkpoint, revision, workspace.name, expected_paths)
            _verify_workspace_revision(workspace, revision)
            return checkpoint
        try:
            staging.rename(checkpoint)
        except OSError:
            if not checkpoint.exists():
                raise
            shutil.rmtree(staging, ignore_errors=True)
        _validate_checkpoint(checkpoint, revision, workspace.name, expected_paths)
        _verify_workspace_revision(workspace, revision)
        return checkpoint
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Checkpoint a HyperFrames workspace before in-place resume edits."
    )
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    try:
        checkpoint = create_source_checkpoint(args.workspace)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"source_checkpoint.py: {exc}\n")
    print(checkpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
