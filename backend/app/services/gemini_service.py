import asyncio
import time
import logging
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
from app.core.config import settings

logger = logging.getLogger("dekho.gemini")


def _call_gemini(client, system_prompt: str, contents: list) -> str:
    """Single Gemini API call. Raises on error."""
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,  # Lower = more consistent, grounded responses
        ),
    )
    return response.text if response.text else "I don't have a clear answer for that right now."


def generate_chat_response(system_prompt: str, chat_history: List[BaseModel], latest_message: str) -> str:
    """
    Generates a response from Gemini using the structured RAG context.
    Includes one automatic retry with a 1s delay on failure.
    """
    if not settings.GEMINI_API_KEY:
        return "There's a configuration issue on the server side. The API key is missing."

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Build conversation history
    contents = []
    for msg in chat_history:
        role = "model" if msg.role == "assistant" else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )

    # Append the latest user message
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=latest_message)]
        )
    )

    # Attempt 1
    try:
        return _call_gemini(client, system_prompt, contents)
    except Exception as e:
        logger.warning(f"Gemini attempt 1 failed: {e}. Retrying in 1s...")

    # Attempt 2 (retry after 1 second)
    time.sleep(1)
    try:
        return _call_gemini(client, system_prompt, contents)
    except Exception as e:
        logger.error(f"Gemini attempt 2 also failed: {e}")
        return "I'm having trouble connecting right now. Please try again in a moment."
