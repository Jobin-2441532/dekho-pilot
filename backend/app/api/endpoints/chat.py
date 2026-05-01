"""
chat.py
-------
Dekho AI Chatbot endpoint — powered by Gemini + FAISS RAG.

Phase E changes:
  1. JWT isolation — all DB queries scoped to current_user.id (was already done)
  2. Fixed process_action_tags — reuses the request Session instead of leaking a new SessionLocal()
  3. ML pattern injection — calls the financeAI sidecar to get the user's spending archetype
     and injects it into the system prompt so Gemini gives personalised advice
  4. Simple /chat/message endpoint — accepts { message } body from the Home page mini-chat,
     wraps it into the full messages format transparently
"""

import re
import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, timezone
import traceback

import httpx
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api.schemas import ChatRequest, ChatResponse, ChatMessage, SourceItem
from app.services.retriever import retriever
from app.services.gemini_service import generate_chat_response
from app.core.database import get_db
from app.models import User, Transaction, SavingsGoal
from app.services.chat_context import build_chat_context
from app.api.endpoints.auth import get_current_user

logger = logging.getLogger("dekho.chat")
router = APIRouter()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")


# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_TEMPLATE = """You are Dekho, a fiercely loyal, ultra-friendly, and positive personal finance buddy specifically for Indian users.
You are essentially the user's smartest financial best friend. You are incredibly warm and supportive, but incredibly effective at breaking down complex concepts clearly. Use positive reinforcement over strictness. Zero corporate jargon. Talk effortlessly and use emojis natively. Address the user directly.

Live App State & Exact Math (Your absolute source of truth):
{global_context}

Historical Data (Recent Transactions & Insights):
{data_context}

Financial Dictionary (For terminology):
{knowledge_context}

{ml_pattern_section}

Guidelines:
1. Persona: A warm, deeply supportive best friend who happens to be a financial genius. You guide effortlessly without ever sounding manipulative or strict.
2. Structure: Break your answer into three distinct zones:
   - Friendly Vibe Check: Start with an empathetic reaction to their question.
   - The Hard Numbers: Use exact math from the "Live App State". Display a beautiful chart using UI tags.
   - The Playbook: Give one clear, highly-actionable next step.
3. Indian Regulatory Guardrails (SEBI/RBI): YOU ARE NOT A SEBI REGISTERED INVESTMENT ADVISOR (RIA). You must NEVER give specific stock recommendations or mutual fund buying advice. Provide only conceptual, educational guidance (e.g. explaining what index funds are) and clearly state that this is for educational purposes.
4. Database Actions: YOU HAVE THE POWER TO UPDATE THE DATABASE!
   If the user asks you to create or set a savings goal, you MUST append this EXACT hidden system tag on a new line at the very end of your response:
   [ACTION: ADD_GOAL | <Goal Title> | <Target Amount>]
5. Graphical Visualizations (Recharts integration):
   [UI: PROGRESS | <Goal Title> | <Current> | <Target>]
   [UI: METRIC | <Metric Name> | <Value>]
   If asked for a chart, fraction, pie, or visual breakdown of categorical data, you MUST use either Bar or Pie chart tags:
   [UI: CHART | Bar | <Chart Title> | <Label1>:<Value1>, <Label2>:<Value2>]
   [UI: CHART | Pie | <Chart Title> | <Label1>:<Value1>, <Label2>:<Value2>]
   (Example: [UI: CHART | Pie | Monthly Distribution | Rent:18000, Shopping:6385, Health:3183])
6. Indian Context: Always use ₹, Lakhs, Crores format.
7. Spending Pattern Awareness: If the ML pattern section above is populated, use it to personalise your advice. For example, if the user is an "impulsive spender", acknowledge that gently and give targeted tips. If "controlled", affirm their good habits.

Always strictly follow the 3-zone structure.
"""

ML_PATTERN_SECTION_TEMPLATE = """ML Spending Pattern Analysis (Use to personalise advice):
  Spending Archetype : {primary_pattern}
  Emotional Trigger  : {emotional_trigger}
  Peak Spend Time    : {peak_spend_time}
  Weekend Spender    : {spends_more_on_weekends}
  Impulse Categories : {impulse_categories}
  Controlled Cats    : {controlled_categories}
  Intentional Ratio  : {intentional_ratio:.0%}
"""


# ---------------------------------------------------------------------------
# ML pattern fetch — non-blocking, graceful fallback
# ---------------------------------------------------------------------------
async def _fetch_ml_pattern(user_id: int) -> Optional[dict]:
    """
    Fetch ML spending pattern from the financeAI sidecar.
    Returns None if sidecar is unavailable — prompt gracefully degrades.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{ML_SERVICE_URL}/api/users/ml/pattern/{user_id}")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return None


def _build_ml_section(pattern: Optional[dict]) -> str:
    """Format the ML pattern into the prompt section, or empty string if unavailable."""
    if not pattern:
        return ""
    try:
        return ML_PATTERN_SECTION_TEMPLATE.format(
            primary_pattern=pattern.get("primary_pattern", "unknown").replace("_", " ").title(),
            emotional_trigger=pattern.get("emotional_trigger", "none").replace("_", " ").title(),
            peak_spend_time=pattern.get("peak_spend_time", "unknown"),
            spends_more_on_weekends="Yes" if pattern.get("spends_more_on_weekends") else "No",
            impulse_categories=", ".join(pattern.get("impulse_categories", [])) or "None",
            controlled_categories=", ".join(pattern.get("controlled_categories", [])) or "None",
            intentional_ratio=float(pattern.get("intentional_ratio", 0.5)),
        )
    except Exception as e:
        logger.warning(f"ML pattern formatting failed: {e}")
        return ""


# ---------------------------------------------------------------------------
# Action tag processor — uses the injected DB session (no leak)
# ---------------------------------------------------------------------------
def process_action_tags(response_text: str, user_id: int, db: Session) -> str:
    """
    Detects [ACTION: ADD_GOAL | Title | Amount] tags, creates the DB record,
    and strips the tag so the frontend never sees internal instructions.

    Phase E fix: uses the injected `db` session instead of opening a new
    SessionLocal() which would leak connections.
    """
    action_match = re.search(
        r'\[ACTION:\s*ADD_GOAL\s*\|\s*([^|\]]+)\s*\|\s*([^\]]+)\]',
        response_text,
        re.IGNORECASE,
    )

    if action_match:
        title = action_match.group(1).strip()
        try:
            amount_str = action_match.group(2).replace(',', '').replace('₹', '').strip()
            amount = float(amount_str)

            new_goal = SavingsGoal(
                user_id=user_id,
                name=title,
                target_amount=amount,
                current_amount=0,
                status='active',
            )
            db.add(new_goal)
            db.commit()
            logger.info(f"✅ Goal created via chat: '{title}' ₹{amount:,.0f} for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Goal creation failed: {e}")

        # Strip the hidden tag from the response
        return re.sub(r'\[ACTION:[^\]]+\]', '', response_text).strip()

    return response_text


# ---------------------------------------------------------------------------
# Helper: build the full prompt context
# ---------------------------------------------------------------------------
def _get_global_context(db: Session, user_id: int) -> str:
    try:
        return build_chat_context(db, user_id)
    except Exception as e:
        logger.warning(f"build_chat_context failed: {e}")
        return "Error loading financial context."


# ---------------------------------------------------------------------------
# POST /chat  — full messages array (used by /ask page)
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full chat endpoint — accepts a messages array with full conversation history.
    Used by the /ask (dedicated chat) page.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    latest_user_message = request.messages[-1].content
    chat_history = request.messages[:-1]

    return await _process_chat(
        user_message=latest_user_message,
        chat_history=chat_history,
        db=db,
        current_user=current_user,
    )


# ---------------------------------------------------------------------------
# POST /chat/message  — simple { message } body (used by Home mini-chat)
# ---------------------------------------------------------------------------
from pydantic import BaseModel

class SimpleMessageRequest(BaseModel):
    message: str

@router.post("/chat/message")
async def simple_chat_endpoint(
    request: SimpleMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simplified single-message endpoint for the Home page mini-chat.
    Returns { reply: "..." } instead of the full ChatResponse schema.
    """
    response = await _process_chat(
        user_message=request.message,
        chat_history=[],
        db=db,
        current_user=current_user,
    )
    return {"reply": response.message.content}


# ---------------------------------------------------------------------------
# Core logic — shared by both endpoints
# ---------------------------------------------------------------------------
async def _process_chat(
    user_message: str,
    chat_history: list,
    db: Session,
    current_user: User,
) -> ChatResponse:
    try:
        # 1. FAISS RAG retrieval
        if not retriever.is_ready:
            retriever.load()

        retrieved_chunks = retriever.search_hybrid(
            user_message,
            data_k=4,
            knowledge_k=2,
        )

        data_chunks = [c for c in retrieved_chunks if c.get('chunk_type') in ('data_summary', 'transaction')]
        knowledge_chunks = [c for c in retrieved_chunks if c.get('chunk_type') == 'knowledge']

        data_text = "\n---\n".join([c.get('text', '') for c in data_chunks])
        knowledge_text = "\n---\n".join([c.get('text', '') for c in knowledge_chunks])

        # 2. Global financial context (JWT-scoped via current_user.id)
        global_text = _get_global_context(db, current_user.id)

        # 3. ML pattern injection (non-blocking — graceful if sidecar is offline)
        ml_pattern = await _fetch_ml_pattern(current_user.id)
        ml_section = _build_ml_section(ml_pattern)

        # 4. Build system prompt with ML context injected
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            global_context=global_text,
            data_context=data_text if data_text else "No specific data found.",
            knowledge_context=knowledge_text if knowledge_text else "No specific knowledge found.",
            ml_pattern_section=ml_section,
        )

        # 5. Generate response via Gemini
        ai_response_text = generate_chat_response(system_prompt, chat_history, user_message)

        # 6. Process action tags — uses injected db session (Phase E fix: no connection leak)
        processed_response_text = process_action_tags(ai_response_text, current_user.id, db)

        # 7. Build source citations
        sources = []
        for c in retrieved_chunks:
            if c.get("chunk_type") == "knowledge":
                label = f"Article: {c.get('source', '').replace('.md', '').replace('_', ' ').title()}"
                s_type = "knowledge"
            elif c.get("chunk_type") == "data_summary":
                cat = c.get("category", "")
                label = f"Data Summary ({cat.title()})" if cat else "Data Summary"
                s_type = "data"
            else:
                label = "Recent Transaction"
                s_type = "data"

            sources.append(SourceItem(
                label=label,
                text=c.get('text', '')[:150] + "...",
                type=s_type,
            ))

        return ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=processed_response_text,
                id=str(uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                sources=sources,
            )
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
