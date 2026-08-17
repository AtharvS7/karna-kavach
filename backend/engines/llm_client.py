"""
LLM client for attack generation using Gemini (primary) and Groq (fallback).
"""
import os
import logging
from typing import Optional
import google.generativeai as genai
from groq import Groq

from config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client with fallback support."""

    def __init__(self):
        # Configure Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            self.gemini = None
            logger.warning("Gemini API key not configured")

        # Configure Groq
        if settings.GROQ_API_KEY:
            self.groq = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.groq = None
            logger.warning("Groq API key not configured")

    async def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """
        Generate text using LLM with automatic fallback.

        Tries Gemini first (higher quality), falls back to Groq if quota exhausted.
        """
        temp = temperature or settings.TEMPERATURE

        # Try Gemini first
        if self.gemini:
            try:
                response = self.gemini.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=temp,
                        max_output_tokens=settings.MAX_TOKENS
                    )
                )
                return response.text
            except Exception as e:
                logger.warning(f"Gemini generation failed: {e}, falling back to Groq")

        # Fallback to Groq
        if self.groq:
            try:
                response = self.groq.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    max_tokens=settings.MAX_TOKENS
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq generation failed: {e}")
                raise Exception("All LLM providers failed")

        raise Exception("No LLM providers configured")
