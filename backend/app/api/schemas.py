from pydantic import BaseModel
from typing import List, Optional, Literal

class SourceItem(BaseModel):
    label: str
    text: str
    type: str  # 'data' or 'knowledge'

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    id: Optional[str] = None
    timestamp: Optional[str] = None
    sources: Optional[List[SourceItem]] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    message: ChatMessage
    action_taken: Optional[bool] = False

class ChatActionRequest(BaseModel):
    action_type: Literal['ADD_GOAL', 'ADD_TO_GOAL']
    goal_name: str
    amount: float

class ChatActionResponse(BaseModel):
    success: bool
    message: str
    goal_id: Optional[int] = None
