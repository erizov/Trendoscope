"""
LLM provider implementations.
Supports OpenAI, Anthropic, and local models.
"""
import os
import json
from typing import Optional, Dict, Any

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class LLMProviderError(Exception):
    """Exception raised for LLM provider errors."""
    pass


def call_openai(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call OpenAI API (supports proxy via base_url).

    Args:
        prompt: Input prompt
        model: Model name (default: gpt-4-turbo-preview)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    if not openai:
        raise LLMProviderError("openai package not installed")

    # Import config
    try:
        from ..config import OPENAI_API_KEY, OPENAI_API_BASE
    except ImportError:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

    if not OPENAI_API_KEY:
        raise LLMProviderError("OPENAI_API_KEY not set")

    # Use cheaper model by default (can be overridden via OPENAI_MODEL env var)
    # GPT-3.5-turbo is ~20x cheaper than GPT-4
    model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    try:
        # Create client with optional base_url
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_API_BASE:
            client_kwargs["base_url"] = OPENAI_API_BASE

        client = openai.OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по анализу трендов и генерации "
                        "контента. Отвечай строго по инструкциям."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    except Exception as e:
        raise LLMProviderError(f"OpenAI API error: {str(e)}")


def call_anthropic_api(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call Anthropic API.

    Args:
        prompt: Input prompt
        model: Model name (default: claude-3-sonnet-20240229)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    if not anthropic:
        raise LLMProviderError("anthropic package not installed")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMProviderError("ANTHROPIC_API_KEY not set")

    model = model or "claude-3-sonnet-20240229"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    except Exception as e:
        raise LLMProviderError(f"Anthropic API error: {str(e)}")


def call_local(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call local LLM via Ollama or similar.

    Args:
        prompt: Input prompt
        model: Model name (default: llama2)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    import httpx

    model = model or "llama2"
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    try:
        client = httpx.Client(timeout=120.0)
        response = client.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    except Exception as e:
        raise LLMProviderError(f"Local LLM error: {str(e)}")


def call_llm(
    provider: str,
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000  # Reduced from 4000 to save costs
) -> str:
    """
    Call LLM provider.

    Args:
        provider: Provider name (openai, anthropic, local, demo)
        prompt: Input prompt
        model: Model name (provider-specific)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If provider is invalid or call fails
    """
    if provider == "openai":
        return call_openai(prompt, model, temperature, max_tokens)
    elif provider == "anthropic":
        return call_anthropic_api(prompt, model, temperature, max_tokens)
    elif provider == "local":
        return call_local(prompt, model, temperature, max_tokens)
    elif provider == "demo":
        # Improved demo mode with template-based generation
        from ..demo_generator import (
            extract_style_from_prompt,
            extract_topic_from_prompt,
            generate_demo_post,
            generate_demo_summary,
            get_recent_news
        )
        
        # Extract style and topic from prompt
        style = extract_style_from_prompt(prompt)
        topic = extract_topic_from_prompt(prompt)
        
        # Check if post generation format
        if '"title":' in prompt and '"text":' in prompt:
            # Try to get real news for context
            news_items = get_recent_news(topic, limit=1)
            
            # Generate post using templates
            post = generate_demo_post(style, topic, news_items)
            return json.dumps(post, ensure_ascii=False)
        else:
            # Summary format
            summary = generate_demo_summary(style, topic)
            return json.dumps(summary, ensure_ascii=False)
    else:
        raise LLMProviderError(f"Unknown provider: {provider}")
