# Makefile variables
SRC_DIR := $(shell grep 'SRC_DIR' config.toml | sed 's/.*= *//')/
PYPROJECT_TOML := $(shell grep 'PYPROJECT_TOML' config.toml | sed 's/.*= *//')
DOCKER_COMPOSE := $(shell grep 'COMPOSE_COMMAND' config.toml | sed 's/.*= *//;s/"//g')
DOCKER_COMPOSE_FILE := $(shell grep 'COMPOSE_FILE' config.toml | sed 's/.*= *//')
# Scripts
DOTENV_FROM_TOML := scripts/makefile/dotenv_from_toml.py
TOML_PG_HOST := scripts/makefile/toml_pg_host.py
DOCKER_COMPOSE_LOGS := scripts/makefile/docker_logs.sh
DOCKER_COMPOSE_SHELL := scripts/makefile/docker_shell.sh
DOCKER_COMPOSE_PRUNE := scripts/makefile/docker_prune.sh
DOCKER_COMPOSE_RMVOLUMES := scripts/makefile/docker_rmvolumes.sh
PYCACHE_DEL := scripts/makefile/pycache_del.sh
DISHKA_PLOT_DATA := scripts/dishka/plot_dependencies_data.py

# Source code formatting, linting and testing
.PHONY: code.format \
		code.lint \
		code.test \
		code.cov \
		code.check

code.format:
	isort $(SRC_DIR)
	black $(SRC_DIR)

code.lint: code.format
	bandit -r $(SRC_DIR) -c $(PYPROJECT_TOML)
	ruff check $(SRC_DIR)
	pylint $(SRC_DIR)
	mypy $(SRC_DIR)

code.test:
	pytest -v

code.cov:
	coverage run -m pytest
	coverage report

code.cov.html:
	coverage run -m pytest
	coverage html

code.check: code.lint code.test

# Dotenv generation
.PHONY: dotenv \
		dotenv-docker \
		dotenv-local

dotenv:
	python $(DOTENV_FROM_TOML)

dotenv-local:
	python $(TOML_PG_HOST) local
	python $(DOTENV_FROM_TOML)

dotenv-docker:
	python $(TOML_PG_HOST) docker
	python $(DOTENV_FROM_TOML)

# Docker Compose controls
.PHONY: up \
		up-echo \
		up-local-db \
		down \
        logs \
        shell \
        prune \
        ps \
        rmvolumes


up-local-db:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d web_app_db_pg --build

up-local-db-auto: dotenv-local
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d web_app_db_pg --build
	sleep 0.5
	alembic upgrade head

up:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d --build

up-echo:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up --build

up-auto: dotenv-docker
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d --build

up-echo-auto: dotenv-docker
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up --build


down:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

down-total:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v


logs:
	@$(DOCKER_COMPOSE_LOGS) "$(DOCKER_COMPOSE)" $(DOCKER_COMPOSE_FILE)

shell:
	@$(DOCKER_COMPOSE_SHELL)

prune:
	@$(DOCKER_COMPOSE_PRUNE)

ps:
	@docker ps

rmvolumes:
	@$(DOCKER_COMPOSE_RMVOLUMES)

# Clean tree
.PHONY: pycache-del \
 		tree

pycache-del:
	@$(PYCACHE_DEL)

tree: pycache-del
	@tree

# Dishka
.PHONY: plot-data

plot-data:
	python $(DISHKA_PLOT_DATA)

# Dev hacks
.PHONY: reset-db-migrate
# Assuming there are no migration files (delete them)
reset-db_migrate:
	@docker compose down -v
	@make up-local-db
	@sleep 1
	@alembic revision --autogenerate -m "Makefile"
	@alembic upgrade head
