"""Operating-system and architecture detection."""

import platform

from .models import Platform


def detect_platform() -> Platform:
    """Return the current OS and a normalized CPU architecture."""

    system = platform.system().lower()
    machine = platform.machine().lower()

    architecture = {
        "aarch64": "arm64",
        "arm64": "arm64",
        "amd64": "x86_64",
        "x86_64": "x86_64",
    }.get(machine, machine)

    return system, architecture
