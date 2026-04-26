from pydantic import BaseModel
from typing import List, Optional

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
