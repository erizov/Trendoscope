"""
Tests for style learning system.
"""
import pytest
from trendascope.gen.style_learning import StyleLearner, get_style_learner


def test_style_learner_record_edit():
    """Test recording edits."""
    learner = StyleLearner(storage_path="test_data/style_learning")
    
    original = {
        'title': 'Original Title',
        'text': 'Original text content'
    }
    
    edited = {
        'title': 'Edited Title',
        'text': 'Edited text content with more formal language'
    }
    
    learner.record_edit(original, edited)
    
    assert len(learner.edit_history) > 0
    assert learner.edit_history[-1]['original_title'] == 'Original Title'


def test_get_learned_preferences():
    """Test getting learned preferences."""
    learner = StyleLearner(storage_path="test_data/style_learning")
    
    # Record some edits
    for i in range(3):
        original = {'title': f'Title {i}', 'text': 'Short text'}
        edited = {'title': f'Title {i}', 'text': 'Much longer text with more details'}
        learner.record_edit(original, edited)
    
    preferences = learner.get_learned_preferences()
    
    assert 'tone' in preferences
    assert 'preferred_length' in preferences


def test_apply_learned_style():
    """Test applying learned style."""
    learner = StyleLearner(storage_path="test_data/style_learning")
    
    post = {
        'title': 'Test Post',
        'text': 'A' * 1500  # Long text
    }
    
    styled = learner.apply_learned_style(post)
    
    assert 'title' in styled
    assert 'text' in styled

