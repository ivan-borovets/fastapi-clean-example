ARG PYTHON_VERSION="3.13"
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim

ARG ENVIRONMENT="prod"
ARG APP_VERSION=develop

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_HTTP_TIMEOUT=300
ENV APP_VERSION=$APP_VERSION

WORKDIR /code

COPY pyproject.toml uv.lock README.md ./

RUN if [ "$ENVIRONMENT" = "prod" ]; then \
      uv sync --frozen --no-cache --no-dev --no-install-project; \
    else \
      uv sync --frozen --no-cache --dev --no-install-project; \
    fi

COPY . .

RUN if [ "$ENVIRONMENT" = "prod" ]; then \
      uv sync --frozen --no-cache --no-dev; \
    else \
      uv sync --frozen --no-cache --dev; \
    fi

RUN groupadd -r runner && \
    useradd -r -g runner -m -s /usr/sbin/nologin runner && \
    chown -R runner:root /code && \
    chmod -R g=u /code

USER runner

EXPOSE 8000

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
