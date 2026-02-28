# Shell / Make config
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

.SILENT:
MAKEFLAGS += --no-print-directory

# -----------------------------
# User-configurable variables (edit this)
# -----------------------------
PROJECT_NAME ?= $(notdir $(abspath .))
INFRA_SERVICES ?= db_pg

# -----------------------------
# Internal vars / aliases
# -----------------------------
PYTHON_BIN := python
DOCKER_COMPOSE := docker compose -p $(PROJECT_NAME)
DOCKER_COMPOSE_PRUNE := scripts/makefile/docker_prune.sh

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
PYTEST_PATHS_ALL := \
	$(PYTEST_PATHS_LIGHT) \
	tests/smoke \
	tests/integration/with_infra

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
	tmp=$$(mktemp -d); trap 'rm -rf "$$tmp"' EXIT; \
	uv -qq export --format pylock.toml -o "$$tmp/pylock.toml"; \
	pip-audit --locked "$$tmp" \
	|| echo "WARNING: pip-audit found vulnerabilities (non-blocking)" >&2

# Code quality
.PHONY: slotscheck lint test check
slotscheck:
	slotscheck $(SLOTSCHECK_TARGET) 2>&1 | tee /dev/stderr \
	| { grep -m1 "Failed to import" || true; } | cut -d"'" -f2 \
	| xargs -r -n1 $(PYTHON_BIN) -c 'import importlib,sys; importlib.import_module(sys.argv[1])'

lint:
	ruff check --fix
	ruff format
	tombi format
	tombi lint
	deptry
	$(MAKE) slotscheck SLOTSCHECK_TARGET=src
	lint-imports
	mypy

test:
	pytest -v \
		$(PYTEST_PATHS_LIGHT) \
		$(PYTEST_ARGS_COV)

check: lint test
	coverage html

# Docker compose
.PHONY: docker-env local-env upd up upd-local up-local down stop-all
docker-env:
	{ \
	  echo "# This .env file is generated automatically for DOCKER environment by Makefile."; \
	  echo "# Do not edit it directly; edit env.example / .secrets and Makefile instead."; \
	  echo; \
	  cat env.example; \
	  if [ -f .secrets ]; then \
	    echo; \
	    echo "# --- secrets from .secrets (not committed) ---"; \
	    cat .secrets; \
	  fi; \
	} > .env

local-env:
	{ \
	  echo "# This .env file is generated automatically for LOCAL environment by Makefile."; \
	  echo "# Do not edit it directly; edit env.example / .secrets and Makefile instead."; \
	  echo; \
	  sed \
	    -e 's|^EXAMPLE_SERVICE_URL=.*|EXAMPLE_SERVICE_URL=http://127.0.0.1:51999|' \
	    -e 's|^POSTGRES_HOST=.*|POSTGRES_HOST=127.0.0.1|' \
	    env.example; \
	  if [ -f .secrets ]; then \
	    echo; \
	    echo "# --- secrets from .secrets (not committed) ---"; \
	    cat .secrets; \
	  fi; \
	} > .env

upd: docker-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate

up: docker-env
	$(DOCKER_COMPOSE) up --build --force-recreate

upd-local: local-env
	$(DOCKER_COMPOSE) up -d --build --force-recreate $(INFRA_SERVICES)

up-local: local-env
	$(DOCKER_COMPOSE) up --build --force-recreate $(INFRA_SERVICES)

down:
	$(DOCKER_COMPOSE) down

stop-all:
	docker ps -q | xargs -r docker stop

# Tests (with infra)
.PHONY: test-docker
test-docker: docker-env
	rc=0; \
	$(DC_TEST_DOCKER) down -v --remove-orphans >/dev/null 2>&1 || true; \
	if [ -n "$(strip $(INFRA_SERVICES))" ]; then \
	  $(DC_TEST_DOCKER) up -d --build --wait --wait-timeout 180 $(INFRA_SERVICES); \
	else \
	  echo "INFRA_SERVICES is empty, skipping infra startup"; \
	fi; \
	$(DC_TEST_DOCKER) run --build --name $(TEST_RUNNER) app \
		pytest $(PYTEST_ARGS_VERBOSE) \
			$(PYTEST_PATHS_ALL) \
			$(PYTEST_ARGS_COV_DOCKER) \
		|| rc=$$?; \
	docker cp $(TEST_RUNNER):/tmp/.coverage ./.coverage.docker 2>/dev/null || true; \
	docker rm $(TEST_RUNNER) >/dev/null 2>&1 || true; \
	$(DC_TEST_DOCKER) down -v --remove-orphans; \
	coverage html --data-file=.coverage.docker -d htmlcov-docker && \
		echo "Coverage HTML report: htmlcov-docker/index.html" || true; \
	exit $$rc

.PHONY: prune
prune:
	$(DOCKER_COMPOSE_PRUNE)

# Project structure visualization
.PHONY: pycache-del tree plot-data
PYCACHE_DEL := scripts/makefile/pycache_del.sh
DISHKA_PLOT_DATA := scripts/dishka/plot_dependencies_data.py

pycache-del:
	@$(PYCACHE_DEL)

tree: pycache-del
	@tree

plot-data:
	@$(PYTHON_BIN) $(DISHKA_PLOT_DATA)
