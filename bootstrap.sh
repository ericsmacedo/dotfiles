#!/usr/bin/env bash
# Bootstrap script for dotfiles
# - Ensures `uv` is installed (and adds it to PATH for this session)
# - Uses `uv` to create & activate a local virtual environment
# - Syncs dependencies from project.tmol (or pyproject.toml if present)
# - Optionally runs `inv setup` if available

set -euo pipefail

# -------- helpers --------
has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

add_local_bins_to_path() {
  # Common install locations for uv
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
}

ensure_uv() {
  if has_cmd uv; then
    return
  fi
  echo "uv not found. Installing uv..."
  # Install uv (downloads Python on demand if needed)
  # shellcheck disable=SC2016
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Make it available for this shell session
  add_local_bins_to_path
  if ! has_cmd uv; then
    echo "uv installation completed, but 'uv' not found on PATH."
    echo "Temporarily adding \$HOME/.local/bin to PATH."
    export PATH="$HOME/.local/bin:$PATH"
  fi
  if ! has_cmd uv; then
    echo "❌ Failed to locate 'uv' after installation. Please add it to your PATH and re-run."
    exit 1
  fi
}

# -------- main --------
main() {
  add_local_bins_to_path
  ensure_uv

  # Resolve repo root (directory containing this script)
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
  cd "$REPO_DIR"

  # Create (or reuse) a local venv with uv. You can pin Python by setting UV_PYTHON_VERSION=3.12, etc.
  UV_PY="${UV_PYTHON_VERSION:-}"
  if [[ -n "$UV_PY" ]]; then
    echo "Creating venv with Python $UV_PY (via uv)..."
    uv venv --python "$UV_PY" --clear
  else
    echo "Creating venv with uv (will download Python if needed)..."
    uv venv --clear
  fi

  # Activate the environment for this shell
  if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
  else
    echo "❌ Could not find .venv/bin/activate. Something went wrong creating the environment."
    exit 1
  fi

  echo "Syncing dependencies with uv..."
  uv sync

  #uv run inv setup

  echo "✅ Bootstrap complete."
  echo "This shell is now inside the virtual environment (.venv)."
}

main "$@"
