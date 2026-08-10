# Dama Bot — Agent Instructions

## Mission

You are working on `dama_bot`, a personal Telegram assistant for two users (Dario and Manuela).

The project uses an **agent-first architecture**:
Telegram message → Agent → Tool → Domain service → Persistence/infrastructure.

The agent must only perform operations exposed through registered tools. It must explicitly tell the user when a requested operation is not supported.

## Read first

Before changing code, inspect:

- `pyproject.toml`
- `src/dama_bot/`
- `docs/agent-architecture.md`
- existing tests

Do not assume the current architecture matches the target architecture. Preserve working behavior while refactoring incrementally.

## Core architectural rules

1. Telegram is an interface, not the business-logic layer.
2. Do not create a new Telegram handler for every capability.
3. Keep one generic message entry point for normal text messages (`handlers/message_handler.py`).
4. Slash commands may remain only for Telegram/system concerns such as `/start`, `/help`, or `/version`.
5. The LLM/agent must never access SQLAlchemy, SQLite, filesystem, or Telegram APIs directly.
6. The agent can only act through explicitly registered tools.
7. Tools call application/domain services; tools must not contain persistence implementation.
8. Services/repositories must not know about the LLM.
9. Tool arguments and results must be strongly typed with Pydantic models where practical.
10. Never invent a capability that is not represented by a registered tool.
11. If no tool can satisfy a request, return a clear "not supported" response rather than hallucinating an action.
12. Keep timezone handling deterministic in application code. The model may parse user intent, but the application owns timezone normalization.
13. Keep SQLite as the source of truth for reminders (and free days). JobQueue is execution infrastructure, not persistence.
14. Do not delete working functionality until the replacement path has tests.

## Currently registered tools

| Tool | Domain | Service | Persistence |
|---|---|---|---|
| `reminder-create` | Reminders | `ReminderService` | SQLite + JobQueue |
| `reminder-list` | Reminders | `ReminderService` | SQLite |
| `reminder-delete` | Reminders | `ReminderService` | SQLite + JobQueue |
| `reminder-update` | Reminders | `ReminderService` | SQLite + JobQueue |
| `free_day-create` | Free Days | `FreeDayService` | SQLite |
| `free_day-is_a_free_day` | Free Days | `FreeDayService` | SQLite |
| `free_day-next` | Free Days | `FreeDayService` | SQLite |
| `garbage-get_garbage_type_for_day` | Garbage | `GarbageService` | In-memory |
| `garbage-is_indifferenziato_week` | Garbage | `GarbageService` | In-memory |
| `diet-get_meals_by_day` | Diet | `DietService` | YAML files |
| `diet-get_meals_by_day_and_meal_type` | Diet | `DietService` | YAML files |

## Agent behavior

The agent should:

1. Receive the user's message and relevant conversation/user context.
2. Decide whether it can answer directly or needs a tool.
3. Call zero or more registered tools.
4. Observe tool results.
5. Produce a concise natural-language response in Italian.
6. Never claim a tool succeeded unless the tool result says it succeeded.
7. Never claim an operation was performed when no tool was invoked.
8. Ask a clarification question when required arguments are genuinely missing and cannot be safely inferred.
9. Refuse capability requests only by stating the actual missing capability; do not fabricate alternatives.

## Tool design

Every tool should have:

- a stable name, e.g. `reminder-create`
- a short description
- typed arguments (Pydantic BaseModel)
- typed result (`ToolResult`)
- a single responsibility
- deterministic side effects
- test coverage for success and failure

Prefer domain-oriented tool names:

- `reminder-create`
- `reminder-list`
- `reminder-delete`
- `reminder-update`
- `diet-get_meals_by_day`

Avoid generic tools such as `database.query` or `execute_python`.

## Safety

Do not introduce arbitrary code execution, shell execution, raw SQL tools, or filesystem tools for the agent.

Tools that cause external side effects must be explicit and narrowly scoped.

Before adding a new capability, define its tool contract first.

## Adding a new tool

1. Define Pydantic argument models.
2. Create or extend a service in `services/`.
3. Create or extend a repository in `database/` if persistence is needed.
4. Write the tool function in `agent/tools/` and register it via `@registry.register(...)`.
5. Wire it in `handlers/message_handler.py`.
6. Add tests covering the tool, service, and repository layers.

## Python/project conventions

- Python 3.12+
- Use `uv` for dependency and command execution.
- Prefer async code at Telegram/LLM boundaries.
- Keep synchronous database work isolated behind services/repositories.
- Use type hints.
- Use Ruff for linting/formatting.
- Do not introduce Node.js tooling unless explicitly requested.
- Prefer small modules over large "god" files.

## Testing

After meaningful changes, run at least:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

If a command is unavailable because the project has not configured it yet, report that instead of silently skipping it.

For agent/tool changes, tests should cover:

- tool selection/capability boundaries
- successful tool invocation
- tool failure propagation
- unsupported requests
- invalid tool arguments
- reminder timezone normalization
- reminder persistence
- scheduling/restore behavior where practical

## Git

Do not commit or push changes unless explicitly asked.
