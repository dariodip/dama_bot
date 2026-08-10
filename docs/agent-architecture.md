# Dama Bot Agent Architecture

## Goal

Turn `dama_bot` from a collection of Telegram commands into a personal assistant whose natural-language interface is Telegram.

## User experience

Instead of:

```text
/remind andare a fare quella cosa oggi alle 9
```

the preferred interface is:

```text
Ricordami di andare a fare quella cosa oggi alle 9.
```

The agent decides whether a registered capability is required.

## Capability model

A capability is represented by a tool.

Example:

```text
reminder-create
reminder-list
reminder-delete
reminder-update
```

The model never gets unrestricted access to application internals.

## Unsupported capability

Example user request:

```text
Mandami una mail a Mario.
```

If there is no `email.send` tool, the agent must answer truthfully:

```text
Non posso inviare email: al momento non ho questa funzione.
```

It must not pretend the email was sent.

## Initial migration

Current:

```text
/remind
  -> reminder handler
  -> parser
  -> service
  -> SQLite
  -> JobQueue
```

Target:

```text
Telegram message
  -> Agent
  -> reminder-create
  -> reminder service
  -> SQLite
  -> JobQueue
```

The reminder service and scheduler should remain reusable.

## Long-term architecture

```text
                         +----------------+
                         |    Telegram    |
                         +-------+--------+
                                 |
                                 v
                         +---------------+
                         |     Agent     |
                         +-------+-------+
                                 |
                       +---------+---------+
                       |    Tool Registry |
                       +---------+---------+
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
        reminder.*          calendar.*         shopping.*
              |                  |                  |
              v                  v                  v
          services           services           services
              |                  |                  |
              +------------------+------------------+
                                 |
                           infrastructure
```

Keep the first implementation deliberately small.
