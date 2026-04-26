import httpx
import json
from app.core.config import settings

def generate_chat_response(system_prompt: str, chat_history: list, user_message: str) -> str:
    """
    Generate a response using local Ollama given a system prompt, chat history, and new user message.
    """
    if not settings.OLLAMA_BASE_URL:
        # Fallback safeguard in case .env breaks so UI testing doesn't fail
        return f"[MOCK AI RESPONSE - Configured Ollama safely, but OLLAMA_BASE_URL is missing]\n\nI am Dekho. Based on your inputs, I received: {user_message}"
    
    # 1. Format the messages
    messages = [{"role": "system", "content": system_prompt}]
    
    # Map chat history safely mapping standard attributes
    for msg in chat_history:
        # Extract purely the role and text content
        role = msg.role if hasattr(msg, 'role') else msg.get("role", "user")
        content = msg.content if hasattr(msg, 'content') else msg.get("content", "")
        
        # skip system messages or errors mapping from UI
        if not content or role not in ["user", "assistant"]:
            continue
            
        messages.append({"role": role, "content": content})
        
    messages.append({"role": "user", "content": user_message})
    
    # 2. Build the Ollama Payload
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3 # Grounded, consistent answers for finance
        }
    }
    
    # 3. Call local Ollama via httpx
    try:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
            json=payload,
            timeout=120.0
        )
        response.raise_for_status()
        data = response.json()
        
        return data.get("message", {}).get("content", "I am sorry, something went wrong formatting the Ollama generation.")
        
    except httpx.HTTPStatusError as e:
        return f"[HTTP {e.response.status_code}] Ollama rejected the request. Details: {e.response.text}"
    except httpx.ConnectError:
        return "[Connection Error] Cannot reach Ollama. Please ensure Ollama is installed and running on localhost:11434 with your selected model."
    except Exception as e:
        return f"[Error] An issue occurred calling Ollama: {str(e)}"
