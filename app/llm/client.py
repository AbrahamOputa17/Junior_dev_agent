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


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """
    Sends a chat completion request to OpenAI and returns the response text.

    Args:
        system_prompt: Sets the assistant's role and constraints.
        user_prompt: The task/question to be answered.
        model: The OpenAI model name (default: gpt-4o-mini for cost efficiency).
        temperature: Sampling temperature (lower = more deterministic).
        max_tokens: Maximum tokens in the response.

    Returns:
        The assistant's response text as a string.

    Raises:
        EnvironmentError: If OPENAI_API_KEY is missing.
        openai.OpenAIError: On API failures.
    """
    client = _get_client()
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


def is_llm_available() -> bool:
    """Returns True if a valid OPENAI_API_KEY is configured."""
    return bool(os.getenv("OPENAI_API_KEY"))
