"""
Smart model selection based on task and quality requirements.
Optimizes cost while maintaining quality.
"""
import os
from typing import Dict, Optional


# Quality tiers with cost optimization
QUALITY_TIERS = {
    "draft": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 800,
        "temperature": 0.7,
        "cost_level": "low",
        "description": "Fast, cheap, good for drafts"
    },
    "standard": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 1500,
        "temperature": 0.8,
        "cost_level": "medium",
        "description": "Balanced quality and cost"
    },
    "premium": {
        "model": "gpt-4-turbo-preview",
        "max_tokens": 2000,
        "temperature": 0.9,
        "cost_level": "high",
        "description": "Highest quality, more expensive"
    }
}

# Task-specific model recommendations
TASK_MODELS = {
    "translation": "gpt-3.5-turbo",  # Cheaper, good enough
    "summarization": "gpt-3.5-turbo",  # Cheaper, good enough
    "filtering": "gpt-3.5-turbo",  # Cheaper, good enough
    "post_generation": None,  # Use quality tier
    "style_analysis": "gpt-3.5-turbo",  # Cheaper, good enough
}


def select_model_for_task(
    task: str,
    quality: str = "standard",
    provider: str = "openai"
) -> Dict[str, any]:
    """
    Select appropriate model and settings for a task.
    
    Args:
        task: Task type (translation, summarization, post_generation, etc.)
        quality: Quality tier (draft, standard, premium)
        provider: Provider name (openai, anthropic)
        
    Returns:
        Dictionary with model, max_tokens, temperature, cost_level
    """
    # For specific tasks, use task-specific model
    if task in TASK_MODELS and task != "post_generation":
        model = TASK_MODELS[task]
        return {
            "model": model,
            "max_tokens": 1000 if task == "translation" else 500,
            "temperature": 0.7,
            "cost_level": "low"
        }
    
    # For post generation, use quality tier
    if quality in QUALITY_TIERS:
        tier = QUALITY_TIERS[quality]
        # Allow override via env var
        model = os.getenv("OPENAI_MODEL", tier["model"])
        return {
            "model": model,
            "max_tokens": tier["max_tokens"],
            "temperature": tier["temperature"],
            "cost_level": tier["cost_level"]
        }
    
    # Default to standard
    return QUALITY_TIERS["standard"]


def get_model_cost_estimate(
    provider: str,
    model: str,
    estimated_tokens_in: int,
    estimated_tokens_out: int
) -> float:
    """
    Estimate cost for API call.
    
    Args:
        provider: Provider name
        model: Model name
        estimated_tokens_in: Estimated input tokens
        estimated_tokens_out: Estimated output tokens
        
    Returns:
        Estimated cost in USD
    """
    from .cost_tracker import COST_PER_1K_TOKENS
    
    if provider not in COST_PER_1K_TOKENS:
        return 0.0
    
    if model not in COST_PER_1K_TOKENS[provider]:
        # Use cheapest model for estimate
        if provider == "openai":
            rates = COST_PER_1K_TOKENS["openai"]["gpt-3.5-turbo"]
        else:
            return 0.0
    else:
        rates = COST_PER_1K_TOKENS[provider][model]
    
    cost = (
        (estimated_tokens_in / 1000) * rates["input"] +
        (estimated_tokens_out / 1000) * rates["output"]
    )
    
    return round(cost, 4)

