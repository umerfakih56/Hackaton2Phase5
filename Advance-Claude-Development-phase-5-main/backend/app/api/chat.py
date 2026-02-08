"""Chat endpoint — processes messages through the AI agent."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.mcp.agent import process_chat
from app.models.conversation import Conversation, Message, MessageRole

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatAction(BaseModel):
    tool: str
    result: dict


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    actions_taken: list[ChatAction]


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    summary="Send a chat message",
    description=(
        "Process a natural-language message through the AI agent. "
        "The agent can create, update, complete, delete, "
        "and list tasks via MCP tools."
    ),
)
async def chat(
    user_id: uuid.UUID,
    body: ChatRequest,
    auth_user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Verify user matches auth token
    if user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    # Get or create conversation
    conv_id: uuid.UUID
    history: list[dict] = []

    if body.conversation_id:
        try:
            conv_id = uuid.UUID(body.conversation_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid conversation_id")

        # Load existing conversation history
        from sqlalchemy import select

        conv = (
            await db.execute(
                select(Conversation).where(
                    Conversation.id == conv_id, Conversation.user_id == user_id
                )
            )
        ).scalar_one_or_none()

        if conv is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        msgs = (
            (
                await db.execute(
                    select(Message)
                    .where(Message.conversation_id == conv_id)
                    .order_by(Message.created_at.asc())
                )
            )
            .scalars()
            .all()
        )

        history = [{"role": m.role.value, "content": m.content} for m in msgs]
    else:
        conv = Conversation(user_id=user_id)
        db.add(conv)
        await db.flush()
        conv_id = conv.id

    # Save user message
    db.add(
        Message(
            conversation_id=conv_id,
            role=MessageRole.USER,
            content=body.message,
        )
    )

    # Process through agent
    try:
        result = await process_chat(db, user_id, body.message, history)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent error: {exc}")

    # Save assistant response
    db.add(
        Message(
            conversation_id=conv_id,
            role=MessageRole.ASSISTANT,
            content=result["response"],
        )
    )

    await db.commit()

    return ChatResponse(
        response=result["response"],
        conversation_id=str(conv_id),
        actions_taken=[
            ChatAction(tool=a["tool"], result=a["result"])
            for a in result["actions_taken"]
        ],
    )
