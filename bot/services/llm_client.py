"""LLM client with tool calling support.

Client for the Qwen Code API (or compatible OpenAI-style API) with tool definitions
for all 9 backend endpoints. The LLM decides which tools to call based on the user's
message and tool descriptions.
"""

import json
import sys
from typing import Any

import httpx

from config import load_config

# Tool definitions for all 9 backend endpoints
# The LLM reads these descriptions to decide which tool to call
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks available in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, e.g. 5, 10",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger a data sync from the autochecker to refresh data",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt that instructs the LLM to use tools
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS).
You have access to tools that let you fetch data from the backend API.

When the user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Once you have the data, provide a clear, helpful answer

If the user asks something you cannot answer with the available tools, say so politely and suggest what you CAN help with.

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Get score distribution for a lab
- get_pass_rates: Get pass rates per task for a lab
- get_timeline: Get submission timeline for a lab
- get_groups: Get per-group scores for a lab
- get_top_learners: Get top students for a lab
- get_completion_rate: Get completion rate for a lab
- trigger_sync: Refresh data from autochecker

Always call tools when you need data. Don't make up numbers - use the tools."""


class LLMClient:
    """Client for the LLM API with tool calling support."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        config = load_config()
        self.api_key = config["LLM_API_KEY"]
        self.base_url = config["LLM_API_BASE_URL"].rstrip("/")
        self.model = config["LLM_API_MODEL"]
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client.

        Returns:
            Configured httpx.AsyncClient with auth headers.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _debug(self, message: str) -> None:
        """Print debug message to stderr (visible in --test mode)."""
        print(message, file=sys.stderr)

    async def chat_with_tools(
        self,
        user_message: str,
        lms_client: Any,
        max_iterations: int = 5,
    ) -> str:
        """Chat with the LLM, allowing it to call tools.

        Args:
            user_message: The user's message.
            lms_client: The LMS client for executing tool calls.
            max_iterations: Maximum tool call iterations.

        Returns:
            The final response from the LLM.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        for iteration in range(max_iterations):
            # Call the LLM
            response_data = await self._call_llm(messages)

            # Check if the LLM wants to call tools
            tool_calls = response_data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])

            if not tool_calls:
                # No tool calls - return the LLM's response
                return response_data.get("choices", [{}])[0].get("message", {}).get("content", "I'm not sure how to help with that.")

            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}

                self._debug(f"[tool] LLM called: {tool_name}({tool_args})")

                # Execute the tool
                result = await self._execute_tool(tool_name, tool_args, lms_client)
                result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)

                self._debug(f"[tool] Result: {result_str[:200]}{'...' if len(result_str) > 200 else ''}")

                tool_results.append({
                    "tool_call_id": tool_call.get("id", ""),
                    "role": "tool",
                    "name": tool_name,
                    "content": result_str,
                })

            if tool_results:
                self._debug(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")

                # Add the assistant's message with tool calls
                messages.append(response_data.get("choices", [{}])[0].get("message", {}))
                # Add tool results
                messages.extend(tool_results)
            else:
                # No results - break to avoid infinite loop
                break

        # Final LLM call with tool results
        response_data = await self._call_llm(messages)
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "I encountered an error processing your request.")

    async def _call_llm(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """Call the LLM API.

        Args:
            messages: List of message dicts (role, content).

        Returns:
            Raw API response.
        """
        client = await self._get_client()

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "tool_choice": "auto",
        }

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def _execute_tool(self, tool_name: str, args: dict[str, Any], lms_client: Any) -> Any:
        """Execute a tool call.

        Args:
            tool_name: Name of the tool to call.
            args: Tool arguments.
            lms_client: The LMS client instance.

        Returns:
            Tool execution result.
        """
        tool_methods = {
            "get_items": lambda: lms_client.get_items(),
            "get_learners": lambda: lms_client.get_learners(),
            "get_scores": lambda: lms_client.get_scores(args.get("lab", "")),
            "get_pass_rates": lambda: lms_client.get_pass_rates(args.get("lab", "")),
            "get_timeline": lambda: lms_client.get_timeline(args.get("lab", "")),
            "get_groups": lambda: lms_client.get_groups(args.get("lab", "")),
            "get_top_learners": lambda: lms_client.get_top_learners(
                args.get("lab", ""), args.get("limit", 5)
            ),
            "get_completion_rate": lambda: lms_client.get_completion_rate(args.get("lab", "")),
            "trigger_sync": lambda: lms_client.trigger_sync(),
        }

        method = tool_methods.get(tool_name)
        if method:
            return await method()

        return {"error": f"Unknown tool: {tool_name}"}
