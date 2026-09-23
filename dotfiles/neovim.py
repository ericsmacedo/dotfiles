"""Specialized Neovim installation workflow."""

import shutil
import tarfile
import tempfile
from pathlib import Path

from .commands import run
from .files import create_symlink, ensure_directory
from .system import detect_platform

LINUX_X86_64_URL = (
    "https://github.com/neovim/neovim-releases/releases/download/"
    "v0.11.3/nvim-linux-x86_64.appimage"
)
MACOS_ARM64_URL = (
    "https://github.com/neovim/neovim/releases/latest/download/nvim-macos-arm64.tar.gz"
)


def install_neovim(
    home: Path = Path.home(),
    local_bin: Path | None = None,
) -> None:
    """Install Neovim using the appropriate platform-specific layout."""

    local_bin = local_bin or home / ".local" / "bin"
    ensure_directory(local_bin)
    system, architecture = detect_platform()

    if system == "darwin" and shutil.which("brew"):
        run("brew", "install", "neovim")
        return

    if system == "linux" and architecture == "x86_64":
        _install_linux_appimage(local_bin)
    elif system == "darwin" and architecture == "arm64":
        _install_macos_tree(home, local_bin)
    else:
        raise RuntimeError(f"Unsupported Neovim platform: {system}/{architecture}")

    _remove_previous_state(home)


def setup_python_environment(home: Path = Path.home()) -> None:
    """Create or update the Python environment used by Neovim tooling."""

    nvim_directory = home / ".config" / "nvim"
    environment = nvim_directory / ".venv"

    if not nvim_directory.exists():
        print("⚠️ Neovim config directory not found. Run 'inv link-configs' first.")
        return
    if not shutil.which("uv"):
        print("❌ uv is not installed; cannot create the Neovim environment.")
        return

    print(f"📦 Creating Neovim venv at {environment}...")
    run("uv", "venv", "--clear", "--project", nvim_directory)
    run("uv", "sync", "--frozen", "--no-progress", "--directory", nvim_directory)
    print("✅ Neovim venv ready.")
    print(f"To verify: {environment}/bin/python -m pip list")


def _install_linux_appimage(local_bin: Path) -> None:
    with tempfile.NamedTemporaryFile(
        prefix=".nvim-",
        dir=local_bin,
        delete=False,
    ) as temporary_file:
        download = Path(temporary_file.name)

    try:
        run("curl", "-fL", LINUX_X86_64_URL, "-o", download)
        download.chmod(0o755)
        download.replace(local_bin / "nvim")
    finally:
        download.unlink(missing_ok=True)


def _install_macos_tree(home: Path, local_bin: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="dotfiles-neovim-") as directory:
        work_directory = Path(directory)
        download = work_directory / "nvim-macos-arm64.tar.gz"
        run("curl", "-L", MACOS_ARM64_URL, "-o", download)

        with tarfile.open(download, "r:gz") as archive:
            archive.extractall(work_directory, filter="data")

        nvim_tree = next(
            (path for path in work_directory.glob("nvim-macos*") if path.is_dir()),
            None,
        )
        if nvim_tree is None or not (nvim_tree / "bin" / "nvim").is_file():
            raise RuntimeError("Neovim archive did not contain the expected executable")

        executable = nvim_tree / "bin" / "nvim"
        executable.chmod(executable.stat().st_mode | 0o111)

        install_root = home / ".local" / "nvim"
        if install_root.exists():
            shutil.rmtree(install_root)
        shutil.move(nvim_tree, install_root)
        create_symlink(install_root / "bin" / "nvim", local_bin / "nvim")


def _remove_previous_state(home: Path) -> None:
    print("🧹 Cleaning up old Neovim state and plugins...")
    shutil.rmtree(home / ".local" / "state" / "nvim", ignore_errors=True)
    shutil.rmtree(home / ".local" / "share" / "nvim", ignore_errors=True)
