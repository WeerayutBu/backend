UV ?= uv

.PHONY: help sync services services-down run worker test lint format check

help:
	@echo "make sync          Install dependencies"
	@echo "make services      Start Redis"
	@echo "make services-down Stop Redis"
	@echo "make run           Start the API"
	@echo "make worker        Start the background worker"
	@echo "make test          Run tests"
	@echo "make lint          Run lint checks"
	@echo "make format        Format code"
	@echo "make check         Run lint and tests"

sync:
	$(UV) sync

services:
	docker compose up -d redis

services-down:
	docker compose down

run:
	$(UV) run uvicorn app.main:app --reload

worker:
	$(UV) run arq app.worker.WorkerSettings

test:
	$(UV) run python -m pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

check: lint test

