#!/bin/bash
# Linux/macOS wrapper for data reset
cd "$(dirname "$0")/.."
PYTHON_EXEC="python3"
[ -d ".venv/bin" ] && PYTHON_EXEC="./.venv/bin/python3"
[ -d "venv/bin" ] && PYTHON_EXEC="./venv/bin/python3"
$PYTHON_EXEC scripts/init_prod.py
