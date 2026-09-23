"""Generic installation workflow for registered command-line tools."""

import shutil
import tarfile
import tempfile
from pathlib import Path

from .commands import run
from .files import ensure_directory
from .models import InstallContext, InstallScript, Release, Tool
from .registry import get_tool
from .system import detect_platform

DEFAULT_LOCAL_BIN = Path.home() / ".local" / "bin"


def install_tool(name: str, local_bin: Path = DEFAULT_LOCAL_BIN) -> None:
    """Install a registered tool for the current platform."""

    tool = get_tool(name)
    system, architecture = detect_platform()

    if system == "darwin" and tool.brew_package and shutil.which("brew"):
        run("brew", "install", tool.brew_package)
        context = InstallContext(
            system=system,
            architecture=architecture,
            method="brew",
            local_bin=local_bin,
            executable=_find_executable(tool.command),
        )
    elif release := tool.releases.get((system, architecture)):
        ensure_directory(local_bin)
        executable = _install_release(tool, release, local_bin)
        context = InstallContext(
            system=system,
            architecture=architecture,
            method="release",
            local_bin=local_bin,
            executable=executable,
        )
    elif tool.install_script:
        _install_script(tool.install_script, tool.command, local_bin)
        context = InstallContext(
            system=system,
            architecture=architecture,
            method="script",
            local_bin=local_bin,
            executable=_find_executable(tool.command),
        )
    else:
        raise RuntimeError(
            f"{name} is not available for {system}/{architecture} without Homebrew"
        )

    if tool.post_install:
        tool.post_install(context)


def _find_executable(command: str) -> Path | None:
    executable = shutil.which(command)
    return Path(executable) if executable else None


def _install_script(
    script: InstallScript,
    command: str,
    local_bin: Path = DEFAULT_LOCAL_BIN,
) -> None:
    """Download and run a vendor-provided installation script."""

    with tempfile.TemporaryDirectory(prefix=f"dotfiles-{command}-") as directory:
        script_path = Path(directory) / "install.sh"
        run("curl", "-LsSf", script.url, "-o", script_path)
        arguments = (argument.format(local_bin=local_bin) for argument in script.args)
        run(script.shell, script_path, *arguments)


def _install_release(tool: Tool, release: Release, local_bin: Path) -> Path:
    """Download a release and place its executable in the local bin directory."""

    with tempfile.TemporaryDirectory(prefix=f"dotfiles-{tool.command}-") as directory:
        work_directory = Path(directory)
        download = work_directory / release.url.rsplit("/", maxsplit=1)[-1]
        run("curl", "-fL", release.url, "-o", download)

        if release.archive_type == "binary":
            binary = download
        else:
            with tarfile.open(download, "r:gz") as archive:
                archive.extractall(work_directory, filter="data")
            binaries = [
                path
                for path in work_directory.glob(release.binary_path)
                if path.is_file()
            ]
            if len(binaries) != 1:
                raise RuntimeError(
                    f"Expected one binary matching {release.binary_path!r}, "
                    f"found {len(binaries)}"
                )
            binary = binaries[0]

        if not binary.is_file():
            raise RuntimeError(f"Release did not contain {release.binary_path!r}")

        destination = local_bin / (release.destination_name or tool.command)
        shutil.move(binary, destination)
        destination.chmod(0o755)

        return destination
