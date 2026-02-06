"""
Disciples - Interfaces to Child Quality Systems
================================================

Shi Fu observes his two disciples:
- Feng Shui (风水): Code architecture quality
- Gu Wu (顾武): Test discipline excellence

These interfaces allow Shi Fu to read from both systems without
modifying their internals (loose coupling, dependency inversion).
"""

from .fengshui_interface import FengShuiInterface
from .guwu_interface import GuWuInterface

__all__ = ["FengShuiInterface", "GuWuInterface"]