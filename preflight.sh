#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
python3 tools/preflight.py
python3 tools/inspect_challenge.py
