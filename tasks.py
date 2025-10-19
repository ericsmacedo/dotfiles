#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

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
    """Symlink config files from ./configs to the correct locations."""
    # Neovim
    nvim_src = CONFIG_DIR / "nvim"
    nvim_dst = HOME / ".config" / "nvim"
    if nvim_src.exists():
        symlink(nvim_src, nvim_dst)

    # tmux
    tmux_src = CONFIG_DIR / "tmux" / "tmux.conf"
    tmux_dst = HOME / ".tmux.conf"
    if tmux_src.exists():
        symlink(tmux_src, tmux_dst)

    # zsh
    zshrc_src = CONFIG_DIR / "zsh" / ".zshrc"
    zshrc_dst = HOME / ".zshrc"
    if zshrc_src.exists():
        symlink(zshrc_src, zshrc_dst)

    # Alacritty (entire directory)
    alacritty_src = CONFIG_DIR / "alacritty"
    alacritty_dst = HOME / ".config" / "alacritty"
    if alacritty_src.exists():
        symlink(alacritty_src, alacritty_dst)

    # Python RC
    pythonrc_src = CONFIG_DIR / "python" / ".pythonrc.py"
    pythonrc_dst = HOME / ".pythonrc.py"
    if pythonrc_src.exists():
        symlink(pythonrc_src, pythonrc_dst)
        shell = os.environ.get("SHELL", "")
        profile = HOME / (".zshrc" if shell.endswith("zsh") else ".bashrc")
        append_unique_line(profile, f'export PYTHONSTARTUP="{pythonrc_dst}"')


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
            tar = f"fd-{FD_VERSION}-aarch64-unknown-linux-gnu.tar.gz"
            d = f"fd-{FD_VERSION}-aarch64-unknown-linux-gnu"
    elif sys == "darwin":
        if arch == "arm64":
            tar = f"fd-{FD_VERSION}-aarch64-apple-darwin.tar.gz"
            d = f"fd-{FD_VERSION}-aarch64-apple-darwin"
        else:
            tar = f"fd-{FD_VERSION}-x86_64-apple-darwin.tar.gz"
            d = f"fd-{FD_VERSION}-x86_64-apple-darwin"
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


# -----------------------------
# Convenience meta tasks
# -----------------------------
@task(
    pre=[
        install_fzf,
        install_fd,
        install_ripgrep,
        install_neovim,
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


@task(pre=[install_all_tools, link_configs])
def setup(c):
    """Full setup: install all tools, link configs, python env."""
    print("✅ Full setup complete. Restart your shell for PATH/profile changes.")
