UV ?= uv

.PHONY: help sync services services-down migrate run test lint format check

help:
	@echo "make sync          Install dependencies"
	@echo "make services      Start PostgreSQL"
	@echo "make services-down Stop PostgreSQL"
	@echo "make migrate       Apply database migrations"
	@echo "make run           Start the API"
	@echo "make test          Run tests"
	@echo "make lint          Run lint checks"
	@echo "make format        Format code"
	@echo "make check         Run lint and tests"

sync:
	$(UV) sync

services:
	docker compose up -d postgres

services-down:
	docker compose down

migrate:
	$(UV) run alembic upgrade head

run:
	$(UV) run uvicorn app.main:app --reload

test:
	$(UV) run python -m pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

check: lint test

