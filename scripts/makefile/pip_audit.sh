#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
uv -qq export --format pylock.toml -o "$tmp/pylock.toml"
pip-audit --locked "$tmp" \
|| echo "WARNING: pip-audit found vulnerabilities (non-blocking)" >&2
