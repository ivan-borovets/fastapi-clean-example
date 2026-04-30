#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

if [ "$#" -ne 1 ] || [ -z "$1" ]; then
  echo 'ERROR: msg is required, e.g. make migration msg="add users"' >&2
  exit 2
fi
slug="$1"

MIGRATION_PROJECT="$(basename "$PWD")-migration"
: "${MIGRATION_DB_SERVICE:?must be set in Makefile (transactional db service for alembic)}"

trap 'docker compose -p "$MIGRATION_PROJECT" down -v --remove-orphans >/dev/null' EXIT

docker compose -p "$MIGRATION_PROJECT" up -d --build --wait --wait-timeout 180 "$MIGRATION_DB_SERVICE"
alembic upgrade head
alembic revision --autogenerate -m "$slug"

if [ -n "${STAIRWAY_TEST:-}" ]; then
  ALLOW_DESTRUCTIVE_TEST_CLEANUP=1 pytest -s -vv "$STAIRWAY_TEST"
fi
