# Shell / Make config
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.SILENT:
MAKEFLAGS += --no-print-directory

# -----------------------------
# User-configurable variables (edit this)
# INFRA_SERVICES: long-running infra (db, broker, cache, ...)
# INFRA_INIT_SERVICES: one-shot services that prepare INFRA_SERVICES
# MIGRATION_DB_SERVICE: transactional db service used by alembic (empty = no migrations)
# STAIRWAY_TEST: path to stairway test (empty = skip stairway step)
# -----------------------------
PROJECT_NAME ?= $(notdir $(abspath .))
INFRA_SERVICES ?= db_pg
INFRA_INIT_SERVICES ?=
MIGRATION_DB_SERVICE ?= db_pg
STAIRWAY_TEST ?= tests/integration/migrations/test_stairway.py

# -----------------------------
# Internal vars / aliases
# -----------------------------
DOCKER_COMPOSE := docker compose -p $(PROJECT_NAME)
PIP_AUDIT := scripts/makefile/pip_audit.sh
SLOTSCHECK := scripts/makefile/slotscheck.sh
DOCKER_ENV := scripts/makefile/docker_env.sh
LOCAL_ENV := scripts/makefile/local_env.sh
DOCKER_PRUNE := scripts/makefile/docker_prune.sh
PYCACHE_DEL := scripts/makefile/pycache_del.sh
MIGRATION := scripts/makefile/migration.sh
DISHKA_PLOT_DATA := scripts/dishka/plot_dependencies_data.py

# Test stack is isolated by project name
TEST_PROJECT ?= $(PROJECT_NAME)-test
DC_TEST_DOCKER := docker compose \
	-p $(TEST_PROJECT) \
	-f docker-compose.yml \
	-f docker-compose.test.yml
TEST_RUNNER := $(TEST_PROJECT)-runner

# Pytest paths
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
PYTEST_ARGS_VERBOSE := -s -vv
PYTEST_ARGS_COV := \
	--cov=src \
	--cov-report=term-missing \
	--cov-report=html
PYTEST_ARGS_COV_DOCKER := \
	--cov=src \
	--cov-report=term-missing

# Safety
.PHONY: pip-audit
pip-audit:
	$(PIP_AUDIT)

# Code quality
.PHONY: slotscheck lint test check check-ci
slotscheck:
	$(SLOTSCHECK) src

lint:
	uv run ruff check --fix
	uv run ruff format
	uv run tombi format
	uv run tombi lint
	uv run deptry
	$(MAKE) slotscheck
	uv run lint-imports
	uv run mypy

test:
	uv run pytest -v \
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
	uv run mypy
	$(MAKE) test
	uv run coverage html

# Docker compose
.PHONY: docker-env local-env upd up upd-local up-local down stop-all
docker-env:
	$(DOCKER_ENV)

local-env:
	$(LOCAL_ENV)

upd: docker-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate

up: docker-env
	$(DOCKER_COMPOSE) up --build --force-recreate

upd-local: local-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate $(INFRA_SERVICES) $(INFRA_INIT_SERVICES)

up-local: local-env
	$(DOCKER_COMPOSE) up --build --force-recreate $(INFRA_SERVICES) $(INFRA_INIT_SERVICES)

down:
	$(DOCKER_COMPOSE) down

stop-all:
	docker ps -q | xargs -r docker stop

.PHONY: prune
prune:
	$(DOCKER_PRUNE)

# Migrations
.PHONY: migration
migration: local-env
	MIGRATION_DB_SERVICE=$(MIGRATION_DB_SERVICE) \
	INFRA_INIT_SERVICES="$(INFRA_INIT_SERVICES)" \
	STAIRWAY_TEST=$(STAIRWAY_TEST) \
	$(MIGRATION) "$(msg)"

# Tests (with infra)
.PHONY: test-docker test-docker-app test-docker-migrations
test-docker-app: docker-env
	rc=0; \
	$(DC_TEST_DOCKER) down -v --remove-orphans >/dev/null 2>&1 || true; \
	if [ -n "$(strip $(INFRA_SERVICES))" ]; then \
	  $(DC_TEST_DOCKER) up -d --build --wait --wait-timeout 180 $(INFRA_SERVICES); \
	  if [ -n "$(strip $(INFRA_INIT_SERVICES))" ]; then \
	    $(DC_TEST_DOCKER) up --build $(INFRA_INIT_SERVICES) >/dev/null; \
	  fi; \
	else \
	  echo "INFRA_SERVICES is empty, skipping infra startup"; \
	fi; \
	$(DC_TEST_DOCKER) run --build --name $(TEST_RUNNER) app \
		pytest $(PYTEST_ARGS_VERBOSE) \
			$(PYTEST_PATHS_APP_INFRA) \
			$(PYTEST_ARGS_COV_DOCKER) \
		|| rc=$$?; \
	docker cp $(TEST_RUNNER):/tmp/.coverage ./.coverage.docker 2>/dev/null || true; \
	docker rm $(TEST_RUNNER) >/dev/null 2>&1 || true; \
	$(DC_TEST_DOCKER) down -v --remove-orphans; \
	exit $$rc

test-docker-migrations: docker-env
	if [ -z "$(strip $(PYTEST_PATHS_MIGRATIONS))" ] || [ -z "$(strip $(MIGRATION_DB_SERVICE))" ]; then \
	  echo "PYTEST_PATHS_MIGRATIONS or MIGRATION_DB_SERVICE is empty, skipping migrations tests"; \
	  exit 0; \
	fi; \
	rc=0; \
	$(DC_TEST_DOCKER) down -v --remove-orphans >/dev/null 2>&1 || true; \
	$(DC_TEST_DOCKER) up -d --build --wait --wait-timeout 180 $(MIGRATION_DB_SERVICE); \
	$(DC_TEST_DOCKER) run --build --no-deps --name $(TEST_RUNNER) app \
		pytest $(PYTEST_ARGS_VERBOSE) \
			$(PYTEST_PATHS_MIGRATIONS) \
		|| rc=$$?; \
	docker rm $(TEST_RUNNER) >/dev/null 2>&1 || true; \
	$(DC_TEST_DOCKER) down -v --remove-orphans; \
	exit $$rc

test-docker:
	$(MAKE) test-docker-app
	$(MAKE) test-docker-migrations
	uv run coverage html --data-file=.coverage.docker -d htmlcov-docker && \
		echo "Coverage HTML report: htmlcov-docker/index.html" || true

# Project structure visualization
.PHONY: pycache-del tree plot-data
pycache-del:
	$(PYCACHE_DEL)

tree: pycache-del
	tree

plot-data:
	APP_LOGGING_LEVEL=CRITICAL uv run python $(DISHKA_PLOT_DATA)
