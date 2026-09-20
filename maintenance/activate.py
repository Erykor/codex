#!/usr/bin/env python3
"""Activate a complete local Linux fork; retain the previous executable for rollback."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile


def require_executable(path):
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f"Missing executable: {path}")


def replace_link(path, target):
    # Reserve a unique name in the same filesystem as the destination.
    with tempfile.TemporaryDirectory(prefix=".codex-link-", dir=path.parent) as tmp:
        staged = Path(tmp) / "link"
        staged.symlink_to(target)
        os.replace(staged, path)


def activate(package, bin_dir, previous_executable=None):
    package = package.resolve(strict=True)
    manifest = json.loads((package / "codex-package.json").read_text())
    if (
        manifest.get("target"),
        manifest.get("variant"),
        manifest.get("layoutVersion"),
    ) != ("x86_64-unknown-linux-gnu", "codex", 1):
        raise ValueError("Expected a canonical x86_64 Linux GNU Codex package")
    for relative in (
        "bin/codex",
        "bin/codex-code-mode-host",
        "codex-path/rg",
        "codex-resources/bwrap",
        "codex-resources/zsh/bin/zsh",
    ):
        require_executable(package / relative)
    candidate = package / "bin/codex"
    subprocess.run([str(candidate), "--version"], check=True, timeout=30)
    subprocess.run(
        [str(candidate.with_name("codex-code-mode-host")), "--help"],
        check=True,
        timeout=30,
        stdout=subprocess.DEVNULL,
    )
    bin_dir.mkdir(parents=True, exist_ok=True)
    with (bin_dir / ".codex-fork-activate.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        links = {
            name: bin_dir / name for name in ("codex", "codex-fork", "codex-stable")
        }
        for path in links.values():
            if path.exists() and not path.is_symlink():
                raise ValueError(f"Refusing to replace a non-symlink: {path}")
        previous = links["codex"].resolve(strict=True)
        require_executable(previous)
        require_executable(previous.with_name("codex-code-mode-host"))
        if previous != candidate:
            rollback = (
                previous_executable.resolve(strict=True)
                if previous_executable
                else previous
            )
            require_executable(rollback)
            require_executable(rollback.with_name("codex-code-mode-host"))
            replace_link(links["codex-stable"], rollback)
        replace_link(links["codex-fork"], candidate)
        replace_link(links["codex"], candidate)
        print(f"codex -> {candidate}")
        print(f"codex-stable -> {links['codex-stable'].resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
    parser.add_argument(
        "--previous-executable",
        type=Path,
        help="Explicit known-good rollback when the current version is defective",
    )
    args = parser.parse_args()
    activate(args.package, args.bin_dir, args.previous_executable)
