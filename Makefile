# Makefile for Python project

.DELETE_ON_ERROR:
.PHONY: FORCE
.PRECIOUS:
.SUFFIXES:

SHELL:=/bin/bash -e -o pipefail
SELF:=$(firstword $(MAKEFILE_LIST))

PY_VERSION:=3

.DEFAULT_GOAL := help

############################################################################
#= BASIC USAGE

.PHONY: help
help: ## Display help message
	@./sbin/makefile-extract-documentation $(MAKEFILE_LIST)

############################################################################
#= SETUP, INSTALLATION, PACKAGING

.PHONY: install devready
install: devready
devready: ## Prepare the development environment and install Git hooks
	uv sync --dev --extra server
	uv run prek install -f
	@echo 'Activate the environment with: source .venv/bin/activate'

.PHONY: build publish
build: ## Build the source distribution and wheel
	uv build

publish: build ## Publish distributions to PyPI (requires trusted publishing or UV_PUBLISH_TOKEN)
	uv publish

############################################################################
#= FORMATTING, TESTING, AND CODE QUALITY

.PHONY: cqa test test-network test-coverage test-matrix
cqa: ## Check the lockfile, run hooks, and validate dependencies
	uv lock --locked
	uv run prek run --all-files
	uv run deptry src

test: ## Run pytest and doctests
	uv run pytest

test-network: ## Run integration tests requiring live UTA access
	uv run pytest -m network

test-coverage: ## Run tests and generate coverage reports
	uv run pytest --cov --cov-report=term-missing --cov-report=xml

test-matrix: ## Test all supported Python versions with Nox
	uv run nox

############################################################################
#= DOCUMENTATION

.PHONY: docs-serve docs-test docs-deploy
docs-serve: ## Serve the documentation locally
	uv run mkdocs serve

docs-test: ## Build the documentation and fail on warnings
	uv run mkdocs build --strict

docs-deploy: ## Deploy documentation to GitHub Pages
	uv run mkdocs gh-deploy --force

############################################################################
#= UTILITIES

.PHONY: show-outdated-deps upgrade-deps bump-deps
show-outdated-deps: ## List outdated dependencies
	uv pip list --outdated

upgrade-deps: ## Upgrade dependencies in the lockfile
	uv lock --upgrade

bump-deps: ## Update dependency minimums
	uv run uv-bump

############################################################################
#= CLEANUP

.PHONY: clean cleaner cleanest distclean
clean: ## Remove temporary and backup files
	find . \( -name '*~' -o -name '*.bak' \) -exec rm -frv {} +

cleaner: clean ## Remove rebuildable artifacts
	rm -frv .cache .DS_Store .pytest_cache .ruff_cache build coverage.xml dist docs/_build site
	find . \( -name __pycache__ -type d \) -exec rm -frv {} +
	find . \( -name '*.pyc' -o -name '*.egg-info' -o -name '*.orig' -o -name '*.rej' \) -exec rm -frv {} +

cleanest: cleaner ## Remove virtual environments and tox/nox state
	rm -frv .eggs .nox .venv venv .tox

distclean: cleanest ## Refuse to remove untracked files automatically
	@echo 'Remove untracked files manually; git clean is intentionally disabled.'
