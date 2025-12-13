"""
Check AI provider balance and auto-fallback to demo mode.
"""
import os
from typing import Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


def check_openai_balance() -> Tuple[bool, Optional[str]]:
    """
    Check if OpenAI API has balance/credits.
    
    Returns:
        Tuple of (has_balance, error_message)
    """
    try:
        from ..gen.llm.providers import call_openai
        
        # Try a minimal test call to check balance
        # Use a very cheap model and minimal tokens
        try:
            test_response = call_openai(
                prompt="test",
                model="gpt-3.5-turbo",
                max_tokens=5
            )
            return True, None
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for common balance/credit errors
            if any(keyword in error_msg for keyword in [
                'insufficient_quota',
                'insufficient funds',
                'billing',
                'payment',
                'credit',
                'balance',
                'quota',
                'rate limit exceeded'  # Sometimes rate limit means no credits
            ]):
                logger.warning("openai_no_balance", extra={"error": str(e)})
                return False, "No OpenAI balance/credits available"
            
            # Other errors (network, etc.) - assume balance exists but call failed
            logger.warning("openai_check_failed", extra={"error": str(e)})
            return True, None  # Assume balance exists, just connection issue
            
    except Exception as e:
        logger.error("balance_check_error", extra={"error": str(e)})
        # If we can't check, assume no balance to be safe
        return False, f"Could not check balance: {str(e)}"


def check_anthropic_balance() -> Tuple[bool, Optional[str]]:
    """
    Check if Anthropic API has balance/credits.
    
    Returns:
        Tuple of (has_balance, error_message)
    """
    try:
        from ..gen.llm.providers import call_anthropic_api
        
        # Try a minimal test call
        try:
            test_response = call_anthropic_api(
                prompt="test",
                model="claude-3-haiku-20240307",
                max_tokens=5
            )
            return True, None
        except Exception as e:
            error_msg = str(e).lower()
            
            if any(keyword in error_msg for keyword in [
                'insufficient_quota',
                'insufficient funds',
                'billing',
                'payment',
                'credit',
                'balance',
                'quota'
            ]):
                logger.warning("anthropic_no_balance", extra={"error": str(e)})
                return False, "No Anthropic balance/credits available"
            
            return True, None
            
    except Exception as e:
        logger.error("anthropic_check_error", extra={"error": str(e)})
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
            "auto_fallback_to_demo",
            extra={
                "requested": requested_provider,
                "reason": error
            }
        )
        return "demo"
    
    return requested_provider

