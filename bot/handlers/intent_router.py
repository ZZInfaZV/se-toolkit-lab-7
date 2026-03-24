"""Intent router for natural language queries.

Routes plain text messages to the LLM, which decides which tools to call
to answer the user's question.
"""

import asyncio
import re

from services.llm_client import LLMClient
from services.lms_client import LMSClient


def is_greeting(text: str) -> bool:
    """Check if the message is a greeting."""
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "привет", "здравствуйте"]
    text_lower = text.lower().strip()
    return any(text_lower.startswith(g) for g in greetings)


def is_gibberish(text: str) -> bool:
    """Check if the message looks like gibberish (no spaces, mostly consonants, or very short)."""
    text = text.strip()
    # Too short
    if len(text) < 3:
        return True
    # No spaces and looks random
    if " " not in text and len(text) > 5:
        vowels = set("aeiouаеёиоуыэюя")
        vowel_count = sum(1 for c in text.lower() if c in vowels)
        # Less than 20% vowels looks suspicious
        if vowel_count / len(text) < 0.2:
            return True
    return False


def handle_intent(text: str) -> str:
    """Handle plain text intent using LLM routing.

    Args:
        text: The user's message.

    Returns:
        Response text.
    """
    async def _route_intent() -> str:
        llm_client = LLMClient()
        lms_client = LMSClient()

        try:
            # Handle greetings
            if is_greeting(text):
                return (
                    "👋 Hello! I'm the LMS Bot. I can help you with:\n\n"
                    "• Checking lab information\n"
                    "• Viewing scores and pass rates\n"
                    "• Finding top students\n"
                    "• Comparing groups\n\n"
                    "Just ask me a question like:\n"
                    "• \"What labs are available?\"\n"
                    "• \"Show me scores for lab 4\"\n"
                    "• \"Which lab has the lowest pass rate?\""
                )

            # Handle gibberish
            if is_gibberish(text):
                return (
                    "🤔 I'm not sure I understand. Try asking me a question like:\n\n"
                    "• \"What labs are available?\"\n"
                    "• \"Show me scores for lab 4\"\n"
                    "• \"Who are the top students?\"\n"
                    "• \"Which lab has the lowest pass rate?\"\n\n"
                    "Or use commands like /help to see what I can do."
                )

            # Use LLM for intent routing
            response = await llm_client.chat_with_tools(text, lms_client)
            return response

        except Exception as e:
            # Fallback for LLM errors
            error_msg = str(e).lower()
            if "401" in error_msg or "unauthorized" in error_msg:
                return (
                    "⚠️ The LLM service is unavailable (authentication error). "
                    "This usually means the Qwen token has expired. "
                    "Please restart the proxy: `cd ~/qwen-code-oai-proxy && docker compose restart`"
                )
            elif "connection" in error_msg or "timeout" in error_msg:
                return (
                    "⚠️ I couldn't reach the LLM service. "
                    "Please check that the LLM backend is running."
                )
            else:
                return (
                    f"⚠️ I encountered an error: {e}\n\n"
                    "Try using a command like /help or /labs instead."
                )
        finally:
            await llm_client.close()
            await lms_client.close()

    return asyncio.run(_route_intent())
