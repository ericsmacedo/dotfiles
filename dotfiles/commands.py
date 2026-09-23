"""Helpers for running external commands."""

import shlex
import subprocess
from collections.abc import Mapping
from os import PathLike

CommandArgument = str | PathLike[str]


def run(
    *args: CommandArgument,
    check: bool = True,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command directly, without interpreting it through a shell."""

    command = [str(arg) for arg in args]
    print(f"→ {shlex.join(command)}")
    return subprocess.run(command, check=check, env=env, text=True)
