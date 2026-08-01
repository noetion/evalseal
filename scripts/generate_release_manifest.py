from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "RELEASE_MANIFEST.sha256"
GIT = ("git", "-c", f"safe.directory={ROOT.as_posix()}")


def _git(*arguments: str) -> bytes:
    return subprocess.run(
        (*GIT, *arguments),
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def _index_paths() -> list[str]:
    return [
        raw.decode("utf-8")
        for raw in _git("ls-files", "--cached", "-z").split(b"\0")
        if raw
    ]


def _render() -> bytes:
    lines = []
    for path in sorted(_index_paths()):
        if path == MANIFEST.name:
            continue
        content = _git("cat-file", "blob", f":{path}")
        lines.append(f"{hashlib.sha256(content).hexdigest()}  {path}\n")
    return "".join(lines).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the release manifest from the exact staged Git blobs."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the current manifest differs from the staged Git blobs",
    )
    args = parser.parse_args()

    unstaged = [
        raw.decode("utf-8")
        for raw in _git("diff", "--name-only", "-z").split(b"\0")
        if raw and raw.decode("utf-8") != MANIFEST.name
    ]
    if unstaged:
        print(
            "refusing to hash unstaged tracked files: " + ", ".join(unstaged),
            file=sys.stderr,
        )
        return 2

    expected = _render()
    if args.check:
        actual = MANIFEST.read_bytes() if MANIFEST.is_file() else b""
        if actual != expected:
            print(
                "RELEASE_MANIFEST.sha256 does not match the staged Git blobs",
                file=sys.stderr,
            )
            return 1
        print("RELEASE_MANIFEST.sha256 matches the staged Git blobs")
        return 0

    with MANIFEST.open("wb") as stream:
        stream.write(expected)
    print(f"Wrote {len(expected.splitlines())} release hashes from staged Git blobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
