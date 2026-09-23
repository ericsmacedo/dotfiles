import shutil
import tarfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import dotfiles.installer as installer
from dotfiles.models import InstallScript, Release, Tool
from dotfiles.registry import default_tool_names, get_tool


class RegistryTests(unittest.TestCase):
    def test_default_tools_exclude_bootstrap_dependency(self):
        names = default_tool_names()

        self.assertIn("fzf", names)
        self.assertIn("ruff", names)
        self.assertNotIn("uv", names)

    def test_unknown_tool_lists_available_names(self):
        with self.assertRaisesRegex(ValueError, "Available tools"):
            get_tool("missing")


class InstallerTests(unittest.TestCase):
    def test_prefers_homebrew_on_macos_and_calls_hook(self):
        hook = Mock()
        tool = Tool(
            command="example",
            brew_package="example",
            post_install=hook,
        )

        with TemporaryDirectory() as directory:
            with (
                patch("dotfiles.installer.get_tool", return_value=tool),
                patch(
                    "dotfiles.installer.detect_platform",
                    return_value=("darwin", "arm64"),
                ),
                patch(
                    "dotfiles.installer.shutil.which",
                    side_effect=["/opt/homebrew/bin/brew", "/bin/example"],
                ),
                patch("dotfiles.installer.run") as run,
            ):
                installer.install_tool("example", Path(directory))

        run.assert_called_once_with("brew", "install", "example")
        context = hook.call_args.args[0]
        self.assertEqual(context.method, "brew")
        self.assertEqual(context.executable, Path("/bin/example"))

    def test_extracts_release_and_marks_it_executable(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "example-package"
            package.mkdir()
            (package / "example").write_text("binary")
            archive_path = root / "example.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.add(package, arcname=package.name)

            release = Release(
                url="https://example.test/example.tar.gz",
                binary_path="example-package/example",
            )
            tool = Tool(command="example")
            local_bin = root / "bin"
            local_bin.mkdir()

            def copy_download(*args, **kwargs):
                shutil.copy2(archive_path, Path(args[-1]))

            with patch("dotfiles.installer.run", side_effect=copy_download):
                destination = installer._install_release(tool, release, local_bin)

            self.assertEqual(destination.read_text(), "binary")
            self.assertTrue(destination.stat().st_mode & 0o111)

    def test_vendor_script_is_downloaded_then_executed(self):
        script = InstallScript(
            url="https://example.test/install.sh",
            args=("--yes", "--bin-dir", "{local_bin}"),
        )
        local_bin = Path("/custom/bin")

        with patch("dotfiles.installer.run") as run:
            installer._install_script(script, "example", local_bin)

        self.assertEqual(run.call_count, 2)
        download, execute = run.call_args_list
        self.assertEqual(download.args[:3], ("curl", "-LsSf", script.url))
        self.assertEqual(execute.args[0], "sh")
        self.assertEqual(execute.args[-3:], ("--yes", "--bin-dir", str(local_bin)))


if __name__ == "__main__":
    unittest.main()
