# Dotfiles Setup

This repository contains my personal development environment configuration — a unified setup for macOS and Linux that installs my favorite CLI tools and symlinks configuration files automatically.

---

## Folder Structure

```
dotfiles/
├─ README.md                # You are here!
├─ pyproject.toml
├─ tasks.py                 # Invoke tasks for setup and configuration
├─ bootstrap.sh             # One-liner setup script for fresh systems
├─ bin/                     # Custom scripts (added to ~/.local/bin)
│  └─ rfv
├─ configs/                 # Configuration files for tools
│  ├─ nvim/                 # Neovim config (init.lua, plugins, etc.)
│  ├─ tmux/
│  │  └─ tmux.conf
│  ├─ zsh/
│  │  └─ zshrc
│  ├─ alacritty/
│  │  └─ alacritty.toml     # or your custom project.tmol
│  └─ python/
│     └─ pythonrc.py
└─ scripts/
   └─ post_install.sh       # Optional: custom post-setup actions
```

---

##  Features

- **Cross-platform support** – Works on both macOS and Linux.
- **Automatic installs** – Fetches CLI tools like:
  - [Neovim](https://neovim.io/)
  - [fzf](https://github.com/junegunn/fzf)
  - [fd](https://github.com/sharkdp/fd)
  - [ripgrep](https://github.com/BurntSushi/ripgrep)
  - [uv](https://github.com/astral-sh/uv)
  - [ruff](https://github.com/astral-sh/ruff)
- **Safe and idempotent** – Existing configs are backed up before changes.
- **Config linking** – Automatically symlinks your configuration files to their correct system paths.
- **Custom scripts** – Any executable inside `bin/` is added to your `~/.local/bin` for easy use.
- **Python environment** – Creates a virtual environment via `uv` and installs dependencies.

---

## ⚙️ Installation

### Prerequisites
- **curl** available
- On macOS: [Homebrew](https://brew.sh/) is recommended (but not required)

---

### Quick Install (Recommended)

```bash
git clone https://github.com/<your-username>/dotfiles.git ~/dotfiles
cd ~/dotfiles
chmod +x bootstrap.sh
source bootstrap.sh
```

This script will:
1. Create a local Python virtual environment.
2. Install the required Python dependencies (`invoke`).
3. Run the full setup (tools + configs + Python environment).

---

### Manual Installation (Alternative)

If you prefer to run things manually:

install uv:
```bash
# 1.Install UV 
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create and activate the environment
uv venv
source .venv/bin/activate
uv sync

# 2. Run setup using Invoke
inv setup
```

You can also run individual tasks:

```bash
inv tools       # Installs CLI tools (fzf, fd, rg, nvim, etc.)
inv configs     # Symlinks configuration files
inv python-env  # Creates Python venv
```

---

## How It Works

### 1. Configuration Management

All configuration files are stored in the `configs/` folder and symlinked into the correct paths.  
Example mappings:
| Tool | Source | Destination |
|------|---------|-------------|
| Neovim | `configs/nvim/` | `~/.config/nvim/` |
| Tmux | `configs/tmux/tmux.conf` | `~/.tmux.conf` |
| Zsh | `configs/zsh/zshrc` | `~/.zshrc` |
| Alacritty | `configs/alacritty/` | `~/.config/alacritty/` |
| Python RC | `configs/python/.pythonrc.py` | `~/.pythonrc.py` |
| ECA | `configs/eca/config.json` | `~/.config/eca/config.json` |

If a file already exists, it will be safely backed up to `~/.dotfiles_backup/` before being replaced.

---

### 2. CLI Tool Installation

The installer:
- Detects your OS (macOS or Linux) and CPU architecture (x86_64 or ARM).
- Uses **Homebrew** on macOS when available.
- Otherwise, downloads binaries from official GitHub releases.
- Adds `~/.local/bin` to your PATH automatically.

Installed tools include:
- **fzf** (fuzzy finder)
- **fd** (fast file finder)
- **ripgrep** (fast text search)
- **neovim**
- **uv** (Python package manager)
- **ruff** (Python linter/formatter)

---

### 3. Python Environment Setup

- Creates a virtual environment using `uv venv`.
- Installs any dependencies from the uv lock file.
- Ensures your `.pythonrc.py` is loaded via `PYTHONSTARTUP`.

---

## 🧠 Useful Commands

```bash
inv --list          # Show all available tasks
inv tools           # Install all tools
inv configs         # Create config symlinks
inv setup           # Full install (recommended)
```

---

## Backups

All existing config files are automatically backed up to:

```
~/.dotfiles_backup/
```

Each backup includes a timestamp (e.g. `.zshrc.20251019-142045`).

---

## Customization

- Add any scripts you want available globally into `bin/`.
- Add more configuration folders under `configs/`.
- Extend `tasks.py` with more Invoke tasks (e.g. for Docker, Brew packages, etc.).
- Add post-setup commands in `scripts/post_install.sh`.

---

## 🧹 Uninstall / Cleanup

To revert all symlinks and restore backups:

```bash
# Simply move backed up files back manually from ~/.dotfiles_backup
mv ~/.dotfiles_backup/.zshrc.* ~/.zshrc
```

Or remove all symlinks:

```bash
find ~ -type l -lname '*dotfiles/configs*' -delete
```

---

## Credits

- [Neovim](https://neovim.io/)
- [fzf](https://github.com/junegunn/fzf)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [fd](https://github.com/sharkdp/fd)
- [astral-sh/uv](https://astral.sh)
- [astral-sh/ruff](https://astral.sh)
- [pyinvoke/invoke](https://www.pyinvoke.org/)

---

## License

MIT License — feel free to use or fork this repo to bootstrap your own environment.
