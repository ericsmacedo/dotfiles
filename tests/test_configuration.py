import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dotfiles.configuration import (
    apply_configurations,
    link_executable_scripts,
    load_mappings,
)


class ConfigurationTests(unittest.TestCase):
    def test_repository_configuration_is_valid(self):
        repository = Path(__file__).resolve().parents[1]

        mappings = load_mappings(repository / "configs", Path("/example-home"))

        self.assertEqual(len(mappings), 10)
        self.assertTrue(all(mapping.platforms for mapping in mappings))

    def test_applies_only_current_platform_and_expands_home(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config_directory = root / "configs"
            home = root / "home"
            config_directory.mkdir()
            home.mkdir()
            (config_directory / "linuxrc").write_text("linux\n")
            (config_directory / "macrc").write_text("mac\n")
            (config_directory / "config.yaml").write_text(
                """configs:
  - src: linuxrc
    dst: ~/.linuxrc
    platform: [linux]
    append:
      file: ~/.profile
      line: source ~/.linuxrc
  - src: macrc
    dst: ~/.macrc
    platform: [darwin]
"""
            )

            mappings = load_mappings(config_directory, home)
            self.assertEqual(mappings[0].destination, home / ".linuxrc")
            self.assertEqual(mappings[0].append.path, home / ".profile")

            with patch(
                "dotfiles.configuration.detect_platform",
                return_value=("linux", "x86_64"),
            ):
                apply_configurations(config_directory, home)
                apply_configurations(config_directory, home)

            self.assertTrue((home / ".linuxrc").is_symlink())
            self.assertFalse((home / ".macrc").exists())
            self.assertEqual(
                (home / ".profile").read_text(),
                "source ~/.linuxrc\n",
            )

    def test_rejects_invalid_config_shape(self):
        with TemporaryDirectory() as directory:
            config_directory = Path(directory)
            (config_directory / "config.yaml").write_text("configs: invalid\n")

            with self.assertRaisesRegex(ValueError, "must be a list"):
                load_mappings(config_directory)

    def test_links_only_executable_scripts(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bin_directory = root / "bin"
            local_bin = root / "local-bin"
            bin_directory.mkdir()
            executable = bin_directory / "example"
            executable.write_text("#!/bin/sh\n")
            executable.chmod(0o755)
            (bin_directory / "notes").write_text("not executable\n")

            link_executable_scripts(bin_directory, local_bin)

            self.assertTrue((local_bin / "example").is_symlink())
            self.assertFalse((local_bin / "notes").exists())


if __name__ == "__main__":
    unittest.main()
