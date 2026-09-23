"""Specialized TPM and tmux plugin installation workflows."""

import os
import shutil
from pathlib import Path

from .commands import run

TPM_REPOSITORY = "https://github.com/tmux-plugins/tpm"
BOOTSTRAP_SESSION = "__tpm_bootstrap"


def install_tpm(home: Path = Path.home()) -> None:
    """Install TPM or update an existing checkout."""

    plugins_directory = home / ".tmux" / "plugins"
    tpm_directory = plugins_directory / "tpm"
    plugins_directory.mkdir(parents=True, exist_ok=True)

    if tpm_directory.exists():
        print(f"TPM already present at {tpm_directory}, pulling latest...")
        run("git", "-C", tpm_directory, "fetch", "--tags", "--all")
        run("git", "-C", tpm_directory, "pull", "--ff-only")
    else:
        run("git", "clone", TPM_REPOSITORY, tpm_directory)

    print("✅ TPM installed/updated.")


def install_tmux_plugins(home: Path = Path.home()) -> None:
    """Install the plugins declared in the user's tmux configuration."""

    if not shutil.which("tmux"):
        raise RuntimeError(
            "tmux is not installed. Install tmux then re-run "
            "'inv install-tmux-plugins'."
        )

    plugins_directory = home / ".tmux" / "plugins"
    tpm_directory = plugins_directory / "tpm"
    if not tpm_directory.exists():
        raise RuntimeError("TPM directory not found; run 'inv install-tpm' first.")

    environment = os.environ.copy()
    environment["TMUX_PLUGIN_MANAGER_PATH"] = str(plugins_directory)

    run("tmux", "start-server", check=False)
    run(
        "tmux",
        "new-session",
        "-d",
        "-s",
        BOOTSTRAP_SESSION,
        "-n",
        "__tpm",
        "sleep 1",
        check=False,
    )

    try:
        installer = tpm_directory / "scripts" / "install_plugins.sh"
        if not installer.exists():
            installer = tpm_directory / "bin" / "install_plugins"
        if not installer.exists():
            raise RuntimeError("TPM plugin installer was not found")

        run(installer, env=environment)
        print("✅ tmux plugins installed.")
    finally:
        run("tmux", "kill-session", "-t", BOOTSTRAP_SESSION, check=False)
