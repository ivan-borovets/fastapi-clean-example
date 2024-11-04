# Inspired by https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0

FROM python:3.12-slim AS builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

ARG PYPROJECT_TOML
ARG POETRY_LOCK

COPY ${PYPROJECT_TOML} ${POETRY_LOCK} ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --only main --no-root

FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . .

ARG UVICORN_PORT

EXPOSE ${UVICORN_PORT}

CMD ["scripts/docker-compose/run_server.sh"]
