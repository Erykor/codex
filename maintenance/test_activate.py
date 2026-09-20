import json
from pathlib import Path
import tempfile
import unittest

from activate import activate


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.old = self.package("old")
        self.new = self.package("new")
        self.official = self.package("official")
        (self.bin_dir / "codex").symlink_to(self.old / "bin/codex")
        (self.bin_dir / "codex-official").symlink_to(self.official / "bin/codex")

    def package(self, name):
        package = self.root / name
        for relative in (
            "bin/codex",
            "bin/codex-code-mode-host",
            "codex-path/rg",
            "codex-resources/bwrap",
            "codex-resources/zsh/bin/zsh",
        ):
            path = package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o755)
        (package / "codex-package.json").write_text(
            json.dumps(
                {
                    "target": "x86_64-unknown-linux-gnu",
                    "variant": "codex",
                    "layoutVersion": 1,
                }
            )
        )
        return package

    def test_rotation_is_idempotent_and_leaves_official_untouched(self):
        activate(self.new, self.bin_dir)
        activate(self.new, self.bin_dir)
        for name in ("codex", "codex-fork"):
            self.assertEqual((self.bin_dir / name).resolve(), self.new / "bin/codex")
        self.assertEqual(
            (self.bin_dir / "codex-stable").resolve(), self.old / "bin/codex"
        )
        self.assertEqual(
            (self.bin_dir / "codex-official").resolve(), self.official / "bin/codex"
        )

    def test_missing_host_does_not_change_links(self):
        (self.new / "bin/codex-code-mode-host").unlink()
        with self.assertRaises(ValueError):
            activate(self.new, self.bin_dir)
        self.assertEqual((self.bin_dir / "codex").resolve(), self.old / "bin/codex")
        self.assertFalse((self.bin_dir / "codex-stable").exists())

    def test_explicit_rollback_excludes_defective_current_version(self):
        good = self.package("known-good")
        activate(self.new, self.bin_dir, good / "bin/codex")
        self.assertEqual((self.bin_dir / "codex-stable").resolve(), good / "bin/codex")

    def test_regular_file_is_preserved(self):
        (self.bin_dir / "codex-stable").write_text("user file")
        with self.assertRaises(ValueError):
            activate(self.new, self.bin_dir)
        self.assertEqual((self.bin_dir / "codex-stable").read_text(), "user file")
        self.assertEqual((self.bin_dir / "codex").resolve(), self.old / "bin/codex")
