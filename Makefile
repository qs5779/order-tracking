SHELL:=/usr/bin/env bash

PACKAGE_DIR = app
PROJECT_NAME = $(shell head -10 pyproject.toml|grep ^name | awk '{print $$NF}'|tr -d '"' | tr '-' '_')
PROJECT_VERSION = $(shell head -10 pyproject.toml|grep ^version | awk '{print $$NF}'|tr -d '"')
BUMP_VERSION = $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF'})
CONST_VERSION = $(shell grep ^VERSION $(PACKAGE_DIR)/constants.py | awk '{print $$NF}'|tr -d '"')
TEST_DIR = tests
# TEST_MASK = $(TEST_DIR)/*.py $(TEST_DIR)/*/*.py
TEST_MASK = $(TEST_DIR)/**/*.py

.PHONY: vars
vars:
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PROJECT_VERSION: $(PROJECT_VERSION)"
	@echo "BUMP_VERSION: $(BUMP_VERSION)"
	@echo "CONST_VERSION: $(CONST_VERSION)"
	@echo "PACKAGE_DIR: $(PACKAGE_DIR)"

.PHONY: version-sanity
version-sanity:
ifneq ($(PROJECT_VERSION), $(BUMP_VERSION))
	$(error Version mismatch PROJECT_VERSION != BUMP_VERSION)
endif
ifneq ($(PROJECT_VERSION), $(CONST_VERSION))
	$(error Version mismatch PROJECT_VERSION != CONST_VERSION)
endif
	@echo "Versions are equal $(PROJECT_VERSION), $(BUMP_VERSION), $(CONST_VERSION)"

.PHONY: update
update:
#	 poetry update --with test --with docs
#	 poetry export -f requirements.txt --without=test --without=docs -o requirements.txt --without-hashes
#	 poetry export -f requirements.txt --only=test --only=docs -o requirements_dev.txt --without-hashes
	poetry update --with test
	poetry export -f requirements.txt --without=test -o requirements.txt --without-hashes
#	 poetry export -f requirements.txt --only=test -o requirements_dev.txt --without-hashes
	pre-commit autoupdate
	git add --update
	pre-commit run

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
#    poetry run doc8 -q docs

.PHONY: safety
safety:
	# poetry run safety check --full-report
	poetry run safety scan --full-report

.PHONY: package
package:
	poetry check
	poetry run pip check

.PHONY: sunit
sunit:
	poetry run pytest -s $(TEST_DIR)

.PHONY: unit
unit:
	poetry run pytest $(TEST_DIR)

.PHONY: test
test: lint package unit

.PHONY: deploy-cloud
deploy-cloud:
	git push cloud main:main

.PHONY: deploy
deploy:
# pass -f to force tagging dev versions which is best for dokku
	manage-tag.sh -fu v$(PROJECT_VERSION)
	git push dokku main:main

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

.DEFAULT:
	@cd docs && $(MAKE) $@

# vim: ft=Makefile
