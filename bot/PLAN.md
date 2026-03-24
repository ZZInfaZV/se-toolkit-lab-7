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

**Implementation:**

### Files created

- `bot/services/llm_client.py` — LLM client with tool calling support
- `bot/services/lms_client.py` — extended with 9 methods for all backend endpoints
- `bot/handlers/intent_router.py` — plain text intent router using LLM
- `bot/handlers/keyboard.py` — inline keyboard button builder

### Tool definitions (9 backend endpoints)

| Tool | Endpoint | Description |
|------|----------|-------------|
| `get_items` | `GET /items/` | List of labs and tasks |
| `get_learners` | `GET /learners/` | Enrolled students and groups |
| `get_scores` | `GET /analytics/scores?lab=` | Score distribution (4 buckets) |
| `get_pass_rates` | `GET /analytics/pass-rates?lab=` | Per-task averages and attempt counts |
| `get_timeline` | `GET /analytics/timeline?lab=` | Submissions per day |
| `get_groups` | `GET /analytics/groups?lab=` | Per-group scores and student counts |
| `get_top_learners` | `GET /analytics/top-learners?lab=&limit=` | Top N learners by score |
| `get_completion_rate` | `GET /analytics/completion-rate?lab=` | Completion rate percentage |
| `trigger_sync` | `POST /pipeline/sync` | Refresh data from autochecker |

### How it works

```
User: "which lab has the worst results?"
  → bot sends message + tool definitions to LLM
  → LLM decides: call get_pass_rates for each lab
  → bot executes the API calls
  → feeds results back to LLM
  → LLM summarizes
  → bot sends response
```

### Key patterns

1. **Tool calling loop**: The LLM returns tool calls, the bot executes them, feeds results back, and the LLM produces the final answer.

2. **Debug logging**: Tool calls and results are printed to stderr so they're visible in `--test` mode (which only shows the final response on stdout).

3. **Fallback handling**: Greetings and gibberish are detected without the LLM. LLM errors produce helpful messages instead of crashes.

4. **Inline keyboards**: The `/start` command shows buttons for common actions (labs, health, scores, top learners, pass rates, groups).

### Testing

```terminal
# Single-step queries
uv run bot.py --test "what labs are available"
uv run bot.py --test "show me scores for lab 4"

# Multi-step queries (LLM chains multiple API calls)
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "which group is best in lab 3"

# Fallback cases
uv run bot.py --test "hello"       # greeting
uv run bot.py --test "asdfgh"      # gibberish
```

**Key insight:** The LLM reads tool descriptions to decide what to call. Description quality matters more than prompt engineering.

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
