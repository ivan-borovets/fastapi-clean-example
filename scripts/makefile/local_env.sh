#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

{
  echo "# This .env file is generated automatically for LOCAL environment by Makefile."
  echo "# Do not edit it directly; edit env.example / .secrets and Makefile instead."
  echo
  sed \
    -e 's|^EXAMPLE_SERVICE_URL=.*|EXAMPLE_SERVICE_URL=http://127.0.0.1:51999|' \
    -e 's|^POSTGRES_HOST=.*|POSTGRES_HOST=127.0.0.1|' \
    env.example
  if [ -f .secrets ]; then
    echo
    echo "# --- secrets from .secrets (not committed) ---"
    cat .secrets
  fi
} > .env
