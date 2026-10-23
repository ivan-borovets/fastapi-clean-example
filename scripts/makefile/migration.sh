#!/bin/bash
# The script is called from Makefile
set -eu -o pipefail

if [ "$#" -ne 1 ] || [ -z "$1" ]; then
  echo 'ERROR: msg is required, e.g. make migration msg="add users"' >&2
  exit 2
fi
slug="$1"

: "${ENV_FILE:?must be set in Makefile (env file for compose interpolation)}"
: "${MIGRATION_PROJECT:?must be set in Makefile (compose project for the migration db)}"
: "${MIGRATION_DB_SERVICE:?must be set in Makefile (transactional db service for alembic)}"

compose=(
  docker compose
  -p "$MIGRATION_PROJECT"
  --env-file "$ENV_FILE"
  -f docker-compose.yml
  -f docker-compose.migration.yml
)

trap '"${compose[@]}" down -v --remove-orphans >/dev/null' EXIT
"${compose[@]}" up -d --build --wait --wait-timeout 180 "$MIGRATION_DB_SERVICE"

uv run alembic upgrade head
uv run alembic revision --autogenerate -m "$slug"

if [ -n "${STAIRWAY_TEST:-}" ]; then
  ALLOW_DESTRUCTIVE_TEST_CLEANUP=1 uv run pytest -v -ra "$STAIRWAY_TEST"
fi
