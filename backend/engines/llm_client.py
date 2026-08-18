"""
LLM client for attack generation using Gemini (primary) and Groq (fallback).
Uses google-genai (new SDK) instead of deprecated google-generativeai.
"""
import asyncio
import logging
from typing import Optional
from google import genai
from google.genai import types
from groq import Groq

from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client with Gemini primary and Groq fallback."""

    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.gemini_client = None
            logger.warning("Gemini API key not configured")

        if settings.GROQ_API_KEY:
            self.groq = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.groq = None
            logger.warning("Groq API key not configured")

    def _gemini_generate_sync(self, prompt: str, temp: float, max_tokens: int) -> str:
        """Synchronous Gemini call — intended to be run via asyncio.to_thread."""
        response = self.gemini_client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text

    async def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Generate text with Gemini primary, Groq fallback."""
        temp = temperature or settings.TEMPERATURE

        if self.gemini_client:
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._gemini_generate_sync, prompt, temp,
                        max(settings.MAX_TOKENS, 8192),  # Gemini supports high token counts
                    ),
                    timeout=90,
                )
                return result
            except asyncio.TimeoutError:
                logger.warning("Gemini timed out after 90s — falling back to Groq")
            except Exception as e:
                logger.warning(f"Gemini failed: {e} — falling back to Groq")

        if self.groq:
            try:
                # Groq free tier has 8000 TPM — use conservative output limit
                groq_max = min(settings.MAX_TOKENS, 4096)
                response = await asyncio.to_thread(
                    self.groq.chat.completions.create,
                    model=settings.GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    max_tokens=groq_max,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq failed: {e}")
                raise

        raise RuntimeError("No LLM providers configured — set GEMINI_API_KEY or GROQ_API_KEY")
