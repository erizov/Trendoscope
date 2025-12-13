"""
Style learning system.
Learns from user edits and refines style over time.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class StyleLearner:
    """Learns and refines writing style from edits."""
    
    def __init__(self, storage_path: str = "data/style_learning"):
        """
        Initialize style learner.
        
        Args:
            storage_path: Path to store learning data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.edit_history: List[Dict[str, Any]] = []
        self.style_patterns: Dict[str, Any] = {}
        self._load_data()
    
    def record_edit(
        self,
        original: Dict[str, Any],
        edited: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Record a user edit to learn from.
        
        Args:
            original: Original post
            edited: Edited post
            user_id: Optional user identifier
        """
        edit_record = {
            'timestamp': datetime.now().isoformat(),
            'original_title': original.get('title', ''),
            'edited_title': edited.get('title', ''),
            'original_text': original.get('text', ''),
            'edited_text': edited.get('text', ''),
            'user_id': user_id,
            'changes': self._analyze_changes(original, edited)
        }
        
        self.edit_history.append(edit_record)
        self._update_style_patterns(edit_record)
        self._save_data()
    
    def _analyze_changes(
        self,
        original: Dict[str, Any],
        edited: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze what changed between original and edited."""
        changes = {
            'title_changed': original.get('title') != edited.get('title'),
            'text_changed': original.get('text') != edited.get('text'),
            'length_change': len(edited.get('text', '')) - len(original.get('text', '')),
            'tone_changes': [],
            'style_changes': []
        }
        
        # Simple analysis (in production, would use NLP)
        original_text = original.get('text', '').lower()
        edited_text = edited.get('text', '').lower()
        
        # Check for tone indicators
        formal_words = ['следует', 'необходимо', 'требуется']
        informal_words = ['нужно', 'надо', 'можно']
        
        if any(word in edited_text for word in formal_words):
            if not any(word in original_text for word in formal_words):
                changes['tone_changes'].append('more_formal')
        
        if any(word in edited_text for word in informal_words):
            if not any(word in original_text for word in informal_words):
                changes['tone_changes'].append('more_informal')
        
        return changes
    
    def _update_style_patterns(self, edit_record: Dict[str, Any]):
        """Update learned style patterns from edit."""
        changes = edit_record.get('changes', {})
        
        # Track common changes
        if changes.get('tone_changes'):
            for tone_change in changes['tone_changes']:
                if 'tone_preferences' not in self.style_patterns:
                    self.style_patterns['tone_preferences'] = defaultdict(int)
                self.style_patterns['tone_preferences'][tone_change] += 1
        
        # Track length preferences
        length_change = changes.get('length_change', 0)
        if 'length_preferences' not in self.style_patterns:
            self.style_patterns['length_preferences'] = []
        self.style_patterns['length_preferences'].append(length_change)
        
        # Keep only recent preferences
        if len(self.style_patterns['length_preferences']) > 100:
            self.style_patterns['length_preferences'] = \
                self.style_patterns['length_preferences'][-100:]
    
    def get_learned_preferences(self) -> Dict[str, Any]:
        """
        Get learned style preferences.
        
        Returns:
            Dictionary with learned preferences
        """
        preferences = {
            'tone': 'neutral',
            'preferred_length': 'medium',
            'common_changes': []
        }
        
        # Determine preferred tone
        tone_prefs = self.style_patterns.get('tone_preferences', {})
        if tone_prefs:
            preferred_tone = max(tone_prefs.items(), key=lambda x: x[1])[0]
            if 'more_formal' in preferred_tone:
                preferences['tone'] = 'formal'
            elif 'more_informal' in preferred_tone:
                preferences['tone'] = 'informal'
        
        # Determine preferred length
        length_prefs = self.style_patterns.get('length_preferences', [])
        if length_prefs:
            avg_change = sum(length_prefs) / len(length_prefs)
            if avg_change > 200:
                preferences['preferred_length'] = 'long'
            elif avg_change < -200:
                preferences['preferred_length'] = 'short'
        
        return preferences
    
    def apply_learned_style(
        self,
        post: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply learned style preferences to a post.
        
        Args:
            post: Post to style
            
        Returns:
            Styled post
        """
        preferences = self.get_learned_preferences()
        
        # Apply tone if learned
        if preferences['tone'] != 'neutral':
            # In production, would use LLM to adjust tone
            # For now, just return original
            pass
        
        # Apply length preference
        text = post.get('text', '')
        preferred_length = preferences['preferred_length']
        
        if preferred_length == 'short' and len(text) > 1000:
            # Truncate (in production, would summarize)
            post['text'] = text[:1000] + "..."
        elif preferred_length == 'long' and len(text) < 500:
            # Expand (in production, would use LLM)
            pass
        
        return post
    
    def _load_data(self):
        """Load learning data from disk."""
        data_file = self.storage_path / "style_learning.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.edit_history = data.get('edit_history', [])
                    self.style_patterns = data.get('style_patterns', {})
            except Exception as e:
                logger.error(f"Error loading style learning data: {e}")
    
    def _save_data(self):
        """Save learning data to disk."""
        data_file = self.storage_path / "style_learning.json"
        try:
            data = {
                'edit_history': self.edit_history[-1000:],  # Keep last 1000 edits
                'style_patterns': self.style_patterns,
                'last_updated': datetime.now().isoformat()
            }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving style learning data: {e}")


# Global style learner instance
_style_learner: Optional[StyleLearner] = None


def get_style_learner() -> StyleLearner:
    """Get global style learner instance."""
    global _style_learner
    if _style_learner is None:
        _style_learner = StyleLearner()
    return _style_learner

