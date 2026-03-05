SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Dependencies

.PHONY: install
install: ## Install prod dependencies
	uv sync --locked

.PHONY: install-dev
install-dev: ## Install prod+dev dependencies
	uv sync --locked --dev

.PHONY: upgrade
upgrade: ## Upgrade all dependencies
	uv sync --upgrade

### Application

PHONY: run-dev
run-dev: ## Run the app in dev mode
	uv run flask --app src run --debug

### Database

.PHONY: new-migrate
new-migrate: ## Auto-generate a new migration.
	uv run alembic -c src/db/migrations/alembic.ini revision --autogenerate -m $(NAME)

.PHONY: migrate
migrate: ## Run the migrations (will update the database).
	uv run alembic -c src/db/migrations/alembic.ini upgrade head

### Format and checks

.PHONY: ruff
ruff: ## Format code with ruff
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: ruff-check
ruff-check:	## Check that the code is linted using ruff
	uv run ruff check src tests cli migrations
	uv run ruff format --check src src tests cli migrations

.PHONY: ty
ty: ## Run ty static type check
	uv run ty check src tests cli migrations

.PHONY: bandit
bandit:	## Run a static security analysis of the code using bandit
	uv run bandit -c pyproject.toml -r src

.PHONY: alembic-check
alembic-check: ## Run the alembic check
	uv run alembic -c src/db/migrations/alembic.ini check

.PHONY: checks
checks: ## Run all checks
	@$(MAKE) ty ruff-check bandit

PHONY: format
format: ## Format code
	@$(MAKE) ruff

### Misc

.PHONY: clean
clean: ## Clean folder, delete temp folders
	rm -rf .venv
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.ty_cache ' -delete
	find . -type d -name '.pytest_cache ' -delete
	find . -type d -name '.ruff_cache' -delete
	rm -f coverage coverage.xml
	rm -rf .report

### Help

.PHONY: help
help: ## Show help message
	@echo "Usage:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
