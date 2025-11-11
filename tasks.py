#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

import yaml
from invoke import task

# -----------------------------
# Globals & helpers
# -----------------------------

HOME = Path.home()
LOCAL_BIN = HOME / ".local" / "bin"
BACKUP_ROOT = HOME / ".dotfiles_backup"
REPO_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = REPO_ROOT / "configs"
BIN_DIR = REPO_ROOT / "bin"

TMUX_PLUGINS_DIR = HOME / ".tmux" / "plugins"
TPM_DIR = TMUX_PLUGINS_DIR / "tpm"

FZF_VERSION = "0.66.0"
FD_VERSION = "v10.3.0"
RG_VERSION = "15.0.0"

# Neovim versions/URLs may change frequently; these are safe defaults:
NVIM_LINUX_X64 = "https://github.com/neovim/neovim-releases/releases/download/v0.11.3/nvim-linux-x86_64.appimage"
NVIM_MAC_ARM_TAR = (
    "https://github.com/neovim/neovim/releases/latest/download/nvim-macos-arm64.tar.gz"
)


def run(cmd, check=True, env=None):
    print(f"→ {cmd}")
    subprocess.run(cmd, shell=True, check=check, env=env)


def has_cmd(cmd):
    return shutil.which(cmd) is not None


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def timestamp():
    return time.strftime("%Y%m%d-%H%M%S")


def backup(path: Path):
    if not path.exists() and not path.is_symlink():
        return None
    ensure_dir(BACKUP_ROOT)
    dest = BACKUP_ROOT / f"{path.name}.{timestamp()}"
    print(f"Backup: {path} -> {dest}")
    shutil.move(str(path), str(dest))
    return dest


def symlink(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        if dest.is_symlink() and Path(os.readlink(dest)).resolve() == src.resolve():
            print(f"Symlink already correct: {dest} → {src}")
            return
        backup(dest)
    print(f"Link: {dest} → {src}")
    dest.symlink_to(src)


def append_unique_line(file: Path, line: str):
    file.parent.mkdir(parents=True, exist_ok=True)
    existing = file.read_text() if file.exists() else ""
    if line.strip() not in [x.strip() for x in existing.splitlines()]:
        with file.open("a") as f:
            f.write(line + "\n")
        print(f"Appended to {file}: {line}")
    else:
        print(f"Already present in {file}: {line}")


def curl_download(url: str, dest: Path):
    run(f'curl -L "{url}" -o "{dest}"')


def extract_targz(tar_path: Path, extract_to: Path):
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_to)


def os_arch():
    sys = platform.system().lower()  # 'darwin' or 'linux'
    arch = platform.machine().lower()  # 'x86_64', 'arm64', etc.
    if arch in ("aarch64", "arm64"):
        arch = "arm64"
    elif arch in ("x86_64", "amd64"):
        arch = "x86_64"
    return sys, arch


# -----------------------------
# Housekeeping tasks
# -----------------------------


@task
def ensure_path(c):
    """Ensure ~/.local/bin exists and is on PATH (zsh/bash)."""
    ensure_dir(LOCAL_BIN)
    shell = os.environ.get("SHELL", "")
    profile = HOME / (".zshrc" if shell.endswith("zsh") else ".bashrc")
    line = f'export PATH="{LOCAL_BIN}:$PATH"'
    append_unique_line(profile, line)
    print(f"Ensured {LOCAL_BIN} on PATH in {profile}")


@task
def link_configs(c):
    """
    Symlink config files and append custom lines as described in configs/config.yaml for this platform.
    """
    config_file = CONFIG_DIR / "config.yaml"
    if not config_file.exists():
        print(f"Config file not found: {config_file}")
        return
    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    sys, _ = os_arch()

    for entry in cfg.get("configs", []):
        platforms = [p.lower() for p in entry.get("platform", [])]
        if sys in platforms:
            src = CONFIG_DIR / entry["src"]
            dst = Path(os.path.expanduser(entry["dst"]))
            if src.exists():
                symlink(src, dst)
                # New feature: append line to file if specified
                if "append" in entry:
                    append_info = entry["append"]
                    append_line = append_info.get("line")
                    append_file = append_info.get("file")
                    if append_line and append_file:
                        append_file_path = Path(os.path.expanduser(append_file))
                        append_unique_line(append_file_path, append_line)
            else:
                print(f"Source does not exist: {src}")


@task
def link_bin_scripts(c):
    """Symlink repo's ./bin executables into ~/.local/bin."""
    ensure_dir(LOCAL_BIN)
    if BIN_DIR.exists():
        for p in BIN_DIR.iterdir():
            if p.is_file() and os.access(p, os.X_OK):
                symlink(p, LOCAL_BIN / p.name)


# -----------------------------
# Per-tool install tasks (macOS/Linux)
# Each can be run independently.
# -----------------------------


@task
def install_tpm(c):
    """Install or update TPM (tmux plugin manager) in ~/.tmux/plugins/tpm."""
    TMUX_PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    if TPM_DIR.exists():
        # Update TPM if it's already there
        print(f"TPM already present at {TPM_DIR}, pulling latest...")
        run(f"git -C '{TPM_DIR}' fetch --tags --all")
        run(f"git -C '{TPM_DIR}' pull --ff-only")
    else:
        run(f"git clone https://github.com/tmux-plugins/tpm '{TPM_DIR}'")
    print("✅ TPM installed/updated.")


@task(pre=[install_tpm])
def install_tmux_plugins(c):
    """
    Install tmux plugins declared in ~/.tmux.conf using TPM, non-interactively.
    Creates a temporary tmux session to run TPM's installer, then kills it.
    """
    if not has_cmd("tmux"):
        raise RuntimeError(
            "tmux is not installed. Install tmux then re-run 'inv install-tmux-plugins'."
        )

    if not TPM_DIR.exists():
        raise RuntimeError("TPM directory not found; run 'inv install-tpm' first.")

    # Ensure TMUX_PLUGIN_MANAGER_PATH in env (TPM respects this)
    env = os.environ.copy()
    env["TMUX_PLUGIN_MANAGER_PATH"] = str(TMUX_PLUGINS_DIR)

    # Start a server and a temporary session (safe if server already running)
    # Name is unlikely to collide; kill at the end no matter what.
    session_name = "__tpm_bootstrap"
    run("tmux start-server", check=False)
    run(f"tmux new-session -d -s {session_name} -n __tpm 'sleep 1'", check=False)

    try:
        # TPM provides both scripts/install_plugins.sh and bin/install_plugins.
        # scripts/install_plugins.sh expects to run within a tmux server context.
        tpm_install = TPM_DIR / "scripts" / "install_plugins.sh"
        if not tpm_install.exists():
            # Fall back to bin helper if scripts path changes
            tpm_install = TPM_DIR / "bin" / "install_plugins"
        run(f"'{tpm_install}'", env=env)
        print("✅ tmux plugins installed.")
    finally:
        run(f"tmux kill-session -t {session_name}", check=False)


@task(pre=[ensure_path])
def install_fzf(c):
    """Install fzf (macOS via brew if available; else tarballs)."""
    sys, arch = os_arch()
    if sys == "darwin" and has_cmd("brew"):
        run("brew install fzf")
        fzf_install = (
            "/opt/homebrew/opt/fzf/install"
            if Path("/opt/homebrew/opt/fzf/install").exists()
            else "/usr/local/opt/fzf/install"
        )
        if Path(fzf_install).exists():
            run(f"yes | {fzf_install} || true", check=False)
        return

    ensure_dir(LOCAL_BIN)
    if sys == "darwin":
        arch_token = "arm64" if arch == "arm64" else "amd64"
        tar_name = f"fzf-{FZF_VERSION}-darwin_{arch_token}.tar.gz"
    elif sys == "linux":
        arch_token = "arm64" if arch == "arm64" else "amd64"
        tar_name = f"fzf-{FZF_VERSION}-linux_{arch_token}.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS: {sys}")

    url = f"https://github.com/junegunn/fzf/releases/download/v{FZF_VERSION}/{tar_name}"
    tmp = Path.cwd() / tar_name
    curl_download(url, tmp)
    extract_targz(tmp, LOCAL_BIN)
    tmp.unlink(missing_ok=True)


@task(pre=[ensure_path])
def install_fd(c):
    """Install fd (macOS via brew if available; else tarballs)."""
    sys, arch = os_arch()
    if sys == "darwin" and has_cmd("brew"):
        run("brew install fd")
        return

    if sys == "linux":
        if arch == "x86_64":
            tar = f"fd-{FD_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
            d = f"fd-{FD_VERSION}-x86_64-unknown-linux-gnu"
        else:
            raise RuntimeError(f"Unsupported OS: {sys}")
    elif sys == "darwin":
        if arch == "arm64":
            tar = f"fd-{FD_VERSION}-aarch64-apple-darwin.tar.gz"
            d = f"fd-{FD_VERSION}-aarch64-apple-darwin"
        else:
            raise RuntimeError(f"Unsupported OS: {sys}")
    else:
        raise RuntimeError(f"Unsupported OS: {sys}")

    url = f"https://github.com/sharkdp/fd/releases/download/{FD_VERSION}/{tar}"
    tmp = Path.cwd() / tar
    curl_download(url, tmp)
    extract_targz(tmp, Path.cwd())
    shutil.move(str(Path(d) / "fd"), str(LOCAL_BIN / "fd"))
    shutil.rmtree(d, ignore_errors=True)
    tmp.unlink(missing_ok=True)


@task(pre=[ensure_path])
def install_ripgrep(c):
    """Install ripgrep (macOS via brew if available; else tarballs)."""
    sys, arch = os_arch()
    if sys == "darwin" and has_cmd("brew"):
        run("brew install ripgrep")
        return

    if sys == "linux":
        if arch == "x86_64":
            tar = f"ripgrep-{RG_VERSION}-x86_64-unknown-linux-musl.tar.gz"
            d = f"ripgrep-{RG_VERSION}-x86_64-unknown-linux-musl"
        else:
            raise RuntimeError(f"Unsupported OS: {sys}")
    elif sys == "darwin":
        if arch == "arm64":
            tar = f"ripgrep-{RG_VERSION}-aarch64-apple-darwin.tar.gz"
            d = f"ripgrep-{RG_VERSION}-aarch64-apple-darwin"
        else:
            raise RuntimeError(f"Unsupported OS: {sys}")
    else:
        raise RuntimeError(f"Unsupported OS: {sys}")

    url = f"https://github.com/BurntSushi/ripgrep/releases/download/{RG_VERSION}/{tar}"
    tmp = Path.cwd() / tar
    curl_download(url, tmp)
    extract_targz(tmp, Path.cwd())
    shutil.move(str(Path(d) / "rg"), str(LOCAL_BIN / "rg"))
    shutil.rmtree(d, ignore_errors=True)
    tmp.unlink(missing_ok=True)


@task(pre=[ensure_path])
def install_uv(c):
    """Install uv (Python package manager) via official script."""
    run("curl -LsSf https://astral.sh/uv/install.sh | sh")


@task(pre=[ensure_path])
def install_ruff(c):
    """Install ruff (Python linter/formatter) via official script."""
    run("curl -LsSf https://astral.sh/ruff/install.sh | sh")


@task(pre=[ensure_path])
def install_neovim(c):
    """Install Neovim (brew on macOS if available; else official archives)."""
    sys, arch = os_arch()
    if sys == "darwin" and has_cmd("brew"):
        run("brew install neovim")
        return

    if sys == "linux" and arch == "x86_64":
        dest = LOCAL_BIN / "nvim"
        curl_download(NVIM_LINUX_X64, dest)
        dest.chmod(0o755)
    elif sys == "darwin" and arch == "arm64":
        tmp = Path.cwd() / "nvim-macos-arm64.tar.gz"
        curl_download(NVIM_MAC_ARM_TAR, tmp)
        extract_targz(tmp, Path.cwd())
        nvim_tree = next(
            (p for p in Path.cwd().glob("nvim-macos*") if p.is_dir()), None
        )
        if nvim_tree and (nvim_tree / "bin" / "nvim").exists():
            install_root = HOME / ".local" / "nvim"
            if install_root.exists():
                shutil.rmtree(install_root)
            shutil.move(str(nvim_tree), str(install_root))
            symlink(install_root / "bin" / "nvim", LOCAL_BIN / "nvim")
        tmp.unlink(missing_ok=True)
    else:
        raise RuntimeError(f"Unsupported combo: {sys} {arch}")

    # --- Clean up any previous Neovim state or plugin data ---
    print("🧹 Cleaning up old Neovim state and plugins...")
    run("rm -rf ~/.local/state/nvim", check=False)
    run("rm -rf ~/.local/share/nvim", check=False)


@task(pre=[ensure_path])
def install_starship(c):
    """Install starship (brew on macOS if available; else official script otherwise)."""
    sys, arch = os_arch()
    if sys == "darwin" and has_cmd("brew"):
        run("brew install starship")
        return
    # For Linux and fallback on macOS
    run("curl -sS https://starship.rs/install.sh | sh -s -- --bin-dir ~/.local/bin")
    print("✅ Starship installed.")


@task
def nvim_venv(c):
    """
    Create or update a Python virtual environment inside Neovim's config folder.
    This venv is used by Neovim's Python-based tools (pynvim, ruff, black, etc.).
    """
    nvim_dir = Path.home() / ".config" / "nvim"
    venv_dir = nvim_dir / ".venv"

    if not nvim_dir.exists():
        print("⚠️ Neovim config directory not found. Run 'inv link-configs' first.")
        return

    print(f"📦 Creating Neovim venv at {venv_dir}...")
    # Use uv if available, else fallback to python -m venv
    if shutil.which("uv"):
        run(f"uv venv --clear --project {nvim_dir}")
        run(f"uv sync --frozen --no-progress --directory {nvim_dir}")
    else:
        print("❌ Neither uv nor python3 found; cannot create Neovim venv.")
        return

    print("✅ Neovim venv ready.")
    print(f"To verify: {venv_dir}/bin/python -m pip list")


@task(
    pre=[
        install_fzf,
        install_fd,
        install_ripgrep,
        install_neovim,
        install_ruff,
        install_starship,
        link_bin_scripts,
    ]
)
def install_all_tools(c):
    """Install all CLI tools (runs individual tasks)."""
    print("✅ All tools installed (individual tasks).")


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
