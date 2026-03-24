"""Command handler implementations.

Each handler is a function that takes a command string and optional arguments,
and returns a text response. No Telegram dependency.
"""

import asyncio

from services.lms_client import LMSClient


def handle_start(command: str) -> str:
    """Handle /start command.

    Args:
        command: The command string (e.g., "/start").

    Returns:
        Welcome message.
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check system health, browse labs, and view scores.\n"
        "Use /help to see all available commands."
    )


def handle_help(command: str) -> str:
    """Handle /help command.

    Args:
        command: The command string (e.g., "/help").

    Returns:
        List of available commands.
    """
    return (
        "📚 Available commands:\n\n"
        "/start — Welcome message\n"
        "/help — Show this help message\n"
        "/health — Check backend system status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View pass rates for a specific lab"
    )


def handle_health(command: str) -> str:
    """Handle /health command.

    Args:
        command: The command string (e.g., "/health").

    Returns:
        Backend health status.
    """
    async def _check_health() -> str:
        client = LMSClient()
        try:
            result = await client.get_health()
            if result["healthy"]:
                return f"✅ Backend is healthy. {result['item_count']} items available."
            return f"❌ Backend error: {result['error']}. Check that the services are running."
        finally:
            await client.close()

    return asyncio.run(_check_health())


def handle_labs(command: str) -> str:
    """Handle /labs command.

    Args:
        command: The command string (e.g., "/labs").

    Returns:
        List of available labs.
    """
    async def _get_labs() -> str:
        client = LMSClient()
        try:
            result = await client.get_labs()
            if "error" in result:
                return f"Backend error: {result['error']}. Check that the services are running."
            labs = result["labs"]
            if not labs:
                return "No labs available."
            lines = ["Available labs:"]
            for lab in labs:
                lines.append(f"- {lab.get('title', 'Unknown Lab')}")
            return "\n".join(lines)
        finally:
            await client.close()

    return asyncio.run(_get_labs())


def handle_scores(command: str, lab_name: str = "") -> str:
    """Handle /scores command.

    Args:
        command: The command string (e.g., "/scores").
        lab_name: The lab name argument.

    Returns:
        Pass rates for the specified lab.
    """
    if not lab_name:
        return "📊 Scores: Please specify a lab name, e.g., /scores lab-04"

    async def _get_scores() -> str:
        client = LMSClient()
        try:
            result = await client.get_pass_rates(lab_name)
            if "error" in result:
                return f"❌ Backend error: {result['error']}. Check that the services are running."
            pass_rates = result["pass_rates"]
            if not pass_rates:
                return f"No pass rates available for {lab_name}."
            # Format lab name for display (lab-04 -> Lab 04)
            display_name = lab_name.replace("lab-", "Lab ").replace("Lab 0", "Lab 0")
            lines = [f"Pass rates for {display_name}:"]
            for rate in pass_rates:
                task_name = rate.get("task_name", rate.get("task", "Unknown"))
                avg_score = rate.get("avg_score", rate.get("pass_rate", 0))
                attempts = rate.get("attempts", 0)
                lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
            return "\n".join(lines)
        finally:
            await client.close()

    return asyncio.run(_get_scores())
