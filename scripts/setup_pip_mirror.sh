#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CONFIG_DIR="${PIP_CONFIG_DIR:-$HOME/.config/pip}"
mkdir -p "$CONFIG_DIR"
cp "$REPO_ROOT/pip.conf.example" "$CONFIG_DIR/pip.conf"
cat <<MSG
Copied $REPO_ROOT/pip.conf.example to $CONFIG_DIR/pip.conf
Please edit the file to point to a mirror or proxy that your environment can reach.
MSG
