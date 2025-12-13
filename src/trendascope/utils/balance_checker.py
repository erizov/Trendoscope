"""
Check AI provider balance and auto-fallback to demo mode.
"""
import os
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def check_openai_balance() -> Tuple[bool, Optional[str]]:
    """
    Check if OpenAI API has balance/credits.
    Uses API key existence as primary check, avoids making actual calls.
    
    Returns:
        Tuple of (has_balance, error_message)
    """
    try:
        # First check if API key exists
        try:
            from ..config import OPENAI_API_KEY
        except ImportError:
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        if not OPENAI_API_KEY:
            logger.warning("openai_no_api_key")
            return False, "No OpenAI API key configured"
        
        # If API key exists, assume balance exists
        # We'll catch balance errors when making actual calls
        # This avoids making unnecessary test calls that cost money
        return True, None
            
    except Exception as e:
        logger.error(f"balance_check_error: {str(e)}")
        # If we can't check, assume no balance to be safe
        return False, f"Could not check balance: {str(e)}"


def check_anthropic_balance() -> Tuple[bool, Optional[str]]:
    """
    Check if Anthropic API has balance/credits.
    Uses API key existence as primary check, avoids making actual calls.
    
    Returns:
        Tuple of (has_balance, error_message)
    """
    try:
        # First check if API key exists
        try:
            from ..config import ANTHROPIC_API_KEY
        except ImportError:
            ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        
        if not ANTHROPIC_API_KEY:
            logger.warning("anthropic_no_api_key")
            return False, "No Anthropic API key configured"
        
        # If API key exists, assume balance exists
        return True, None
            
    except Exception as e:
        logger.error(f"anthropic_check_error: {str(e)}")
        return False, f"Could not check balance: {str(e)}"


def check_provider_balance(provider: str) -> Tuple[bool, Optional[str]]:
    """
    Check balance for a provider.
    
    Args:
        provider: Provider name (openai, anthropic, etc.)
        
    Returns:
        Tuple of (has_balance, error_message)
    """
    if provider == "openai":
        return check_openai_balance()
    elif provider == "anthropic":
        return check_anthropic_balance()
    elif provider == "demo":
        return True, None  # Demo always works
    else:
        # Unknown provider - assume no balance
        return False, f"Unknown provider: {provider}"


def auto_fallback_provider(requested_provider: str) -> str:
    """
    Auto-fallback to demo if provider has no balance.
    
    Args:
        requested_provider: Requested provider
        
    Returns:
        Provider to use (may be demo if balance check fails)
    """
    if requested_provider == "demo":
        return "demo"
    
    has_balance, error = check_provider_balance(requested_provider)
    
    if not has_balance:
        logger.info(
            f"auto_fallback_to_demo: requested={requested_provider}, reason={error}"
        )
        return "demo"
    
    return requested_provider

