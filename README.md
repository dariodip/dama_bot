# Dama Bot

A personal Telegram assistant for Dario and Manuela, powered by an **agent-first architecture**. Natural-language messages are routed through an OpenAI-backed agent that decides which registered tools to invoke, keeping Telegram as a thin interface layer.

## Features

| Domain | Tools | Persistence |
|---|---|---|
| **Reminders** | `reminder-create`, `reminder-list`, `reminder-delete`, `reminder-update` | SQLite |
| **Free Days** | `free_day-create`, `free_day-is_a_free_day`, `free_day-next` | SQLite |
| **Garbage Schedule** | `garbage-get_garbage_type_for_day`, `garbage-is_indifferenziato_week` | In-memory schedule |
| **Diet** | `diet-get_meals_by_day`, `diet-get_meals_by_day_and_meal_type` | YAML files (`data/diet/`) |

Slash commands `/start`, `/help`, and `/version` are handled directly by Telegram handlers.

## Architecture

```
Telegram message
  → handlers/message_handler (generic entry point)
  → Agent (OpenAI chat completions loop, max 5 turns)
  → ToolRegistry → Tool function
  → Domain Service
  → Repository / Infrastructure (SQLite, YAML, in-memory)
```

See [docs/agent-architecture.md](docs/agent-architecture.md) for the full design document.

## Project Structure

```
src/dama_bot/
├── main.py                  # Entry point
├── bot.py                   # Application factory, post-init hooks
├── config.py                # Environment and settings
├── agent/
│   ├── core.py              # Agent (OpenAI loop)
│   ├── registry.py          # ToolRegistry + Tool
│   ├── models.py            # UserContext, ToolResult, AgentResponse
│   └── tools/
│       ├── reminder.py      # Reminder CRUD tools
│       ├── free_day.py      # Free day tools
│       ├── garbage.py       # Garbage schedule tools
│       └── diet.py          # Diet plan tools
├── handlers/
│   ├── __init__.py          # Handler registration
│   ├── message_handler.py   # Generic text → Agent bridge
│   ├── start.py             # /start command
│   ├── help.py              # /help command
│   ├── version.py           # /version command
│   └── reminders/
│       └── scheduler.py     # Telegram JobQueue scheduling
├── services/
│   ├── reminder.py          # Reminder business logic
│   ├── free_day.py          # Free day business logic
│   ├── garbage.py           # Garbage schedule logic
│   └── diet.py              # Diet plan logic
└── database/
    ├── __init__.py           # Schema auto-creation
    ├── connection.py         # SQLAlchemy engine/session
    ├── models.py             # ORM models + domain enums
    └── repository.py         # Data access layer

tests/                        # Mirrors src/ structure
data/diet/                    # Per-user YAML diet plans
scripts/deploy.sh             # rsync + systemd deploy to Raspberry Pi
```

## Requirements

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** for dependency management and running commands

## Setup

```bash
# Install dependencies
uv sync

# Create .env.dev (or .env for production)
cp .env.dev.example .env.dev
# Fill in TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, etc.
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot API token |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-5-nano` | OpenAI model identifier |
| `SQLITE_URL` | `sqlite:///data/dama_bot.sqlite3` | SQLAlchemy database URL |
| `APP_ENV` | `dev` | `dev` loads `.env.dev`, `prod` loads `.env` |

## Running

```bash
# Development
uv run dama-bot

# Or via Makefile
make run
```

## Development

```bash
# Run tests
make test              # or: uv run pytest

# Lint
make lint              # or: uv run ruff check .

# Auto-format
make format            # or: uv run ruff check . --fix && uv run ruff format .

# Format + lint
make check
```

## Deployment

Deploys to a Raspberry Pi via rsync + systemd:

```bash
make deploy <user> <host>
```

This syncs the project, installs dependencies with `uv sync`, and restarts the `dama-bot` systemd service.

## Adding a New Capability

1. **Define the tool contract** — create argument/result Pydantic models
2. **Create the service** in `services/` (business logic, no LLM awareness)
3. **Create the repository** in `database/` if persistence is needed
4. **Register the tool** in `agent/tools/` using `@registry.register(...)`
5. **Wire it up** in `handlers/message_handler.py`
6. **Write tests** covering the tool, service, and repository layers

The agent will automatically discover and use the new tool based on its description.

## License

Private project.
