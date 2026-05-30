#!/bin/bash
# Start the monitor in watch mode (for terminal use or systemd)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
exec python3 src/main.py --watch
