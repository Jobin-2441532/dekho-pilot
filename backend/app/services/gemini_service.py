from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.config import settings

def generate_chat_response(system_prompt: str, chat_history: List[BaseModel], latest_message: str) -> str:
    """
    Generates a response from Gemini using the structured RAG context.
    """
    if not settings.GEMINI_API_KEY:
        return "[Connection Error] Gemini API Key is missing. Please set it in .env."

    try:
        # Initialize the official recommended GenAI client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Build contents from history
        contents = []
        for msg in chat_history:
            # Gemini roles are typically "user" and "model"
            role = "model" if msg.role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )
            
        # Append the final user message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=latest_message)]
            )
        )
        
        # Call Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
        )
        
        return response.text if response.text else "Sorry, I am out of words."

    except Exception as e:
        return f"[Error] Gemini API Error: {str(e)}"
