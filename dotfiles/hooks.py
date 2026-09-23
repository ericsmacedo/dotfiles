"""Exceptional setup performed after specific tool installations."""

from pathlib import Path

from .commands import run
from .models import InstallContext


def configure_fzf(context: InstallContext) -> None:
    """Enable FZF shell integration after a Homebrew installation."""

    if context.method != "brew":
        return

    install_script = _find_fzf_install_script()
    if install_script:
        run(install_script, "--all", check=False)


def _find_fzf_install_script() -> Path | None:
    """Find the integration script in a standard Homebrew prefix."""

    candidates = (
        Path("/opt/homebrew/opt/fzf/install"),
        Path("/usr/local/opt/fzf/install"),
    )
    return next((path for path in candidates if path.exists()), None)
