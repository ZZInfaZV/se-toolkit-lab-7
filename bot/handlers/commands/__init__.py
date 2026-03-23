"""Command handler implementations.

Each handler is a function that takes a command string and optional arguments,
and returns a text response. No Telegram dependency.
"""


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
    # TODO: Task 2 — call backend API
    return "🔍 Health check: Backend status will be implemented in Task 2"


def handle_labs(command: str) -> str:
    """Handle /labs command.
    
    Args:
        command: The command string (e.g., "/labs").
        
    Returns:
        List of available labs.
    """
    # TODO: Task 2 — call backend API
    return "📋 Available labs will be implemented in Task 2"


def handle_scores(command: str, lab_name: str = "") -> str:
    """Handle /scores command.
    
    Args:
        command: The command string (e.g., "/scores").
        lab_name: The lab name argument.
        
    Returns:
        Pass rates for the specified lab.
    """
    # TODO: Task 2 — call backend API
    if lab_name:
        return f"📊 Scores for {lab_name} will be implemented in Task 2"
    return "📊 Scores: Please specify a lab name, e.g., /scores lab-04"
