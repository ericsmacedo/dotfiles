import shutil
import tarfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from dotfiles.neovim import install_neovim, setup_python_environment
from dotfiles.nodejs import NVM_INSTALL_URL, NVM_VERSION, install_nodejs
from dotfiles.tmux import BOOTSTRAP_SESSION, install_tmux_plugins, install_tpm


class NeovimTests(unittest.TestCase):
    def test_installs_linux_appimage_and_removes_previous_state(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            local_bin = home / ".local" / "bin"
            state = home / ".local" / "state" / "nvim"
            plugins = home / ".local" / "share" / "nvim"
            state.mkdir(parents=True)
            plugins.mkdir(parents=True)

            def create_appimage(*args, **kwargs):
                Path(args[-1]).write_text("appimage")

            with (
                patch(
                    "dotfiles.neovim.detect_platform",
                    return_value=("linux", "x86_64"),
                ),
                patch("dotfiles.neovim.run", side_effect=create_appimage),
            ):
                install_neovim(home, local_bin)

            executable = local_bin / "nvim"
            self.assertEqual(executable.read_text(), "appimage")
            self.assertTrue(executable.stat().st_mode & 0o111)
            self.assertFalse(state.exists())
            self.assertFalse(plugins.exists())

    def test_installs_complete_macos_tree(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            local_bin = home / ".local" / "bin"
            source = root / "nvim-macos-arm64" / "bin"
            source.mkdir(parents=True)
            (source / "nvim").write_text("mac binary")
            archive_path = root / "nvim.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.add(root / "nvim-macos-arm64", arcname="nvim-macos-arm64")

            def copy_archive(*args, **kwargs):
                shutil.copy2(archive_path, Path(args[-1]))

            with (
                patch(
                    "dotfiles.neovim.detect_platform",
                    return_value=("darwin", "arm64"),
                ),
                patch("dotfiles.neovim.shutil.which", return_value=None),
                patch("dotfiles.neovim.run", side_effect=copy_archive),
            ):
                install_neovim(home, local_bin)

            executable = local_bin / "nvim"
            self.assertTrue(executable.is_symlink())
            self.assertEqual(executable.resolve().read_text(), "mac binary")
            self.assertTrue(executable.resolve().stat().st_mode & 0o111)

    def test_configures_python_environment_with_uv(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            nvim_directory = home / ".config" / "nvim"
            nvim_directory.mkdir(parents=True)

            with (
                patch("dotfiles.neovim.shutil.which", return_value="/bin/uv"),
                patch("dotfiles.neovim.run") as run,
            ):
                setup_python_environment(home)

            self.assertEqual(run.call_count, 2)
            self.assertEqual(
                run.call_args_list[0],
                call("uv", "venv", "--clear", "--project", nvim_directory),
            )


class TmuxTests(unittest.TestCase):
    def test_clones_tpm_when_missing(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            tpm_directory = home / ".tmux" / "plugins" / "tpm"

            with patch("dotfiles.tmux.run") as run:
                install_tpm(home)

            run.assert_called_once_with(
                "git",
                "clone",
                "https://github.com/tmux-plugins/tpm",
                tpm_directory,
            )

    def test_runs_tpm_installer_and_closes_bootstrap_session(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            installer = (
                home / ".tmux" / "plugins" / "tpm" / "scripts" / "install_plugins.sh"
            )
            installer.parent.mkdir(parents=True)
            installer.touch()

            with (
                patch("dotfiles.tmux.shutil.which", return_value="/bin/tmux"),
                patch("dotfiles.tmux.run") as run,
            ):
                install_tmux_plugins(home)

            self.assertEqual(
                run.call_args_list[-1],
                call("tmux", "kill-session", "-t", BOOTSTRAP_SESSION, check=False),
            )
            environment = run.call_args_list[-2].kwargs["env"]
            self.assertEqual(
                environment["TMUX_PLUGIN_MANAGER_PATH"],
                str(home / ".tmux" / "plugins"),
            )


class NodejsTests(unittest.TestCase):
    def test_installs_nvm_then_nodejs_lts(self):
        with TemporaryDirectory() as directory:
            home = Path(directory) / "home"

            with patch("dotfiles.nodejs.run") as run:
                install_nodejs(home)

            self.assertEqual(run.call_count, 3)
            download, install_nvm, install_node = run.call_args_list
            self.assertEqual(download.args[:3], ("curl", "-fsSL", NVM_INSTALL_URL))
            self.assertEqual(install_nvm.args[0], "bash")
            self.assertEqual(install_node.args[:2], ("bash", "-c"))
            self.assertIn("nvm install --lts", install_node.args[2])
            self.assertEqual(install_node.kwargs["env"]["HOME"], str(home))
            self.assertEqual(
                install_node.kwargs["env"]["NVM_DIR"],
                str(home / ".nvm"),
            )
            self.assertEqual(NVM_VERSION, "v0.39.7")


if __name__ == "__main__":
    unittest.main()
