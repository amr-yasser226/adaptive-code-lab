#!/bin/bash
# Linux/macOS wrapper for starting the server
cd "$(dirname "$0")/.."
PYTHON_EXEC="python3"
[ -d ".venv/bin" ] && PYTHON_EXEC="./.venv/bin/python3"
[ -d "venv/bin" ] && PYTHON_EXEC="./venv/bin/python3"
$PYTHON_EXEC scripts/run_prod.py
