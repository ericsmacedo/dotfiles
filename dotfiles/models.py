"""Data models used to describe installable command-line tools."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Platform = tuple[str, str]
ArchiveType = Literal["tar.gz", "binary"]
InstallMethod = Literal["brew", "release", "script"]


@dataclass(frozen=True, slots=True)
class Release:
    """A downloadable release for one operating-system/architecture pair."""

    url: str
    binary_path: str
    archive_type: ArchiveType = "tar.gz"
    destination_name: str | None = None


@dataclass(frozen=True, slots=True)
class InstallScript:
    """A vendor-provided installation script."""

    url: str
    args: tuple[str, ...] = ()
    shell: str = "sh"


@dataclass(frozen=True, slots=True)
class InstallContext:
    """Information passed to an exceptional post-install hook."""

    system: str
    architecture: str
    method: InstallMethod
    local_bin: Path
    executable: Path | None = None


@dataclass(frozen=True, slots=True)
class Tool:
    """Installation options for a command-line tool."""

    command: str
    version: str | None = None
    brew_package: str | None = None
    releases: Mapping[Platform, Release] = field(default_factory=dict)
    install_script: InstallScript | None = None
    post_install: Callable[[InstallContext], None] | None = None
    install_by_default: bool = True
