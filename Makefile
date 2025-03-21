# Makefile variables, pt. 1
PYTHON := python
CONFIGS_DIG := config
TOML_CONFIG_MANAGER := $(CONFIGS_DIG)/toml_config_manager.py

# Setting environment
.PHONY: env dotenv

env:
	@echo APP_ENV=$(APP_ENV)

dotenv:
	@$(PYTHON) $(TOML_CONFIG_MANAGER) ${APP_ENV}

# Makefile variables, pt. 2
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := docker-compose.yaml
DOCKER_COMPOSE_PRUNE := scripts/makefile/docker_prune.sh

# Docker Compose controls
.PHONY: guard-APP_ENV up.db up.db-echo up up.echo down down.total logs.db shell.db prune

guard-APP_ENV:
ifndef APP_ENV
	$(error "APP_ENV is not set. Set APP_ENV before running this command.")
endif

up.db: guard-APP_ENV
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up -d web_app_db_pg --build

up.db-echo: guard-APP_ENV
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up web_app_db_pg --build

up:
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up -d --build

up.echo:
	@echo "APP_ENV=$(APP_ENV)"
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) up --build

down: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) down

down.total: guard-APP_ENV
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) down -v

logs.db:
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) logs -f web_app_db_pg

shell.db:
	@cd $(CONFIGS_DIG)/$(APP_ENV) && $(DOCKER_COMPOSE) --env-file .env.$(APP_ENV) exec web_app_db_pg sh

prune:
	$(DOCKER_COMPOSE_PRUNE)

# Makefile variables, pt. 3
SRC_DIR := src
TESTS_DIR := tests

# Source code formatting
.PHONY: code.format code.lint code.test code.cov code.cov.html code.check

code.format:
	isort $(CONFIGS_DIG) $(SRC_DIR) $(TESTS_DIR)
	black $(CONFIGS_DIG) $(SRC_DIR) $(TESTS_DIR)

code.lint: code.format
	bandit -r $(CONFIGS_DIG) $(SRC_DIR) -c pyproject.toml
	ruff check $(CONFIGS_DIG) $(SRC_DIR) $(TESTS_DIR)
	pylint $(CONFIGS_DIG) $(SRC_DIR)
	mypy $(CONFIGS_DIG) $(SRC_DIR)

code.test:
	pytest -v

code.cov:
	coverage run -m pytest
	coverage report

code.cov.html:
	coverage run -m pytest
	coverage html

code.check: code.lint code.test

# Makefile variables, pt. 4
PYCACHE_DEL := scripts/makefile/pycache_del.sh
DISHKA_PLOT_DATA := scripts/dishka/plot_dependencies_data.py

# Clean tree
.PHONY: pycache-del tree

pycache-del:
	@$(PYCACHE_DEL)

tree: pycache-del
	@tree

# Dishka
.PHONY: plot-data

plot-data:
	python $(DISHKA_PLOT_DATA)
