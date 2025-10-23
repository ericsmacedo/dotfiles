#!/usr/bin/env bash
# Bootstrap script for dotfiles
# - Ensures `uv` is installed (and adds it to PATH for this session)
# - runs `uv run inv setup` 

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

  uv run --no-progress inv setup

  echo "✅ Bootstrap complete."
}

main "$@"
