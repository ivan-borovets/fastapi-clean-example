# Shell config
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

# Make config
.DEFAULT_GOAL := check
.SILENT:
MAKEFLAGS += --no-print-directory

# -----------------------------
# User-configurable variables (edit this)
# INFRA_SERVICES: long-running infra (db, broker, cache, ...)
# INFRA_INIT_SERVICES: one-shot services that prepare INFRA_SERVICES
# MIGRATION_DB_SERVICE: transactional db service used by alembic (empty = no migrations)
# MIGRATION_DB_PORT: host port MIGRATION_DB_SERVICE publishes; change it if the port is taken
# STAIRWAY_TEST: path to stairway test (empty = skip stairway step)
# PYTEST_WORKERS: parallel pytest processes, each one gets its own test database
# -----------------------------
PROJECT_NAME ?= $(notdir $(abspath .))
INFRA_SERVICES ?= db_pg
INFRA_INIT_SERVICES ?=
MIGRATION_DB_SERVICE ?= db_pg
MIGRATION_DB_PORT ?= 15432
STAIRWAY_TEST ?= tests/integration/migrations/test_stairway.py
PYTEST_WORKERS ?= 4

# -----------------------------
# Internal vars / aliases
# -----------------------------
# Script aliases
DI_GRAPH := scripts/dishka/render_di_graph.py
DOCKER_ENV := scripts/makefile/docker_env.sh
DOCKER_PRUNE := scripts/makefile/docker_prune.sh
LOCAL_ENV := scripts/makefile/local_env.sh
MIGRATION := scripts/makefile/migration.sh
PIP_AUDIT := scripts/makefile/pip_audit.sh
PYCACHE_DEL := scripts/makefile/pycache_del.sh
SELF_RETURN := scripts/makefile/self_return.py
SLOTSCHECK := scripts/makefile/slotscheck.sh

# Env files
ENV_FILE := .env
TEST_ENV_FILE := .env.test

# Compose names
TEST_PROJECT := $(PROJECT_NAME)-test
TEST_RUNNER := $(TEST_PROJECT)-runner
MIGRATION_PROJECT := $(PROJECT_NAME)-migration

# Compose commands
DOCKER_COMPOSE := ENV_FILE=$(ENV_FILE) docker compose \
	-p $(PROJECT_NAME) \
	--env-file $(ENV_FILE) \
	-f docker-compose.yml
DOCKER_COMPOSE_TEST := ENV_FILE=$(TEST_ENV_FILE) docker compose \
	-p $(TEST_PROJECT) \
	--env-file $(TEST_ENV_FILE) \
	-f docker-compose.yml \
	-f docker-compose.test.yml

# Pytest paths
PYTEST_PATHS_TOOLING := \
	tests/tooling
PYTEST_PATHS_LIGHT := \
	tests/sanity \
	tests/unit \
	tests/integration/no_infra
PYTEST_PATHS_APP_INFRA := \
	$(PYTEST_PATHS_LIGHT) \
	tests/smoke \
	tests/integration/with_infra
PYTEST_PATHS_MIGRATIONS := \
	tests/integration/migrations

# Pytest args
PYTEST_ARGS_OUTPUT := -v -ra
PYTEST_ARGS_PARALLEL := -n $(PYTEST_WORKERS)
PYTEST_ARGS_COV := \
	--cov=src \
	--cov-report=term-missing \
	--cov-report=html
PYTEST_ARGS_COV_DOCKER := \
	--cov=src \
	--cov-report=term-missing

# Quality
.PHONY: pip-audit slotscheck lint test check check-ci
pip-audit:
	$(PIP_AUDIT)

slotscheck:
	$(SLOTSCHECK) src

lint:
	uv run ruff check --fix --unsafe-fixes
	uv run ruff format
	uv run tombi format
	uv run tombi lint
	uv run deptry
	$(MAKE) slotscheck
	uv run lint-imports
	uv run python $(SELF_RETURN) src tests scripts
	uv run mypy

test:
	uv run pytest $(PYTEST_ARGS_OUTPUT) \
		$(PYTEST_PATHS_TOOLING) \
		$(PYTEST_PATHS_LIGHT) \
		$(PYTEST_ARGS_COV)

check: lint test
	uv run coverage html

check-ci:
	uv run ruff check
	uv run ruff format --check
	uv run tombi format --check
	uv run tombi lint
	uv run deptry
	$(MAKE) slotscheck
	uv run lint-imports
	uv run python $(SELF_RETURN) src tests scripts
	uv run mypy
	$(MAKE) test

# Env generation
.PHONY: local-env docker-env test-env
local-env:
	$(LOCAL_ENV) > $(ENV_FILE)

docker-env:
	$(DOCKER_ENV) > $(ENV_FILE)

test-env:
	$(DOCKER_ENV) > $(TEST_ENV_FILE)

# Docker
.PHONY: upd-local up-local upd up down stop-all prune
upd-local: local-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate $(INFRA_SERVICES) $(INFRA_INIT_SERVICES)

up-local: local-env
	$(DOCKER_COMPOSE) up --build --force-recreate $(INFRA_SERVICES) $(INFRA_INIT_SERVICES)

upd: docker-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate

up: docker-env
	$(DOCKER_COMPOSE) up --build --force-recreate

down:
	$(DOCKER_COMPOSE) down

stop-all:
	docker ps -q | xargs -r docker stop

prune:
	$(DOCKER_PRUNE)

# Migrations
.PHONY: migration
migration: local-env
	POSTGRES_PORT=$(MIGRATION_DB_PORT) \
	ENV_FILE=$(ENV_FILE) \
	MIGRATION_PROJECT=$(MIGRATION_PROJECT) \
	MIGRATION_DB_SERVICE=$(MIGRATION_DB_SERVICE) \
	STAIRWAY_TEST=$(STAIRWAY_TEST) \
	$(MIGRATION) "$(msg)"

# Tests with infra (Docker)
.PHONY: test-docker-app test-docker-migrations test-docker
test-docker-app: test-env
	rc=0; \
	$(DOCKER_COMPOSE_TEST) down -v --remove-orphans >/dev/null 2>&1 || true; \
	if [ -n "$(strip $(INFRA_SERVICES))" ]; then \
	  $(DOCKER_COMPOSE_TEST) up -d --build --wait --wait-timeout 180 $(INFRA_SERVICES); \
	  if [ -n "$(strip $(INFRA_INIT_SERVICES))" ]; then \
	    $(DOCKER_COMPOSE_TEST) up --build --abort-on-container-failure $(INFRA_INIT_SERVICES) >/dev/null; \
	  fi; \
	else \
	  echo "INFRA_SERVICES is empty, skipping infra startup"; \
	fi; \
	$(DOCKER_COMPOSE_TEST) run --build --name $(TEST_RUNNER) app \
		pytest $(PYTEST_ARGS_OUTPUT) $(PYTEST_ARGS_PARALLEL) \
			$(or $(paths),$(PYTEST_PATHS_APP_INFRA)) \
			$(if $(paths),,$(PYTEST_ARGS_COV_DOCKER)) \
		|| rc=$$?; \
	docker cp $(TEST_RUNNER):/tmp/.coverage ./.coverage.docker 2>/dev/null || true; \
	docker rm $(TEST_RUNNER) >/dev/null 2>&1 || true; \
	$(DOCKER_COMPOSE_TEST) down -v --remove-orphans; \
	exit $$rc

test-docker-migrations: test-env
	if [ -z "$(strip $(PYTEST_PATHS_MIGRATIONS))" ] || [ -z "$(strip $(MIGRATION_DB_SERVICE))" ]; then \
	  echo "PYTEST_PATHS_MIGRATIONS or MIGRATION_DB_SERVICE is empty, skipping migrations tests"; \
	  exit 0; \
	fi; \
	rc=0; \
	$(DOCKER_COMPOSE_TEST) down -v --remove-orphans >/dev/null 2>&1 || true; \
	$(DOCKER_COMPOSE_TEST) up -d --build --wait --wait-timeout 180 $(MIGRATION_DB_SERVICE); \
	$(DOCKER_COMPOSE_TEST) run --build --no-deps --entrypoint pytest --name $(TEST_RUNNER) app \
		$(PYTEST_ARGS_OUTPUT) \
		$(PYTEST_PATHS_MIGRATIONS) \
		|| rc=$$?; \
	docker rm $(TEST_RUNNER) >/dev/null 2>&1 || true; \
	$(DOCKER_COMPOSE_TEST) down -v --remove-orphans; \
	exit $$rc

test-docker:
	$(MAKE) test-docker-app paths=''
	$(MAKE) test-docker-migrations
	uv run coverage html --data-file=.coverage.docker -d htmlcov-docker && \
		echo "Coverage HTML report: htmlcov-docker/index.html" || true

# Utils
.PHONY: di-graph pycache-del
di-graph:
	APP_DEBUG_MODE=false APP_LOGGING_LEVEL=CRITICAL uv run python $(DI_GRAPH)

pycache-del:
	$(PYCACHE_DEL)
