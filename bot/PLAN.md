# Bot Development Plan

This document outlines the implementation plan for the LMS Telegram bot across all four tasks.

## Overview

The goal is to build a Telegram bot that lets users interact with the LMS backend through chat. Users can check system health, browse labs and scores, and ask questions in plain language. The bot uses an LLM to understand what the user wants and fetch the right data.

## Architecture

The bot follows a layered architecture:

```
┌──────────────────────────────────────────────────────────────┐
│  Telegram User                                               │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐                                         │
│  │  aiogram        │  ← Telegram transport layer            │
│  │  (bot.py)       │                                         │
│  └────────┬────────┘                                         │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                         │
│  │  Handlers       │  ← Command logic (no Telegram deps)    │
│  │  (handlers/)    │                                         │
│  └────────┬────────┘                                         │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐     ┌──────────────────┐                │
│  │  API Client     │     │  LLM Client       │                │
│  │  (services/)    │     │  (services/)      │                │
│  └────────┬────────┘     └────────┬─────────┘                │
│           │                       │                          │
│           ▼                       ▼                          │
│  ┌─────────────────┐     ┌──────────────────┐                │
│  │  LMS Backend    │     │  Qwen Code API   │                │
│  │  (FastAPI)      │     │  (LLM)           │                │
│  └─────────────────┘     └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
```

## Task 1: Plan and Scaffold

**Goal:** Create project structure with testable handler architecture.

**Approach:**
- Create `bot/` directory with `handlers/`, `services/`, and configuration modules
- Implement handlers as pure functions that take command text and return response text
- Build `--test` mode that calls handlers directly without Telegram
- This separation means the same handler logic works from `--test`, unit tests, or Telegram

**Deliverables:**
- `bot/bot.py` — entry point with `--test` mode
- `bot/handlers/` — command handlers (no Telegram dependency)
- `bot/config.py` — environment variable loading
- `bot/pyproject.toml` — dependencies
- `bot/PLAN.md` — this document

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
- Create `bot/services/lms_client.py` — async HTTP client for the backend
- Implement Bearer token authentication using `LMS_API_KEY`
- Update handlers to call real endpoints:
  - `/health` → `GET /health` (or ping the root endpoint)
  - `/labs` → `GET /items/` with filtering
  - `/scores <lab>` → `GET /analytics/...` with lab parameter
- Add error handling for network failures, timeouts, and API errors
- Return user-friendly messages when the backend is unavailable

**Key pattern:** The API client is a separate service. Handlers call it, but don't know HTTP details.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Let users ask questions in plain language (e.g., "what labs are available?").

**Approach:**
- Create `bot/services/llm_client.py` — client for the Qwen Code API
- Define tool descriptions for each backend action (get_health, get_labs, get_scores, etc.)
- Build an intent router that:
  1. Sends user message + tool descriptions to LLM
  2. LLM returns which tool to call with arguments
  3. Bot executes the tool and returns the result
- The key insight: the LLM reads tool descriptions to decide what to call. Description quality matters more than prompt engineering.

**Tool descriptions example:**
```
get_labs: List all available labs. No arguments needed.
get_scores: Get pass rates for a specific lab. Argument: lab_name (e.g., "lab-04")
```

## Task 4: Containerize and Document

**Goal:** Deploy the bot alongside the existing backend.

**Approach:**
- Create `bot/Dockerfile` — multi-stage build with uv for dependency installation
- Add bot service to `docker-compose.yml`
- Configure networking: bot connects to backend via service name (`http://backend:8000`), not `localhost`
- Set up environment variables for containerized deployment
- Write deployment documentation in the README

**Docker networking note:** Inside Docker Compose, containers use service names as hostnames. The bot uses `http://backend:8000` to reach the backend, not `localhost:42002`.

## Testing Strategy

1. **Unit tests** — test handlers in isolation (pytest)
2. **Test mode** — `--test` flag for manual verification without Telegram
3. **Integration tests** — test with real backend (Task 2+)
4. **Telegram testing** — send commands to the deployed bot

## Git Workflow

For each task:
1. Create an issue on GitHub
2. Create a branch: `task-N-short-description`
3. Commit changes incrementally
4. Open a PR with `Closes #issue-number` in the description
5. Partner reviews and approves
6. Merge to main

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Backend API changes | Use typed API client, test endpoints early |
| LLM costs | Use free tier (Qwen Code: 1000 requests/day) |
| Telegram rate limits | Add basic throttling if needed |
| Docker networking issues | Test service-to-service connectivity before deploying bot |

## Success Criteria

By the end of Task 4:
- All P0 requirements met (testable handlers, CLI test mode, all slash commands)
- P1 requirements met (natural language intent routing, LLM tool use)
- Bot deployed and running on VM
- Documentation complete
