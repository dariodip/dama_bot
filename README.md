# Dama Bot

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dariodip/dama_bot/ci.yml)
![GitHub Release](https://img.shields.io/github/v/release/dariodip/dama_bot)


A personal Telegram assistant for Dario and Manuela, powered by an **agent-first architecture**. Natural-language messages are routed through an OpenAI-backed agent that decides which registered tools to invoke, keeping Telegram as a thin interface layer.

This is a personal project and is not intended for public use. It is a work in progress and is subject to change at any time. I've decided to document the design and implementation decisions in the [docs](docs) directory to share my learning process with the community.

## Features

| Domain | Tools | Persistence |
|---|---|---|
| **Reminders** | `reminder-create`, `reminder-list`, `reminder-delete`, `reminder-update` | SQLite |
| **Free Days** | `free_day-create`, `free_day-is_a_free_day`, `free_day-next` | SQLite |
| **Garbage Schedule** | `garbage-get_garbage_type_for_day`, `garbage-is_indifferenziato_week` | In-memory schedule |
| **Diet** | `diet-get_meals_by_day`, `diet-get_meals_by_day_and_meal_type` | YAML files (`data/diet/`) |

Slash commands `/start`, `/help`, and `/version` are handled directly by Telegram handlers.

## Architecture

```text
Telegram message
  ↓
handlers/message_handler (generic entry point)
  ↓
Agent (OpenAI chat completions loop, max 5 turns)
  ↓
Plugin Loader (discovers & loads enabled plugins)
  ↓
Plugins (e.g. reminders, weather)
  ↓
Tools (e.g. reminder-create)
  ↓
Services
  ↓
Infrastructure (SQLite, Telegram API, YAML, etc.)
```

See [docs/agent-architecture.md](docs/agent-architecture.md) for the full design document.

## Project Structure

```text
src/dama_bot/
├── main.py                  # Entry point
├── bot.py                   # Application factory, post-init hooks
├── config.py                # Environment and settings
├── agent/
│   ├── core.py              # Agent (OpenAI loop)
│   ├── registry.py          # ToolRegistry
│   ├── plugin.py            # Plugin and Tool protocols
│   ├── loader.py            # PluginLoader
│   └── models.py            # UserContext, ToolResult, AgentResponse
├── plugins/                 # Extensible capabilities
│   ├── reminders/
│   ├── free_day/
│   ├── garbage/
│   └── diet/
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

settings.toml                 # Configuration of the bot
scripts/new_plugin.py         # Bootstrap script for new plugins
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

### Enabling Plugins

The `settings.toml` file controls which plugins are enabled. Only enabled plugins will expose their tools to the Agent:

```toml
[plugins]
enabled = [
    "reminders",
    "free_day",
    "garbage",
    "diet"
]
```

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

Capabilities are added by creating a new plugin.

1. **Scaffold the plugin** using the Makefile:
   ```bash
   make plugin-new NAME=weather
   ```
2. **Define the tool contract** — update the generated Pydantic models.
3. **Implement the logic** — preferably in a dedicated service inside `src/dama_bot/services/`.
4. **Wire the plugin** — implement `get_plugin()` in `src/dama_bot/plugins/weather/plugin.py`.
5. **Enable the plugin** — add `"weather"` to the `enabled` list in `settings.toml`.
6. **Write tests** covering the tool, service, and repository layers.

The Agent will automatically discover and use the tools provided by enabled plugins.

## License

Private project.
