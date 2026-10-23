#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

echo "# Generated automatically for LOCAL environment by Makefile."
echo "# Do not edit it directly; edit env.example / .secrets and Makefile instead."
echo
sed \
  -e 's|^POSTGRES_HOST=.*|POSTGRES_HOST=127.0.0.1|' \
  env.example
if [ -f .secrets ]; then
  echo
  echo "# --- secrets from .secrets (not committed) ---"
  cat .secrets
fi
