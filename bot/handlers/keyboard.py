"""Inline keyboard builder for common actions."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Build the main inline keyboard with common actions.

    Returns:
        InlineKeyboardMarkup with buttons for common queries.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📚 Available Labs", callback_data="labs"),
            InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
        ],
        [
            InlineKeyboardButton(text="📊 Lab Scores", callback_data="scores"),
            InlineKeyboardButton(text="🏆 Top Students", callback_data="top_learners"),
        ],
        [
            InlineKeyboardButton(text="📈 Pass Rates", callback_data="pass_rates"),
            InlineKeyboardButton(text="👥 Groups", callback_data="groups"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_lab_selection_keyboard(labs: list[dict]) -> InlineKeyboardMarkup:
    """Build a keyboard with lab selection buttons.

    Args:
        labs: List of lab dicts with 'id' and 'title'.

    Returns:
        InlineKeyboardMarkup with lab buttons.
    """
    keyboard = []
    row = []
    for lab in labs[:10]:  # Limit to 10 labs
        lab_id = lab.get("id", lab.get("name", ""))
        lab_title = lab.get("title", lab.get("name", lab_id))
        # Shorten the display name
        display = lab_id.replace("lab-", "Lab ")
        row.append(InlineKeyboardButton(text=display, callback_data=f"lab_{lab_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Build a help keyboard with example queries.

    Returns:
        InlineKeyboardMarkup with example query buttons.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="❓ What labs exist?",
                callback_data="example_labs"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📊 Show lab scores",
                callback_data="example_scores"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏆 Find best lab",
                callback_data="example_best"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
