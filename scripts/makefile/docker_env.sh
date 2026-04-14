#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

{
  echo "# This .env file is generated automatically for DOCKER environment by Makefile."
  echo "# Do not edit it directly; edit env.example / .secrets and Makefile instead."
  echo
  cat env.example
  if [ -f .secrets ]; then
    echo
    echo "# --- secrets from .secrets (not committed) ---"
    cat .secrets
  fi
} > .env
