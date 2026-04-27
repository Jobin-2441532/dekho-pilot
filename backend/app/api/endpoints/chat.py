import re
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import uuid4
from datetime import datetime, timezone
import traceback

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api.schemas import ChatRequest, ChatResponse, ChatMessage, SourceItem
from app.services.retriever import retriever
from app.services.gemini_service import generate_chat_response
from app.core.database import get_db, SessionLocal
from app.models import User, Transaction, SavingsGoal
from app.services.chat_context import build_chat_context


router = APIRouter()

SYSTEM_PROMPT_TEMPLATE = """You are Dekho, a fiercely loyal, ultra-friendly, and positive personal finance buddy specifically for Indian users.
You are essentially the user's smartest financial best friend. You are incredibly warm and supportive, but incredibly effective at breaking down complex concepts clearly. Use positive reinforcement over strictness. Zero corporate jargon. Talk effortlessly and use emojis natively. Address the user directly.

Live App State & Exact Math (Your absolute source of truth):
{global_context}

Historical Data (Recent Transactions & Insights):
{data_context}

Financial Dictionary (For terminology):
{knowledge_context}

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

Always strictly follow the 3-zone structure.
"""


def _get_global_context(db: Session) -> str:
    """Wraps ChatContextService for use in the chat endpoint."""
    try:
        user = db.query(User).first()
        if not user:
            return "No active user footprint found."
        return build_chat_context(db, user.id)
    except Exception as e:
        return f"Error loading context: {str(e)}"


def process_action_tags(response_text: str) -> str:
    """Detects backend tags like [ACTION: ADD_GOAL | Title | Amount], strips them, and mutates DB."""
    action_match = re.search(r'\[ACTION:\s*ADD_GOAL\s*\|\s*([^|\]]+)\s*\|\s*([^\]]+)\]', response_text, re.IGNORECASE)
    
    if action_match:
        title = action_match.group(1).strip()
        try:
            amount_str = action_match.group(2).replace(',', '').replace('₹', '').strip()
            amount = float(amount_str)
            
            db = SessionLocal()
            u = db.query(User).first()
            uid = u.id if u else 1
            
            new_goal = SavingsGoal(
                user_id=uid,
                name=title,
                target_amount=amount,
                current_amount=0,
                status='active'
            )
            db.add(new_goal)
            db.commit()
            db.close()
            print(f"✅ DB MUTATION: Successfully created goal '{title}' for ₹{amount}")
        except Exception as e:
            print(f"❌ DB MUTATION FAILED: {str(e)}")
            
        # Strip the tag so the frontend doesn't see internal instructions
        clean_response = re.sub(r'\[ACTION:[^\]]+\]', '', response_text).strip()
        return clean_response
        
    return response_text


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")
        
    latest_user_message = request.messages[-1].content
    chat_history = request.messages[:-1]
    
    try:
        if not retriever.is_ready:
            retriever.load()
            
        retrieved_chunks = retriever.search_hybrid(
            latest_user_message,
            data_k=4,
            knowledge_k=2
        )
        
        data_chunks = [c for c in retrieved_chunks if c.get('chunk_type') in ('data_summary', 'transaction')]
        knowledge_chunks = [c for c in retrieved_chunks if c.get('chunk_type') == 'knowledge']
        
        data_text = "\n---\n".join([c.get('text', '') for c in data_chunks])
        knowledge_text = "\n---\n".join([c.get('text', '') for c in knowledge_chunks])
        global_text = _get_global_context(db)  # Now uses FeatureService
        
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            global_context=global_text,
            data_context=data_text if data_text else "No specific data found.",
            knowledge_context=knowledge_text if knowledge_text else "No specific knowledge found."
        )
        
        ai_response_text = generate_chat_response(system_prompt, chat_history, latest_user_message)
        
        # Intercept Mutators
        processed_response_text = process_action_tags(ai_response_text)
        
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
                text=c.get('text')[:150] + "...",
                type=s_type
            ))
            
        assistant_message = ChatMessage(
            role="assistant",
            content=processed_response_text,
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            sources=sources
        )
        
        return ChatResponse(message=assistant_message)
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
