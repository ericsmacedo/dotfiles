"""Loading and applying the repository's configuration mappings."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from .files import append_unique_line, create_symlink, ensure_directory
from .system import detect_platform


@dataclass(frozen=True, slots=True)
class AppendLine:
    """A line that should be present in a configuration file."""

    path: Path
    line: str


@dataclass(frozen=True, slots=True)
class ConfigMapping:
    """A repository configuration and its destination."""

    source: Path
    destination: Path
    platforms: tuple[str, ...]
    append: AppendLine | None = None


def load_mappings(
    config_directory: Path, home: Path = Path.home()
) -> list[ConfigMapping]:
    """Load and validate mappings from ``config.yaml``."""

    config_file = config_directory / "config.yaml"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    data = yaml.safe_load(config_file.read_text()) or {}
    entries = data.get("configs", [])
    if not isinstance(entries, list):
        raise ValueError("The 'configs' value must be a list")

    return [
        _parse_mapping(entry, index, config_directory, home)
        for index, entry in enumerate(entries, start=1)
    ]


def apply_configurations(
    config_directory: Path,
    home: Path = Path.home(),
) -> None:
    """Link every configuration declared for the current platform."""

    system, _ = detect_platform()
    try:
        mappings = load_mappings(config_directory, home)
    except FileNotFoundError as error:
        print(error)
        return

    for mapping in mappings:
        if system not in mapping.platforms:
            continue
        if not mapping.source.exists():
            print(f"Source does not exist: {mapping.source}")
            continue

        create_symlink(mapping.source, mapping.destination)
        if mapping.append:
            append_unique_line(mapping.append.path, mapping.append.line)


def link_executable_scripts(bin_directory: Path, local_bin: Path) -> None:
    """Link executable repository scripts into the user's local bin directory."""

    ensure_directory(local_bin)
    if not bin_directory.exists():
        return

    for script in sorted(bin_directory.iterdir()):
        if script.is_file() and os.access(script, os.X_OK):
            create_symlink(script, local_bin / script.name)


def _parse_mapping(
    entry: object,
    index: int,
    config_directory: Path,
    home: Path,
) -> ConfigMapping:
    if not isinstance(entry, dict):
        raise ValueError(f"Config entry {index} must be a mapping")

    try:
        source = config_directory / str(entry["src"])
        destination = _expand_home(str(entry["dst"]), home)
    except KeyError as error:
        raise ValueError(
            f"Config entry {index} is missing {error.args[0]!r}"
        ) from error

    raw_platforms = entry.get("platform", [])
    if not isinstance(raw_platforms, list):
        raise ValueError(f"Config entry {index} platform must be a list")
    platforms = tuple(str(platform).lower() for platform in raw_platforms)

    append = None
    if append_data := entry.get("append"):
        if not isinstance(append_data, dict):
            raise ValueError(f"Config entry {index} append must be a mapping")
        try:
            append = AppendLine(
                path=_expand_home(str(append_data["file"]), home),
                line=str(append_data["line"]),
            )
        except KeyError as error:
            raise ValueError(
                f"Config entry {index} append is missing {error.args[0]!r}"
            ) from error

    return ConfigMapping(
        source=source,
        destination=destination,
        platforms=platforms,
        append=append,
    )


def _expand_home(value: str, home: Path) -> Path:
    if value == "~":
        return home
    if value.startswith("~/"):
        return home / value[2:]
    return Path(value)
