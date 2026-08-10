.PHONY: help run \
	test lint format check clean

PYTHON := uv run python


help:
	@echo "Dama Bot development commands"
	@echo ""
	@echo "Development:"
	@echo "  make run              Start Django development server"
	@echo ""
	@echo "Quality:"
	@echo "  make lint             Run Ruff"
	@echo "  make format           Format code with Ruff"
	@echo "  make check            Format + lint"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run tests"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove Python cache"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy           Deploy the project"

run:
	$(PYTHON) dama-bot


test:
	uv run pytest

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .

check: format
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

deploy:
	./scripts/deploy.sh
