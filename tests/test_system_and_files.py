import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dotfiles.files import append_unique_line, create_symlink
from dotfiles.system import detect_platform


class PlatformTests(unittest.TestCase):
    def test_normalizes_operating_system_and_architecture(self):
        cases = (
            ("Darwin", "arm64", ("darwin", "arm64")),
            ("Linux", "aarch64", ("linux", "arm64")),
            ("Linux", "AMD64", ("linux", "x86_64")),
        )

        for system, machine, expected in cases:
            with self.subTest(system=system, machine=machine):
                with (
                    patch("dotfiles.system.platform.system", return_value=system),
                    patch("dotfiles.system.platform.machine", return_value=machine),
                ):
                    self.assertEqual(detect_platform(), expected)


class FileOperationTests(unittest.TestCase):
    def test_symlink_backs_up_conflict_and_is_idempotent(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "config" / "destination"
            backup_root = root / "backups"
            source.write_text("managed\n")
            destination.parent.mkdir()
            destination.write_text("original\n")

            create_symlink(source, destination, backup_root)
            create_symlink(source, destination, backup_root)

            self.assertTrue(destination.is_symlink())
            self.assertEqual(destination.resolve(), source.resolve())
            backups = list(backup_root.iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "original\n")

    def test_append_unique_line_is_idempotent(self):
        with TemporaryDirectory() as directory:
            profile = Path(directory) / "profile"

            append_unique_line(profile, "export EXAMPLE=1")
            append_unique_line(profile, "export EXAMPLE=1")

            self.assertEqual(profile.read_text(), "export EXAMPLE=1\n")


if __name__ == "__main__":
    unittest.main()
