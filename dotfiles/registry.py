"""Definitions for tools managed by this repository."""

from .hooks import configure_fzf
from .models import InstallScript, Release, Tool

RIPGREP_VERSION = "15.0.0"
FD_VERSION = "v10.3.0"
FZF_VERSION = "0.66.0"

TOOLS: dict[str, Tool] = {
    "eza": Tool(
        command="eza",
        brew_package="eza",
        releases={
            ("linux", "x86_64"): Release(
                url=(
                    "https://github.com/eza-community/eza/releases/latest/download/"
                    "eza_x86_64-unknown-linux-gnu.tar.gz"
                ),
                binary_path="**/eza",
            ),
            ("linux", "arm64"): Release(
                url=(
                    "https://github.com/eza-community/eza/releases/latest/download/"
                    "eza_aarch64-unknown-linux-gnu.tar.gz"
                ),
                binary_path="**/eza",
            ),
        },
    ),
    "fd": Tool(
        command="fd",
        version=FD_VERSION,
        brew_package="fd",
        releases={
            ("linux", "x86_64"): Release(
                url=(
                    "https://github.com/sharkdp/fd/releases/download/"
                    f"{FD_VERSION}/fd-{FD_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
                ),
                binary_path=f"fd-{FD_VERSION}-x86_64-unknown-linux-gnu/fd",
            ),
            ("darwin", "arm64"): Release(
                url=(
                    "https://github.com/sharkdp/fd/releases/download/"
                    f"{FD_VERSION}/fd-{FD_VERSION}-aarch64-apple-darwin.tar.gz"
                ),
                binary_path=f"fd-{FD_VERSION}-aarch64-apple-darwin/fd",
            ),
        },
    ),
    "fzf": Tool(
        command="fzf",
        version=FZF_VERSION,
        brew_package="fzf",
        releases={
            ("darwin", "arm64"): Release(
                url=(
                    "https://github.com/junegunn/fzf/releases/download/"
                    f"v{FZF_VERSION}/fzf-{FZF_VERSION}-darwin_arm64.tar.gz"
                ),
                binary_path="fzf",
            ),
            ("darwin", "x86_64"): Release(
                url=(
                    "https://github.com/junegunn/fzf/releases/download/"
                    f"v{FZF_VERSION}/fzf-{FZF_VERSION}-darwin_amd64.tar.gz"
                ),
                binary_path="fzf",
            ),
            ("linux", "arm64"): Release(
                url=(
                    "https://github.com/junegunn/fzf/releases/download/"
                    f"v{FZF_VERSION}/fzf-{FZF_VERSION}-linux_arm64.tar.gz"
                ),
                binary_path="fzf",
            ),
            ("linux", "x86_64"): Release(
                url=(
                    "https://github.com/junegunn/fzf/releases/download/"
                    f"v{FZF_VERSION}/fzf-{FZF_VERSION}-linux_amd64.tar.gz"
                ),
                binary_path="fzf",
            ),
        },
        post_install=configure_fzf,
    ),
    "ripgrep": Tool(
        command="rg",
        version=RIPGREP_VERSION,
        brew_package="ripgrep",
        releases={
            ("linux", "x86_64"): Release(
                url=(
                    "https://github.com/BurntSushi/ripgrep/releases/download/"
                    f"{RIPGREP_VERSION}/"
                    f"ripgrep-{RIPGREP_VERSION}-x86_64-unknown-linux-musl.tar.gz"
                ),
                binary_path=(f"ripgrep-{RIPGREP_VERSION}-x86_64-unknown-linux-musl/rg"),
            ),
            ("darwin", "arm64"): Release(
                url=(
                    "https://github.com/BurntSushi/ripgrep/releases/download/"
                    f"{RIPGREP_VERSION}/"
                    f"ripgrep-{RIPGREP_VERSION}-aarch64-apple-darwin.tar.gz"
                ),
                binary_path=(f"ripgrep-{RIPGREP_VERSION}-aarch64-apple-darwin/rg"),
            ),
        },
    ),
    "ruff": Tool(
        command="ruff",
        install_script=InstallScript(url="https://astral.sh/ruff/install.sh"),
    ),
    "starship": Tool(
        command="starship",
        brew_package="starship",
        install_script=InstallScript(
            url="https://starship.rs/install.sh",
            args=("-y", "--bin-dir", "{local_bin}"),
        ),
    ),
    "uv": Tool(
        command="uv",
        install_script=InstallScript(url="https://astral.sh/uv/install.sh"),
        install_by_default=False,
    ),
}


def get_tool(name: str) -> Tool:
    """Return a registered tool or raise an error listing valid names."""

    try:
        return TOOLS[name]
    except KeyError as error:
        available = ", ".join(sorted(TOOLS))
        raise ValueError(
            f"Unknown tool {name!r}. Available tools: {available}"
        ) from error


def default_tool_names() -> tuple[str, ...]:
    """Return registered tools included in the full setup."""

    return tuple(name for name, tool in TOOLS.items() if tool.install_by_default)
