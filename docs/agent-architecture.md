# Dama Bot Agent Architecture

## Goal

Turn `dama_bot` from a collection of Telegram commands into a personal assistant whose natural-language interface is Telegram.

## User Experience

Instead of:

```text
/remind andare a fare quella cosa oggi alle 9
```

the preferred interface is:

```text
Ricordami di andare a fare quella cosa oggi alle 9.
```

The agent decides whether a registered capability is required.

## Architecture Overview

```
Telegram
  │
  ├─ /start, /help, /version   → Dedicated Telegram handlers
  │
  └─ Any text message           → Generic message handler
                                      │
                                      ▼
                               ┌─────────────┐
                               │    Agent     │  OpenAI chat completions
                               │  (core.py)   │  up to 5 tool-call turns
                               └──────┬──────┘
                                      │
                               ┌──────┴──────┐
                               │ ToolRegistry │
                               └──────┬──────┘
                                      │
              ┌───────────┬───────────┼───────────┬───────────┐
              ▼           ▼           ▼           ▼           ▼
         reminder-*   free_day-*  garbage-*    diet-*     (future)
              │           │           │           │
              ▼           ▼           ▼           ▼
          Services    Services    Services    Services
              │           │                       │
              ▼           ▼                       ▼
          Repositories Repositories           YAML files
              │           │
              ▼           ▼
            SQLite      SQLite
```

## Capability Model

A capability is represented by a **tool** registered in the `ToolRegistry`.

### Currently Registered Tools

| Tool Name | Domain | Description |
|---|---|---|
| `reminder-create` | Reminders | Create a new reminder with text + ISO datetime |
| `reminder-list` | Reminders | List all active (unsent, future) reminders |
| `reminder-delete` | Reminders | Delete a reminder by numeric ID |
| `reminder-update` | Reminders | Update text and/or datetime of a reminder |
| `free_day-create` | Free Days | Register a free day (every 3rd day pattern) |
| `free_day-is_a_free_day` | Free Days | Check whether a given date falls on a free day |
| `free_day-next` | Free Days | Find the next upcoming free day |
| `garbage-get_garbage_type_for_day` | Garbage | Get which waste type to sort on a given day |
| `garbage-is_indifferenziato_week` | Garbage | Check whether a date falls in an "indifferenziata" week |
| `diet-get_meals_by_day` | Diet | Retrieve all meals for a user for a given day |
| `diet-get_meals_by_day_and_meal_type` | Diet | Retrieve a specific meal type for a user and day |

### Unsupported Capabilities

If the user requests something not covered by a registered tool:

```text
User:  Mandami una mail a Mario.
Agent: Non posso inviare email: al momento non ho questa funzione.
```

The agent must **never pretend** an action succeeded.

## Tool Contract

Every tool must have:

- A stable name (e.g. `reminder-create`)
- A short description used by the LLM for tool selection
- Typed arguments (Pydantic `BaseModel`)
- A `ToolResult` return type (`success`, `message`, optional `data`)
- A single responsibility
- Deterministic side effects
- Test coverage for success and failure

Tools call services; they must **not** contain persistence logic directly.

## Message Flow

1. User sends a text message on Telegram
2. `handle_agent_message` builds a `UserContext` and forwards the text to `Agent.handle_message`
3. The Agent sends the message to OpenAI with the tool definitions
4. If the LLM returns tool calls, the registry validates arguments and executes the tool
5. Tool results are appended to the conversation and sent back to the LLM
6. Steps 3–5 repeat for up to 5 turns
7. The LLM's final text response is sent back to the user on Telegram

## Data Model

### SQLite Tables

- **reminders**: `id`, `text`, `remind_at`, `username`, `chat_id`, `message_id`, `sent`, `created_at`
- **free_days**: `id`, `date`, `username`, `chat_id`, `created_at`

### YAML Files

- `data/diet/<username>.yml` — per-user weekly diet plans with meals indexed by weekday (0=Monday)

### In-Memory

- `GarbageService` uses a hardcoded weekly schedule with alternating Wednesday types

## Reminder Lifecycle

1. **Creation**: Tool → Service → Repository (SQLite) + `schedule_reminder` (Telegram JobQueue)
2. **Execution**: JobQueue fires `send_reminder` callback → sends Telegram message → `mark_as_sent`
3. **Restore on startup**: `restore_pending_reminders` queries unsent future reminders and reschedules them
4. **Deletion/Update**: Tool → Service → cancel old job → update DB → optionally reschedule

SQLite is the **source of truth**; the JobQueue is execution infrastructure.

## Layering Rules

| Layer | May access | Must not access |
|---|---|---|
| Telegram handlers | Agent, UserContext | Services, Repositories, SQLAlchemy |
| Agent | ToolRegistry, OpenAI client | Services, Repositories, Telegram API |
| Tools | Services | Repositories, SQLAlchemy, Telegram API |
| Services | Repositories | Agent, Tools, Telegram API |
| Repositories | SQLAlchemy/YAML/filesystem | Agent, Services, Telegram API |
