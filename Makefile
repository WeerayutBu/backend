UV ?= uv

.PHONY: help sync kernel test lint check

help:
	@echo "make sync    Install dependencies"
	@echo "make kernel  Register the Jupyter kernel"
	@echo "make test    Execute every notebook"
	@echo "make lint    Check the notebook runner"
	@echo "make check   Run lint and notebook tests"

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
