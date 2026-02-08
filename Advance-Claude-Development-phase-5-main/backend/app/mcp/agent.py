"""OpenAI Agents SDK agent setup with MCP tools for task management."""

import json
import uuid
from typing import Any

import structlog
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.mcp.tools import TOOLS

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a helpful AI assistant for managing tasks and todos.
You can help users create, update, complete, delete, and list their tasks.

When users ask you to perform task operations, use the available tools.
Always confirm what you've done after using a tool.

Guidelines:
- Default priority is "medium" unless the user specifies otherwise.
- When listing tasks, show them in a readable format.
- If a user mentions "high priority" or "urgent", set priority to "high".
- If a user mentions "low priority", set priority to "low".
- Parse natural language dates when possible (e.g., "by Friday", "tomorrow").
- Be concise and helpful.
"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": (
                "Create a new task with title, description, "
                "priority, tags, due date, and recurrence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {
                        "type": "string",
                        "description": "Optional description",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority (default: medium)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tag names",
                    },
                    "due_date": {"type": "string", "description": "ISO 8601 due date"},
                    "reminder_offset": {
                        "type": "string",
                        "description": "Reminder offset (e.g. 1h, 1d)",
                    },
                    "is_recurring": {
                        "type": "boolean",
                        "description": "Whether task recurs",
                    },
                    "recurrence_pattern": {
                        "type": "object",
                        "description": "Recurrence config (type, days_of_week, etc.)",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": (
                "Update an existing task. Only include fields you want to change."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "due_date": {"type": "string"},
                    "reminder_offset": {"type": "string"},
                    "is_recurring": {"type": "boolean"},
                    "recurrence_pattern": {"type": "object"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID to complete",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to delete"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks with optional filtering, sorting, and search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "Search query"},
                    "status": {"type": "string", "enum": ["pending", "completed"]},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "sort_by": {
                        "type": "string",
                        "enum": ["created_at", "due_date", "priority", "title"],
                    },
                    "sort_order": {"type": "string", "enum": ["asc", "desc"]},
                    "page": {"type": "integer"},
                    "page_size": {"type": "integer"},
                },
            },
        },
    },
]


async def execute_tool(
    tool_name: str,
    tool_args: dict[str, Any],
    db: AsyncSession,
    user_id: uuid.UUID,
) -> dict:
    """Execute a tool function by name."""
    func = TOOLS.get(tool_name)
    if func is None:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return await func(db, user_id, **tool_args)
    except Exception as exc:
        logger.warning("tool_execution_failed", tool=tool_name, error=str(exc))
        return {"error": str(exc)}


async def process_chat(
    db: AsyncSession,
    user_id: uuid.UUID,
    message: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Process a chat message through the OpenAI-compatible agent."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    actions_taken: list[dict] = []

    # Agent loop — handle tool calls iteratively
    for _ in range(5):  # Max 5 tool-call rounds
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                result = await execute_tool(tool_name, tool_args, db, user_id)
                actions_taken.append({"tool": tool_name, "result": result})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )
        else:
            # Final text response
            return {
                "response": choice.message.content or "",
                "actions_taken": actions_taken,
            }

    # If we exhaust the loop, return whatever we have
    return {
        "response": "I processed your request.",
        "actions_taken": actions_taken,
    }
