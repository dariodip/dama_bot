.PHONY: help run \
	test lint format check clean

PYTHON := uv run python


help:
	@echo "Dama Bot development commands"
	@echo ""
	@echo "Development:"
	@echo "  make run              Start the Telegram bot"
	@echo "  make plugin-new NAME=name  Create a new plugin scaffold"
	@echo "  make compile-locales  Compile .po translation catalogs to .mo"
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
	@echo "  make compile-locales  Compile translation catalogs (.po -> .mo)"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy           Deploy the project"

run:
	$(PYTHON) dama-bot

plugin-new:
	@if [ -z "$(NAME)" ]; then echo "Error: NAME is required. Usage: make plugin-new NAME=<plugin_name>"; exit 1; fi
	$(PYTHON) scripts/new_plugin.py $(NAME)

compile-locales:
	$(PYTHON) scripts/compile_locales.py

test:
	uv run pytest

lint:
	ruff check .

format:
	ruff check . --fix
	ruff format .

check: format
	ruff check .

complexity:
	uv run complexipy .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ifeq ($(firstword $(MAKECMDGOALS)),deploy)
  # Extract everything from the 2nd word onward as arguments
  DEPLOY_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn those arguments into do-nothing targets so Make ignores them
  $(eval $(DEPLOY_ARGS):;@:)
endif

deploy:
	./scripts/deploy.sh $(DEPLOY_ARGS)
