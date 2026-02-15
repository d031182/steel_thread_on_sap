"""
Gu Wu Pytest Plugins

Custom pytest plugins for enhanced testing experience:
- human_readable_errors: Translates cryptic errors → clear explanations
"""

# Auto-import plugins so pytest can discover them
from . import human_readable_errors

__all__ = ['human_readable_errors']