"""Command handlers for the Telegram bot.

Handlers are plain functions that take input and return text.
They don't depend on Telegram — same logic works from --test mode,
unit tests, or Telegram.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
