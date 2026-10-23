#!/bin/bash
set -e

PORT=${2:-8000}

case "$1" in
  api)
    exec uvicorn app.main.run:make_app --factory --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips '*'
    ;;
  start)
    alembic upgrade head
    exec uvicorn app.main.run:make_app --factory --host 0.0.0.0 --port "$PORT" --reload
    ;;
  *)
    exec "$@"
    ;;
esac
