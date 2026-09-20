#!/usr/bin/env python3
"""Build native Linux CLI/host/bwrap with upstream's matching V8 artifacts."""

import os
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[1]
os.environ["CODEX_REPO_ROOT"] = str(repo)
sys.path.insert(0, str(repo / "scripts"))

from codex_package.targets import TARGET_SPECS
from codex_package.v8 import resolve_codex_v8_cargo_env


def main():
    rust_root = repo / "codex-rs"
    rust_info = subprocess.check_output(["rustc", "-vV"], cwd=rust_root, text=True)
    if "host: x86_64-unknown-linux-gnu\n" not in rust_info:
        raise SystemExit("This workflow supports native x86_64 Linux GNU only")
    env = os.environ.copy()
    env.update(resolve_codex_v8_cargo_env(TARGET_SPECS["x86_64-unknown-linux-gnu"]))
    subprocess.run(
        [
            "cargo",
            "build",
            "--locked",
            "--release",
            "--bin",
            "codex",
            "--bin",
            "codex-code-mode-host",
            "--bin",
            "bwrap",
        ],
        cwd=rust_root,
        env=env,
        check=True,
    )


if __name__ == "__main__":
    main()
