#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

uv run slotscheck "$1" 2>&1 | tee /dev/stderr \
| { grep -m1 "Failed to import" || true; } | cut -d"'" -f2 \
| xargs -r -n1 uv run python -c 'import importlib,sys; importlib.import_module(sys.argv[1])'
