#!/usr/bin/env python3
"""Identity of the deterministic SCLA release gate.

A source revision proves which lesson bytes were checked. It does not prove
which checker code judged them. This digest binds a green preflight receipt to
the complete deterministic gate implementation and its pinned browser runtime,
so adding or changing a checker automatically invalidates older green markers.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


SRC = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]


def contract_files() -> list[Path]:
    files = sorted(SRC.glob("*.py"))
    files.extend([
        REPO / "scripts" / "build-gate.sh",
        REPO / "projects" / "video-production" / "design-system" / "package.json",
        REPO / "projects" / "video-production" / "design-system" / "package-lock.json",
    ])
    return [path for path in files if path.is_file()]


def gate_contract_revision() -> str:
    digest = hashlib.sha256()
    for path in contract_files():
        relative = path.relative_to(REPO).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: gate_contract.py", file=sys.stderr)
        return 2
    print(gate_contract_revision())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
