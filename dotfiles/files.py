"""Filesystem operations used while configuring dotfiles."""

import shutil
import time
from pathlib import Path

DEFAULT_BACKUP_ROOT = Path.home() / ".dotfiles_backup"


def ensure_directory(path: Path) -> None:
    """Create a directory and any missing parents."""

    path.mkdir(parents=True, exist_ok=True)


def backup(
    path: Path,
    backup_root: Path = DEFAULT_BACKUP_ROOT,
) -> Path | None:
    """Move an existing path into the timestamped backup directory."""

    if not path.exists() and not path.is_symlink():
        return None

    ensure_directory(backup_root)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    destination = backup_root / f"{path.name}.{timestamp}"
    print(f"Backup: {path} -> {destination}")
    shutil.move(path, destination)
    return destination


def create_symlink(
    source: Path,
    destination: Path,
    backup_root: Path = DEFAULT_BACKUP_ROOT,
) -> None:
    """Create a symlink, backing up a conflicting destination first."""

    ensure_directory(destination.parent)
    if destination.is_symlink() or destination.exists():
        if destination.is_symlink() and destination.resolve() == source.resolve():
            print(f"Symlink already correct: {destination} → {source}")
            return
        backup(destination, backup_root)

    print(f"Link: {destination} → {source}")
    destination.symlink_to(source)


def append_unique_line(path: Path, line: str) -> None:
    """Append a line only when an equivalent stripped line is not present."""

    ensure_directory(path.parent)
    existing = path.read_text() if path.exists() else ""
    if line.strip() in (
        existing_line.strip() for existing_line in existing.splitlines()
    ):
        print(f"Already present in {path}: {line}")
        return

    with path.open("a") as file:
        file.write(line + "\n")
    print(f"Appended to {path}: {line}")
