#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from invoke import task

from dotfiles.commands import run
from dotfiles.configuration import apply_configurations, link_executable_scripts
from dotfiles.files import append_unique_line, ensure_directory
from dotfiles.installer import install_tool as install_registered_tool
from dotfiles.neovim import install_neovim as install_neovim_for_current_platform
from dotfiles.neovim import setup_python_environment
from dotfiles.nodejs import install_nodejs as install_nodejs_for_current_platform
from dotfiles.registry import default_tool_names
from dotfiles.tmux import install_tmux_plugins as install_configured_tmux_plugins
from dotfiles.tmux import install_tpm as install_tpm_manager

# -----------------------------
# Globals & helpers
# -----------------------------

HOME = Path.home()
LOCAL_BIN = HOME / ".local" / "bin"
REPO_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = REPO_ROOT / "configs"
BIN_DIR = REPO_ROOT / "bin"

# -----------------------------
# Housekeeping tasks
# -----------------------------


@task
def ensure_path(c):
    """Ensure ~/.local/bin exists and is on PATH (zsh/bash)."""
    ensure_directory(LOCAL_BIN)
    shell = os.environ.get("SHELL", "")
    profile = HOME / (".zshrc" if shell.endswith("zsh") else ".bashrc")
    line = f'export PATH="{LOCAL_BIN}:$PATH"'
    append_unique_line(profile, line)
    print(f"Ensured {LOCAL_BIN} on PATH in {profile}")


@task
def link_configs(c):
    """Link configurations declared for the current platform."""
    apply_configurations(CONFIG_DIR, HOME)


@task
def link_bin_scripts(c):
    """Symlink repo's ./bin executables into ~/.local/bin."""
    link_executable_scripts(BIN_DIR, LOCAL_BIN)


# -----------------------------
# Per-tool install tasks (macOS/Linux)
# Each can be run independently.
# -----------------------------


@task
def install_tpm(c):
    """Install or update TPM (tmux plugin manager) in ~/.tmux/plugins/tpm."""
    install_tpm_manager(HOME)


@task(pre=[install_tpm])
def install_tmux_plugins(c):
    """Install tmux plugins declared in ~/.tmux.conf."""
    install_configured_tmux_plugins(HOME)


@task(pre=[ensure_path])
def install_fzf(c):
    """Install fzf (macOS via brew if available; else tarballs)."""
    install_registered_tool("fzf", LOCAL_BIN)


@task(pre=[ensure_path])
def install_fd(c):
    """Install fd (macOS via brew if available; else tarballs)."""
    install_registered_tool("fd", LOCAL_BIN)


@task(pre=[ensure_path])
def install_ripgrep(c):
    """Install ripgrep (macOS via brew if available; else tarballs)."""
    install_registered_tool("ripgrep", LOCAL_BIN)


@task(pre=[ensure_path], help={"name": "Registered tool name"})
def install_tool(c, name):
    """Install one tool from the registry."""
    install_registered_tool(name, LOCAL_BIN)


@task(pre=[ensure_path])
def install_uv(c):
    """Install uv (Python package manager) via official script."""
    install_registered_tool("uv", LOCAL_BIN)


@task(pre=[ensure_path])
def install_ruff(c):
    """Install ruff (Python linter/formatter) via official script."""
    install_registered_tool("ruff", LOCAL_BIN)


@task(pre=[ensure_path])
def install_neovim(c):
    """Install Neovim (brew on macOS if available; else official archives)."""
    install_neovim_for_current_platform(HOME, LOCAL_BIN)


@task(pre=[ensure_path])
def install_nodejs(c):
    """Install NVM and the current Node.js LTS release."""
    install_nodejs_for_current_platform(HOME)


@task(pre=[ensure_path])
def install_eza(c):
    """Install eza (brew on macOS if available; else GitHub release on Linux)."""
    install_registered_tool("eza", LOCAL_BIN)


@task(pre=[ensure_path])
def install_starship(c):
    """Install starship (brew on macOS if available; else official script otherwise)."""
    install_registered_tool("starship", LOCAL_BIN)


@task
def nvim_venv(c):
    """Create or update Neovim's Python environment."""
    setup_python_environment(HOME)


@task(pre=[ensure_path])
def install_all_tools(c):
    """Install every default registry tool and specialized tool."""
    for name in default_tool_names():
        install_registered_tool(name, LOCAL_BIN)
    install_nodejs_for_current_platform(HOME)
    install_neovim_for_current_platform(HOME, LOCAL_BIN)
    link_executable_scripts(BIN_DIR, LOCAL_BIN)
    print("✅ All tools installed.")


@task(name="test")
def run_tests(c):
    """Run the local unit test suite."""
    run(
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-v",
        "-s",
        REPO_ROOT / "tests",
        "-t",
        REPO_ROOT,
    )


@task(pre=[ensure_path, link_configs])
def configure_only(c):
    """Only link configs."""
    print("✅ Configuration complete.")


@task(
    pre=[
        install_all_tools,
        link_configs,
        install_tmux_plugins,
        nvim_venv,
    ]
)
def setup(c):
    """Full setup: install all tools, link configs, python env."""
    print("✅ Full setup complete. Restart your shell for PATH/profile changes.")
