"""
Gu Wu (顾武) Testing Framework - Self-Healing Test Optimization Engine

Philosophy:
    "Attending to martial affairs with discipline and continuous improvement"
    
    Like a martial arts master who continuously refines technique through practice
    and reflection, Gu Wu learns from every test execution to optimize the testing
    process autonomously.

Core Principles:
    1. Self-Learning: Learn from test patterns, failures, and performance
    2. Self-Healing: Auto-detect and suggest fixes for flaky/slow tests
    3. Self-Prioritizing: Reorder tests based on failure probability
    4. Self-Optimizing: Continuously improve test execution efficiency

Parallel to Feng Shui:
    - Feng Shui: Auto-corrects CODE organization
    - Gu Wu: Auto-optimizes TEST execution
    
Both embody the principle of continuous, autonomous improvement.
"""

__version__ = "1.0.0"
__author__ = "P2P Data Products Team"

from .engine import GuWuEngine
from .metrics import MetricsCollector
from .optimizer import TestOptimizer
from .insights import InsightsGenerator

__all__ = [
    'GuWuEngine',
    'MetricsCollector',
    'TestOptimizer',
    'InsightsGenerator'
]