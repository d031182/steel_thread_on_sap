"""
Shi Fu Meta-Architecture Intelligence

Phase 6: Enhancement Consultant

Shi Fu not only correlates quality (Phase 1-5), but also proposes
improvements to quality tools themselves (Phase 6).

Components:
- agent_registry.py: Documents all 6 Feng Shui agent purposes
- enhancement_proposer.py: Analyzes gaps, proposes new detectors
- architecture_observer.py: Uses Feng Shui to analyze Feng Shui!

Philosophy:
"The master teacher teaches students (Phase 1-5),
 and also teaches the tools that teach students (Phase 6)."
"""

from .agent_registry import AGENT_PURPOSES, get_agent_for_issue

__all__ = [
    'AGENT_PURPOSES',
    'get_agent_for_issue',
]