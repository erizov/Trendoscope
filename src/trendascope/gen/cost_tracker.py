"""
Cost tracking for AI API calls.
Tracks usage and costs for OpenAI, Anthropic, and other providers.
"""
import os
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path


# Cost per 1K tokens (as of 2024)
COST_PER_1K_TOKENS = {
    "openai": {
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
    },
    "anthropic": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    }
}


class CostTracker:
    """Track AI API costs."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize cost tracker.
        
        Args:
            log_file: Optional path to JSON log file
        """
        self.costs = {
            "openai": 0.0,
            "anthropic": 0.0,
            "local": 0.0,
            "demo": 0.0,
            "total": 0.0
        }
        self.usage = {
            "openai": {"calls": 0, "tokens_in": 0, "tokens_out": 0},
            "anthropic": {"calls": 0, "tokens_in": 0, "tokens_out": 0},
            "local": {"calls": 0},
            "demo": {"calls": 0},
        }
        self.log_file = log_file or os.getenv(
            "COST_LOG_FILE",
            str(Path.home() / ".trendoscope_costs.json")
        )
        self._load_history()
    
    def _load_history(self):
        """Load cost history from file."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.costs = data.get("costs", self.costs)
                    self.usage = data.get("usage", self.usage)
        except Exception:
            pass  # Start fresh if can't load
    
    def _save_history(self):
        """Save cost history to file."""
        try:
            data = {
                "costs": self.costs,
                "usage": self.usage,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Don't fail if can't save
    
    def log_call(
        self,
        provider: str,
        model: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0
    ):
        """
        Log an API call and calculate cost.
        
        Args:
            provider: Provider name (openai, anthropic, etc.)
            model: Model name
            tokens_in: Input tokens
            tokens_out: Output tokens
        """
        # Update usage
        if provider in self.usage:
            self.usage[provider]["calls"] += 1
            if tokens_in > 0:
                self.usage[provider]["tokens_in"] += tokens_in
            if tokens_out > 0:
                self.usage[provider]["tokens_out"] += tokens_out
        
        # Calculate cost
        cost = self._calculate_cost(provider, model, tokens_in, tokens_out)
        
        if provider in self.costs:
            self.costs[provider] += cost
            self.costs["total"] += cost
        
        # Save to file
        self._save_history()
        
        return cost
    
    def _calculate_cost(
        self,
        provider: str,
        model: Optional[str],
        tokens_in: int,
        tokens_out: int
    ) -> float:
        """
        Calculate cost for API call.
        
        Args:
            provider: Provider name
            model: Model name
            tokens_in: Input tokens
            tokens_out: Output tokens
            
        Returns:
            Cost in USD
        """
        if provider not in COST_PER_1K_TOKENS:
            return 0.0
        
        if not model or model not in COST_PER_1K_TOKENS[provider]:
            # Use default/cheapest model for provider
            if provider == "openai":
                rates = COST_PER_1K_TOKENS["openai"]["gpt-3.5-turbo"]
            elif provider == "anthropic":
                rates = COST_PER_1K_TOKENS["anthropic"]["claude-3-haiku-20240307"]
            else:
                return 0.0
        else:
            rates = COST_PER_1K_TOKENS[provider][model]
        
        cost = (
            (tokens_in / 1000) * rates["input"] +
            (tokens_out / 1000) * rates["output"]
        )
        
        return round(cost, 6)
    
    def get_summary(self) -> Dict:
        """
        Get cost summary.
        
        Returns:
            Dictionary with costs and usage
        """
        return {
            "costs": self.costs.copy(),
            "usage": self.usage.copy(),
            "cost_per_call": {
                provider: (
                    self.costs[provider] / max(1, self.usage[provider]["calls"])
                    if self.usage[provider]["calls"] > 0 else 0.0
                )
                for provider in self.costs
                if provider != "total"
            }
        }
    
    def reset(self):
        """Reset all costs and usage."""
        self.costs = {k: 0.0 for k in self.costs}
        self.usage = {
            k: {"calls": 0, "tokens_in": 0, "tokens_out": 0}
            for k in self.usage
        }
        self._save_history()


# Global tracker instance
_tracker = None


def get_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker


def track_call(
    provider: str,
    model: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0
) -> float:
    """
    Track an API call (convenience function).
    
    Args:
        provider: Provider name
        model: Model name
        tokens_in: Input tokens
        tokens_out: Output tokens
        
    Returns:
        Cost in USD
    """
    return get_tracker().log_call(provider, model, tokens_in, tokens_out)

