# Dama Bot Agent Architecture

## Goal

Turn `dama_bot` from a collection of Telegram commands into a personal assistant whose natural-language interface is Telegram.

The application is built around a **plugin architecture**: each domain capability is implemented as an independent plugin that owns its tools, services, persistence and other domain-specific resources.

The core application provides the Agent runtime and plugin infrastructure without depending on individual capabilities.

---

## User Experience

The preferred interface is natural language.

Instead of:

```text
/remind andare a fare quella cosa oggi alle 9
```

the user can write:

```text
Ricordami di andare a fare quella cosa oggi alle 9.
```

The Agent decides whether one or more registered plugin capabilities are required.

Users do not need to know which plugin or tool implements a capability.

---

## Architecture Overview

```text
Telegram
  │
  ├─ /start, /help, /version
  │       │
  │       ▼
  │   Telegram handlers
  │
  └─ Any text message
          │
          ▼
   Generic message handler
          │
          ▼
      UserContext
          │
          ▼
   ┌─────────────────┐
   │      Agent      │
   │                 │
   │ OpenAI client   │
   │ Tool selection  │
   │ Tool execution  │
   └────────┬────────┘
            │
            ▼
      ┌─────────────┐
      │ ToolRegistry│
      └──────┬──────┘
             │
       registered tools
             │
    ┌────────┼─────────┬─────────┬─────────┐
    ▼        ▼         ▼         ▼         ▼
 Reminder  Free Day  Garbage    Diet     Future
 Plugin     Plugin    Plugin    Plugin   Plugins
    │        │         │         │
    ▼        ▼         ▼         ▼
 Services  Services  Services  Services
    │        │         │         │
    ▼        ▼         ▼         ▼
Repositories / domain resources
    │        │         │         │
 SQLite    SQLite    In-memory   YAML
```

The **core** must not contain domain-specific business logic.

Plugins provide the application's capabilities.

---

# Plugin Architecture

A plugin is a self-contained application module that adds one domain capability to `dama_bot`.

Examples:

```text
plugins/
├── reminder/
├── free_day/
├── garbage/
└── diet/
```

The exact filesystem structure may differ, but the architectural principle remains the same.

Each plugin is responsible for registering its capabilities with the core application.

A plugin may contain:

* tools;
* services;
* repositories;
* models;
* schemas;
* configuration;
* domain-specific data;
* translations;
* tests;
* other resources required by the capability.

The core application must not contain imports or dependencies on individual plugins unless required by the plugin discovery/registration mechanism.

---

## Plugin Responsibilities

A plugin should encapsulate a complete domain capability.

For example:

```text
Reminder Plugin
│
├── tools
│   ├── create
│   ├── list
│   ├── update
│   └── delete
│
├── services
├── repositories
├── models
├── translations
└── tests
```

The plugin exposes its capabilities through tools.

The Agent does not know how a plugin is implemented.

It only knows the tools registered by the plugin.

---

## Plugin Registration

Plugins must explicitly register their tools and required components with the application.

Conceptually:

```text
Application startup
       │
       ▼
Discover plugins
       │
       ▼
Plugin registration
       │
       ├── register tools
       ├── register services
       └── register plugin resources
       │
       ▼
ToolRegistry
       │
       ▼
Agent
```

Adding a new capability should primarily require creating a new plugin rather than modifying the Agent or core business logic.

The Agent must not contain domain-specific branching such as:

```python
if intent == "reminder":
    ...
elif intent == "diet":
    ...
```

Domain capabilities belong to plugins and are exposed through tools.

---

# Capability Model

A capability is exposed to the Agent as a **tool** registered by a plugin.

The ToolRegistry is the boundary between the Agent and the available capabilities.

### Currently Registered Tools

| Tool Name                             | Plugin   | Description                                             |
| ------------------------------------- | -------- | ------------------------------------------------------- |
| `reminder-create`                     | Reminder | Create a new reminder with text + ISO datetime          |
| `reminder-list`                       | Reminder | List all active (unsent, future) reminders              |
| `reminder-delete`                     | Reminder | Delete a reminder by numeric ID                         |
| `reminder-update`                     | Reminder | Update text and/or datetime of a reminder               |
| `free_day-create`                     | Free Day | Register a free day                                     |
| `free_day-is_a_free_day`              | Free Day | Check whether a given date falls on a free day          |
| `free_day-next`                       | Free Day | Find the next upcoming free day                         |
| `garbage-get_garbage_type_for_day`    | Garbage  | Get which waste type to sort on a given day             |
| `garbage-is_indifferenziato_week`     | Garbage  | Check whether a date falls in an "indifferenziata" week |
| `diet-get_meals_by_day`               | Diet     | Retrieve all meals for a user for a given day           |
| `diet-get_meals_by_day_and_meal_type` | Diet     | Retrieve a specific meal type for a user and day        |

This list represents the currently installed plugins and their registered capabilities. It is not a closed set.

---

# Adding a New Capability

A new capability should normally be implemented as a new plugin.

For example:

```text
plugins/weather/
```

The plugin should:

1. implement its domain logic;
2. expose its capabilities through tools;
3. register those tools;
4. contain its own tests;
5. contain its own translations;
6. own any domain-specific persistence or resources.

The Agent and core application should not require domain-specific changes.

The goal is to make plugins independently implementable and removable.

---

# Unsupported Capabilities

If the user requests something not covered by a registered tool:

```text
User:  Mandami una mail a Mario.
Agent: Non posso inviare email: al momento non ho questa funzione.
```

The Agent must **never pretend** an action succeeded.

The absence of a registered tool means that the capability is unavailable.

The Agent must not attempt to implement or simulate missing functionality.

---

# Tool Contract

Every tool must have:

* a stable name;
* a short description used by the LLM for tool selection;
* typed arguments using Pydantic `BaseModel`;
* a `ToolResult` return type;
* a single responsibility;
* deterministic side effects;
* test coverage for success and failure.

Example:

```text
Tool
 │
 ├── validates input
 │
 ▼
Service
 │
 ▼
domain operation
 │
 ▼
ToolResult
```

Tools call services.

Tools must **not** contain persistence logic directly.

Tools must not access repositories, SQLAlchemy, Telegram APIs or other infrastructure directly.

---

# ToolResult

Tools communicate their execution result through a common `ToolResult` abstraction.

Conceptually:

```python
ToolResult(
    success=True,
    message="Reminder created successfully",
    data={...},
)
```

or:

```python
ToolResult(
    success=False,
    message="Reminder not found",
    data=None,
)
```

The concrete implementation must follow the project's current models and conventions.

The Agent must use the result to determine the appropriate response.

A failed tool execution must never be represented to the user as a successful operation.

---

# Message Flow

1. User sends a text message on Telegram.
2. `handle_agent_message` builds a `UserContext`.
3. The Telegram layer forwards the normalized text and context to `Agent.handle_message`.
4. The Agent sends the message and available tool definitions to OpenAI.
5. If the LLM returns tool calls, the ToolRegistry validates their arguments.
6. The corresponding plugin tool is executed.
7. The tool calls its plugin service.
8. The tool result is appended to the conversation.
9. The Agent sends the updated conversation back to the LLM.
10. Steps 4–9 repeat for up to 5 tool-call turns.
11. The LLM's final text response is sent back to Telegram.

The Agent interacts with capabilities exclusively through the ToolRegistry.

---

# Telegram Message Handling

Telegram is an adapter and must not contain domain logic.

### Private chats

Every text message in a private chat may be forwarded to the Agent.

### Groups

The bot processes a group message only when the bot is explicitly mentioned.

```text
Group message without mention
        │
        ▼
      ignored
```

```text
@dama_bot ricordami di comprare il latte
        │
        ▼
Telegram adapter
        │
        ▼
Agent
```

Mention detection belongs to the Telegram adapter.

The Agent must not contain logic related to Telegram mentions.

When a bot mention is present, the Telegram adapter should normalize the message before passing it to the Agent.

For example:

```text
@dama_bot ricordami di comprare il latte
```

becomes:

```text
ricordami di comprare il latte
```

The Agent receives Telegram-independent input plus a `UserContext`.

---

# UserContext

The Telegram layer creates a `UserContext` containing the contextual information required by the Agent and plugins.

Typical information includes:

* user ID;
* chat ID;
* chat type;
* username;
* other contextual information required by the application.

The exact structure is defined by the implementation.

Plugins may use the context through their service/tool interfaces when required.

The Agent must not obtain this information directly from the Telegram API.

---

# Data Model

Persistence is owned by the plugin that requires it.

### Reminder Plugin

SQLite table:

```text
reminders:
    id
    text
    remind_at
    username
    chat_id
    message_id
    sent
    created_at
```

### Free Day Plugin

SQLite table:

```text
free_days:
    id
    date
    username
    chat_id
    created_at
```

### Diet Plugin

User-specific YAML files:

```text
data/diet/<username>.yml
```

containing weekly meal plans indexed by weekday:

```text
0 = Monday
```

### Garbage Plugin

`GarbageService` uses an in-memory weekly schedule with alternating Wednesday types.

Plugins own their persistence and domain-specific resources.

The core application must not contain plugin-specific persistence logic.

---

# Reminder Plugin Lifecycle

The Reminder plugin has an additional scheduling responsibility.

### Creation

```text
reminder-create
      ↓
ReminderService
      ↓
ReminderRepository
      ↓
SQLite

      +

schedule_reminder
      ↓
Telegram JobQueue
```

### Execution

```text
JobQueue
    ↓
send_reminder
    ↓
Telegram
    ↓
mark_as_sent
```

### Restore on startup

```text
Application startup
      ↓
ReminderRepository
      ↓
unsent + future reminders
      ↓
schedule_reminder
```

### Deletion / Update

```text
Tool
 ↓
ReminderService
 ↓
cancel existing job
 ↓
update/delete database record
 ↓
optionally schedule new job
```

SQLite is the **source of truth**.

The Telegram JobQueue is execution infrastructure and must not be treated as persistent state.

The scheduler is independent from the Agent: executing an existing reminder must not require an LLM call.

---

# Internationalization

Internationalization is implemented at the **plugin level**.

Each plugin owns the translations for its user-facing strings.

Conceptually:

```text
plugins/
├── reminder/
│   └── translations/
│       ├── en.*
│       └── it.*
│
├── diet/
│   └── translations/
│       ├── en.*
│       └── it.*
│
└── garbage/
    └── translations/
        ├── en.*
        └── it.*
```

The exact format and directory structure should follow the project's implementation.

Currently supported languages are:

* English (`en`) — default/fallback language
* Italian (`it`)

Plugins must not rely on translations owned by another plugin.

Adding a new plugin must allow its translations to be added without modifying a global collection of plugin-specific strings.

User-facing strings must not be hardcoded in plugin business logic when they require localization.

---

# Layering Rules

| Layer               | May access                                       | Must not access                                        |
| ------------------- | ------------------------------------------------ | ------------------------------------------------------ |
| Telegram handlers   | Agent, UserContext                               | Services, Repositories, SQLAlchemy                     |
| Agent               | ToolRegistry, OpenAI client                      | Services, Repositories, Telegram API, plugin internals |
| ToolRegistry        | Registered tools                                 | Domain logic                                           |
| Plugin Tools        | Plugin Services, plugin context                  | Repositories, SQLAlchemy, Telegram API                 |
| Plugin Services     | Plugin Repositories, domain resources            | Agent, Tools, Telegram API                             |
| Plugin Repositories | SQLAlchemy, YAML, filesystem, plugin persistence | Agent, Telegram API                                    |
| Core                | Plugin infrastructure, registry, configuration   | Plugin-specific business logic                         |

A plugin may expose additional internal layers when needed, but dependencies must always flow toward lower-level infrastructure.

---

# Core vs Plugins

The distinction between **core** and **plugins** is fundamental.

## Core

The core contains generic infrastructure such as:

* Agent;
* ToolRegistry;
* Tool contracts;
* UserContext;
* application lifecycle;
* plugin discovery/registration;
* common configuration;
* common infrastructure abstractions.

The core should remain domain-agnostic.

## Plugins

Plugins contain domain-specific functionality such as:

* reminders;
* free days;
* garbage;
* diet;
* future capabilities.

A plugin owns the implementation of its domain.

---

# Design Principles

### 1. Plugin isolation

A plugin should be independently understandable and removable.

### 2. Explicit capabilities

The Agent can only perform operations exposed through registered tools.

### 3. No domain logic in Telegram

Telegram is only an interface adapter.

### 4. No domain logic in the Agent

The Agent decides **which capability to use**, but does not implement the capability.

### 5. Services own business logic

Tools should remain thin and deterministic.

### 6. Persistence belongs to the plugin

A plugin owns the persistence required by its domain.

### 7. Core remains domain-agnostic

Adding a plugin should not require adding domain-specific code to the Agent.

### 8. Fail safely

The Agent must never claim that an operation succeeded unless the corresponding tool successfully executed it.

### 9. Internationalization belongs to plugins

Plugin-specific user-facing strings and translations must remain inside the plugin.

### 10. Prefer composition over coupling

The system should grow by composing independent plugins rather than increasing coupling inside the core application.
