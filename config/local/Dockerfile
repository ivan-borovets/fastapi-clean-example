FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --target /app/dependencies .
COPY . ./

FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/dependencies" \
    PATH="/app/dependencies/bin:$PATH"
COPY --from=builder /app/dependencies /app/dependencies
COPY --from=builder /app/ ./
EXPOSE 8888
CMD ["uvicorn", "app.run:make_app", "--host", "0.0.0.0", "--port", "8888", "--loop", "uvloop"]
