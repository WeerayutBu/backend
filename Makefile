UV ?= uv
BROKER_COMPOSE := docker compose -f 05-cache-jobs/compose.yml

.PHONY: help sync kernel test lint check brokers-up brokers-recreate brokers-down brokers-reset brokers-status

help:
	@echo "make sync    Install dependencies"
	@echo "make kernel  Register the Jupyter kernel"
	@echo "make test    Execute every notebook"
	@echo "make lint    Check the notebook runner"
	@echo "make check   Run lint and notebook tests"
	@echo "make brokers-up        Start the learning brokers"
	@echo "make brokers-recreate  Recreate brokers but keep messages"
	@echo "make brokers-down      Stop brokers but keep messages"
	@echo "make brokers-reset     Stop brokers and delete saved messages"
	@echo "make brokers-status    Show broker status"

sync:
	$(UV) sync

kernel:
	$(UV) run python -m ipykernel install --user \
		--name backend-learning \
		--display-name "Python (backend-learning)"

test:
	$(UV) run python scripts/run_notebooks.py

lint:
	$(UV) run ruff check scripts

check: lint test

brokers-up:
	$(BROKER_COMPOSE) up -d

brokers-recreate:
	$(BROKER_COMPOSE) down
	$(BROKER_COMPOSE) up -d

brokers-down:
	$(BROKER_COMPOSE) down

brokers-reset:
	$(BROKER_COMPOSE) down --volumes

brokers-status:
	$(BROKER_COMPOSE) ps
