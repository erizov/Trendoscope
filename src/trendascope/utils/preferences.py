"""
User preferences storage and management.
Saves user preferences for model, quality, translation, etc.
"""
import os
import json
from typing import Dict, Optional
from pathlib import Path


PREFERENCES_FILE = Path.home() / ".trendoscope_preferences.json"


def get_preferences() -> Dict:
    """
    Get user preferences.
    
    Returns:
        Dictionary with user preferences
    """
    default_prefs = {
        "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        "quality": "standard",
        "translate": True,
        "provider": "openai",
        "temperature": 0.8,
    }
    
    try:
        if PREFERENCES_FILE.exists():
            with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                saved_prefs = json.load(f)
                default_prefs.update(saved_prefs)
    except Exception:
        pass
    
    return default_prefs


def save_preferences(preferences: Dict) -> None:
    """
    Save user preferences.
    
    Args:
        preferences: Dictionary with preferences to save
    """
    try:
        # Load existing preferences
        current = get_preferences()
        # Update with new preferences
        current.update(preferences)
        # Save
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_preference(key: str, default: any = None) -> any:
    """
    Get a specific preference.
    
    Args:
        key: Preference key
        default: Default value if not found
        
    Returns:
        Preference value or default
    """
    prefs = get_preferences()
    return prefs.get(key, default)

