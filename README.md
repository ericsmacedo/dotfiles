# Dotfiles

Configuration and setup scripts for macOS and Linux.

## Requirements

- `curl`
- `git`
- `tmux` for the full setup
- Homebrew is optional on macOS

## Install

```bash
git clone https://github.com/ericsmacedo/dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap.sh
```

`bootstrap.sh` installs `uv` when needed and runs the full setup.

To run it manually:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv run inv setup
```

## Commands

```bash
uv run inv --list
uv run inv setup
uv run inv install-all-tools
uv run inv install-tool --name ripgrep
uv run inv link-configs
uv run inv test
```

## Files

```text
tasks.py                 Invoke commands
dotfiles/registry.py     Tool list
dotfiles/installer.py    Tool installation
dotfiles/configuration.py Config file linking
dotfiles/neovim.py       Neovim setup
dotfiles/nodejs.py       Node.js setup
dotfiles/tmux.py         TPM and tmux plugin setup
configs/config.yaml      Config file locations
configs/                 Managed config files
bin/                     Local scripts
tests/                   Unit tests
```

## Tools

The setup installs:

- Neovim
- Node.js
- fzf
- fd
- ripgrep
- Ruff
- eza
- Starship

`uv` is installed by the bootstrap script. Node.js, Neovim, and tmux use separate setup code. The other tools are listed in `dotfiles/registry.py`.

Node.js is installed through NVM. The NVM version is pinned, and `nvm install --lts` installs the current Node.js LTS release.

On macOS, Homebrew is used when available. Otherwise, the setup downloads a release file or runs the tool's install script.

## Add a tool

Add a `Tool` entry to `dotfiles/registry.py`:

```python
"example": Tool(
    command="example",
    version="1.2.3",
    brew_package="example",
    releases={
        ("linux", "x86_64"): Release(
            url="https://example.com/example-1.2.3-linux.tar.gz",
            binary_path="example-1.2.3/example",
        ),
    },
),
```

The tool is then included in `install-all-tools`. Set `install_by_default=False` to make it optional.

Test it with:

```bash
uv run inv install-tool --name example
```

## Config files

Config links are defined in `configs/config.yaml`:

```yaml
configs:
  - src: nvim/
    dst: ~/.config/nvim/
    platform: [linux, darwin]
```

Existing files are moved to `~/.dotfiles_backup/` before links are created.

Executable files in `bin/` are linked into `~/.local/bin`.

## Tests

```bash
uv run inv test
```

The `rfv` script also requires `bat`, which is not installed by this project.
