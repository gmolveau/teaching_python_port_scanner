set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := true

default:
    @just --list

### Dependencies

# Install prod dependencies
install:
    uv sync --locked

# Install prod+dev dependencies
install-dev:
    uv sync --locked --dev

# Upgrade all dependencies
upgrade:
    uv sync --upgrade

### Application

# Run the app in dev mode
run-dev:
    [ -f .env ] || cp .env.example .env
    uv run flask --app src run --debug

### Database

# Auto-generate a new migration
new-migrate name:
    uv run alembic -c alembic.ini revision --autogenerate -m {{ name }}

# Run the migrations (will update the database)
migrate:
    uv run alembic -c alembic.ini upgrade head

### Format and checks

# Format code with ruff
ruff:
    uv run ruff check . --fix
    uv run ruff format .

# Check that the code is linted using ruff
ruff-check:
    uv run ruff check src tests cli migrations
    uv run ruff format --check src tests cli migrations

# Run ty static type check
ty:
    uv run ty check src tests cli migrations

# Run a static security analysis of the code using bandit
bandit:
    uv run bandit -c pyproject.toml -r src

# Run the alembic check
alembic-check:
    uv run alembic -c alembic.ini check

# Run all checks
checks: ty ruff-check bandit

# Format code
format: ruff

### Telemetry

run-jaeger:
    docker run --rm -p 16686:16686 -p 4318:4318 -e COLLECTOR_OTLP_ENABLED=true jaegertracing/all-in-one:1.76.0

### Misc

# Clean folder, delete temp folders
clean:
    rm -rf .venv
    find . -type f -name '*.pyc' -delete
    find . -type d -name '__pycache__' -delete
    find . -type d -name '.ty_cache ' -delete
    find . -type d -name '.pytest_cache ' -delete
    find . -type d -name '.ruff_cache' -delete
    rm -f coverage coverage.xml
    rm -rf .report
