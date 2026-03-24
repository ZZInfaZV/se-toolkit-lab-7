"""Telegram bot entry point.

Usage:
    uv run bot.py              # Run the Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""

import argparse
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import handle_intent
from handlers.keyboard import get_main_keyboard


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command string into command and arguments.

    Args:
        text: The input text (e.g., "/scores lab-04" or "/start").

    Returns:
        Tuple of (command, arguments).
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lstrip("/")
    args = parts[1] if len(parts) > 1 else ""
    return command, args


def handle_command_sync(command: str, args: str = "") -> str:
    """Route a command to the appropriate handler.

    Args:
        command: The command name (e.g., "start", "help").
        args: Command arguments.

    Returns:
        Response text.
    """
    handlers = {
        "start": lambda: handle_start(f"/{command}"),
        "help": lambda: handle_help(f"/{command}"),
        "health": lambda: handle_health(f"/{command}"),
        "labs": lambda: handle_labs(f"/{command}"),
        "scores": lambda: handle_scores(f"/{command}", args),
    }

    handler = handlers.get(command)
    if handler:
        return handler()
    return f"❓ Unknown command: /{command}. Use /help to see available commands."


def run_test_mode(command_text: str) -> None:
    """Run in test mode: call handler directly and print response.

    Args:
        command_text: The command to test (e.g., "/start").
    """
    # Check if it's a plain text query (not a command)
    if not command_text.strip().startswith("/"):
        response = handle_intent(command_text)
        print(response)
        sys.exit(0)
    
    command, args = parse_command(command_text)
    response = handle_command_sync(command, args)
    print(response)
    sys.exit(0)


async def handle_start_command(message: types.Message) -> None:
    """Telegram handler for /start command."""
    response = handle_start("/start")
    keyboard = get_main_keyboard()
    await message.answer(response, reply_markup=keyboard)


async def handle_help_command(message: types.Message) -> None:
    """Telegram handler for /help command."""
    response = handle_help("/help")
    await message.answer(response)


async def handle_health_command(message: types.Message) -> None:
    """Telegram handler for /health command."""
    response = handle_health("/health")
    await message.answer(response)


async def handle_labs_command(message: types.Message) -> None:
    """Telegram handler for /labs command."""
    response = handle_labs("/labs")
    await message.answer(response)


async def handle_scores_command(message: types.Message) -> None:
    """Telegram handler for /scores command."""
    args = message.text.split(maxsplit=1)
    lab_name = args[1] if len(args) > 1 else ""
    response = handle_scores("/scores", lab_name)
    await message.answer(response)


async def handle_text_message(message: types.Message) -> None:
    """Handle plain text messages using LLM intent routing."""
    text = message.text or ""
    
    # Skip if it's a command (should be handled by other handlers)
    if text.startswith("/"):
        return
    
    # Use LLM intent router
    response = handle_intent(text)
    await message.answer(response)


async def handle_callback_query(callback: types.CallbackQuery) -> None:
    """Handle inline keyboard button clicks."""
    action = callback.data
    
    if action == "labs":
        response = handle_labs("/labs")
        await callback.message.answer(response)
    elif action == "health":
        response = handle_health("/health")
        await callback.message.answer(response)
    elif action == "scores":
        await callback.message.answer("📊 To view scores, please type: /scores lab-04 (replace with the lab number)")
    elif action == "top_learners":
        await callback.message.answer("🏆 To see top students, ask: \"Who are the top 5 students in lab 4?\"")
    elif action == "pass_rates":
        await callback.message.answer("📈 To view pass rates, ask: \"Show pass rates for lab 3\"")
    elif action == "groups":
        await callback.message.answer("👥 To compare groups, ask: \"Which group is best in lab 2?\"")
    elif action.startswith("example_"):
        examples = {
            "example_labs": "What labs are available?",
            "example_scores": "Show me scores for lab 4",
            "example_best": "Which lab has the lowest pass rate?",
        }
        example = examples.get(action, "")
        if example:
            response = handle_intent(example)
            await callback.message.answer(response)
    
    await callback.answer()


async def run_telegram_bot() -> None:
    """Run the Telegram bot."""
    config = load_config()

    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN not found in .env.bot.secret")
        print("Please create .env.bot.secret with your Telegram bot token.")
        sys.exit(1)

    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()

    # Register command handlers
    dp.message.register(handle_start_command, CommandStart())
    dp.message.register(handle_help_command, Command("help"))
    dp.message.register(handle_health_command, Command("health"))
    dp.message.register(handle_labs_command, Command("labs"))
    dp.message.register(handle_scores_command, Command("scores"))

    # Register text message handler for plain text (LLM routing)
    dp.message.register(handle_text_message)

    # Register callback query handler for inline buttons
    dp.callback_query.register(handle_callback_query)

    print("Bot is starting...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command and print response (e.g., '/start' or 'hello')",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        import asyncio
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
