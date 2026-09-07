"""
app/llm/client.py
Shared OpenAI LLM Client with .env loading and retry logic.
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from the workspace root (two levels up from this file: app/llm/ -> app/ -> root)
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)


def _get_client() -> OpenAI:
    """Returns a configured OpenAI client using OPENAI_API_KEY from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file: OPENAI_API_KEY=\"sk-...\"  "
            f"(looked for .env at: {_env_path})"
        )
    return OpenAI(api_key=api_key)


import time
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 2048,
    retries: int = 3,
    backoff_factor: float = 1.5,
) -> str:
    """
    Sends a chat completion request to OpenAI with exponential backoff retries.
    """
    client = _get_client()
    last_exception = None

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                sleep_time = backoff_factor ** attempt
                time.sleep(sleep_time)

    if last_exception:
        raise last_exception
    return ""


def chat_completion_structured(
    system_prompt: str,
    user_prompt: str,
    schema: Type[T],
    model: str = "gpt-4o-mini",
    retries: int = 3
) -> T:
    """
    Executes completion and validates the output against a Pydantic schema.
    """
    import json
    raw = chat_completion(system_prompt, user_prompt, model=model, retries=retries)
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

    parsed_json = json.loads(text)
    return schema.model_validate(parsed_json)


def is_llm_available() -> bool:
    """Returns True if a valid OPENAI_API_KEY is configured."""
    return bool(os.getenv("OPENAI_API_KEY"))
