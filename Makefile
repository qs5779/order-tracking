# pkgtmpl/Makefile.local.package revision 002

SHELL:=/usr/bin/env bash

# PROJECT_NAME = $(shell head -10 pyproject.toml|grep ^name | awk '{print $$NF}'|tr -d '"' | tr '-' '_')
PROJECT_NAME = orders
PROJECT_VERSION = $(shell head -10 pyproject.toml|grep ^version | awk '{print $$NF}'|tr -d '"')
PACKAGE_DIR = app
WHEEL_VERSION = $(shell echo $(PROJECT_VERSION)|sed -e 's/-dev/.dev/')
BUMP_VERSION = $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF}')
CONST_VERSION = $(shell grep ^VERSION $(PACKAGE_DIR)/constants.py | awk '{print $$NF}'|tr -d '"')
ESCAPED_VERSION := $(subst .,\.,$(PROJECT_VERSION))
HOST = $(shell hostname)
ifneq ($(HOST), yam)
DOCKER_ENV_FILE = docker_env.development
DOCKER_PROJECT = $(PROJECT_NAME)_dev
else
DOCKER_ENV_FILE = docker_env.production
DOCKER_PROJECT = $(PROJECT_NAME)
endif

TEST_MASK ?= tests/*.py

.PHONY: poetry-update
poetry-update:
	poetry update --with test
	pre-commit-update-repo.sh

.PHONY: update
update: poetry-update safety
	pre-commit-update-repo.sh

.PHONY: vars
vars:
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PROJECT_VERSION: $(PROJECT_VERSION)"
	@echo "PACKAGE_DIR: $(PACKAGE_DIR)"
	@echo "WHEEL_VERSION: $(WHEEL_VERSION)"
	@echo "BUMP_VERSION: $(BUMP_VERSION)"
	@echo "CONST_VERSION: $(CONST_VERSION)"
	@echo "ESCAPED_VERSION: $(ESCAPED_VERSION)"
	@echo "DOCKER_ENV_FILE: $(DOCKER_ENV_FILE)"
	@echo "DOCKER_PROJECT: $(DOCKER_PROJECT)"

.PHONY: version-sanity
version-sanity:
ifneq ($(PROJECT_VERSION), $(BUMP_VERSION))
	$(error Version mismatch PROJECT_VERSION != BUMP_VERSION)
endif
ifneq ($(PROJECT_VERSION), $(CONST_VERSION))
	$(error Version mismatch PROJECT_VERSION != CONST_VERSION)
endif
	@echo "Versions are equal $(PROJECT_VERSION), $(BUMP_VERSION), $(CONST_VERSION)"

.PHONY: changelog-check
changelog-check: version-sanity
ifneq (,$(findstring dev,$(PROJECT_VERSION)))
	$(error Cannot pull request when dev version)
else ifeq (,$(shell grep '\[$(ESCAPED_VERSION)\]' CHANGELOG.md))
	$(error No changelog entry for $(PROJECT_VERSION))
else ifneq (,$(shell grep Unreleased CHANGELOG.md))
	$(error Unreleased section in CHANGELOG.md)
else
	@echo "Changelog entry found for $(PROJECT_VERSION)"
endif

.PHONY: run
run:
	scripts/start.sh

.PHONY: start
start:
ifneq ($(DOCKER_ENV_FILE), docker_env.production)
	cp -f tests/data/test.db ./storage
endif
	docker compose --env-file $(DOCKER_ENV_FILE) -p $(DOCKER_PROJECT) -f compose.yaml up --build -d

.PHONY: stop
stop:
	docker compose --env-file $(DOCKER_ENV_FILE) -p $(DOCKER_PROJECT) -f compose.yaml down --remove-orphans --rmi local

.PHONY: black
black:
	poetry run isort $(PACKAGE_DIR) $(TEST_MASK)
	poetry run black $(PACKAGE_DIR) $(TEST_MASK)

.PHONY: mypy
mypy: black
	poetry run mypy $(PACKAGE_DIR) $(TEST_MASK)

.PHONY: lint
lint: mypy
	poetry run flake8 $(PACKAGE_DIR) $(TEST_MASK)

.PHONY: units
units:
	poetry run pytest -s tests

.PHONY: unit
unit:
	poetry run pytest tests

.PHONY: package
package:
	poetry check
	poetry run pip check

.PHONY:  safety
safety:
	safety scan --full-report

.PHONY: nitpick
nitpick:
	nitpick -p . check

.PHONY: test
test: testdb version-sanity nitpick lint package unit clean-test

# TODO: figure out how to unit test via drone
.PHONY: citest
citest: testdb changelog-check lint package unit clean-test

.PHONY: testdb
testdb:
	mkdir -p ./storage
	cp -f tests/data/test.db ./storage

.PHONY: release
release: changelog-check
	@echo "Release $(PROJECT_VERSION) ready to be pushed"
	manage-tag.sh -u v$(PROJECT_VERSION)

.PHONY: clean clean-build clean-pyc clean-test
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr docs/_build
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -f storage/test.db

.DEFAULT:
	@cd docs && $(MAKE) $@

# vim: ft=Makefile
