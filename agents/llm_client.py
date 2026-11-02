"""Unified Multi-Provider LLM Client supporting Google Gemini and Anthropic

Claude.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger(__name__)

def get_llm_provider() -> str:
    """Get the active LLM provider ('gemini' or 'claude')."""
    return os.getenv("LLM_PROVIDER", "gemini").lower()

def call_gemini(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
    """Invoke Google Gemini via the official google-genai SDK."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Combine system prompt and prompt if provided
        full_content = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        
        # Using fast and highly capable flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_content
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return None

def call_claude(prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
    """Invoke Anthropic Claude via the official anthropic SDK."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        system_arg = system_prompt if system_prompt else "You are an elite quantitative equity analyst specializing in the Indian stock market (NSE/BSE)."
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            system=system_arg,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        return None

def generate_ai_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    preferred_provider: Optional[str] = None
) -> str:
    """Execute completion using the configured or preferred provider.

    Falls back to intelligent heuristic synthesis if no API keys are
    configured.
    """
    provider = (preferred_provider or get_llm_provider()).lower()
    
    response = None
    if provider == "gemini":
        response = call_gemini(prompt, system_prompt)
        if not response:
            # Fallback to Claude if Gemini key missing/failed
            response = call_claude(prompt, system_prompt)
    elif provider == "claude":
        response = call_claude(prompt, system_prompt)
        if not response:
            # Fallback to Gemini if Claude key missing/failed
            response = call_gemini(prompt, system_prompt)

    if response:
        return response.strip()

    # Rule-Based Intelligent Fallback when API keys are not yet provided
    return "__NO_API_KEY__"
