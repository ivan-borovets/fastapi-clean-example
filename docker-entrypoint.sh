#!/bin/bash
set -e

PORT=${2:-8000}

case "$1" in
    start)
        alembic upgrade head
        exec uvicorn app.main.run:make_app --factory --host 0.0.0.0 --port "$PORT" --reload
        ;;
    pytest)
        alembic upgrade head
        shift
        exec pytest "$@"
        ;;
    *)
        exec "$@"
        ;;
esac
