FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --target /app/dependencies .
COPY . ./

FROM python:3.12-slim-bookworm AS final
ARG APP_UID=10001
ARG APP_GID=10001
RUN groupadd -g ${APP_GID} appgroup && \
    useradd -u ${APP_UID} -g ${APP_GID} -s /usr/sbin/nologin -M appuser
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/dependencies" \
    PATH="/app/dependencies/bin:$PATH"
COPY --from=builder --chown=${APP_UID}:${APP_GID} /app/ ./
USER appuser
EXPOSE 8888
CMD ["uvicorn", "app.run:make_app", "--host", "0.0.0.0", "--port", "8888", "--loop", "uvloop"]
