"""
Strategy Manager for Feng Shui ReAct Agent

Manages strategy selection and switching based on performance.
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class Strategy(Enum):
    """Available improvement strategies"""
    AGGRESSIVE = "aggressive"  # Fix all issues immediately
    CONSERVATIVE = "conservative"  # Fix one at a time, verify each
    TARGETED = "targeted"  # Fix only critical issues
    EXPERIMENTAL = "experimental"  # Try new approaches


@dataclass
class StrategyConfig:
    """Configuration for a specific strategy"""
    batch_size: int
    verify_each: bool
    risk_tolerance: str  # LOW/MEDIUM/HIGH
    description: str


class StrategyManager:
    """Manage and switch between improvement strategies"""
    
    STRATEGY_CONFIGS = {
        Strategy.CONSERVATIVE: StrategyConfig(
            batch_size=1,
            verify_each=True,
            risk_tolerance='LOW',
            description="Fix one issue at a time with verification"
        ),
        Strategy.AGGRESSIVE: StrategyConfig(
            batch_size=10,
            verify_each=False,
            risk_tolerance='HIGH',
            description="Fix multiple issues quickly without individual verification"
        ),
        Strategy.TARGETED: StrategyConfig(
            batch_size=3,
            verify_each=True,
            risk_tolerance='MEDIUM',
            description="Focus on critical issues only"
        ),
        Strategy.EXPERIMENTAL: StrategyConfig(
            batch_size=2,
            verify_each=True,
            risk_tolerance='MEDIUM',
            description="Try new fix approaches"
        )
    }
    
    STRATEGY_ROTATION = [
        Strategy.CONSERVATIVE,
        Strategy.AGGRESSIVE,
        Strategy.TARGETED,
        Strategy.EXPERIMENTAL
    ]
    
    def __init__(self, initial_strategy: Strategy = Strategy.CONSERVATIVE):
        """
        Initialize strategy manager
        
        Args:
            initial_strategy: Starting strategy (default: CONSERVATIVE)
        """
        self.current_strategy = initial_strategy
        self.consecutive_failures = 0
        self.strategy_history: List[Dict] = []
        self._rotation_index = self.STRATEGY_ROTATION.index(initial_strategy)
        
    def get_current_strategy(self) -> Strategy:
        """Get currently active strategy"""
        return self.current_strategy
    
    def get_strategy_config(self, strategy: Strategy = None) -> StrategyConfig:
        """
        Get configuration for specific strategy
        
        Args:
            strategy: Strategy to get config for (None = current)
            
        Returns:
            StrategyConfig with settings
        """
        if strategy is None:
            strategy = self.current_strategy
        return self.STRATEGY_CONFIGS[strategy]
    
    def should_switch_strategy(self, consecutive_failures: int = None) -> bool:
        """
        Determine if strategy should change
        
        Args:
            consecutive_failures: Failure count (None = use internal counter)
            
        Returns:
            True if should switch, False otherwise
        """
        failures = consecutive_failures if consecutive_failures is not None else self.consecutive_failures
        return failures >= 3
    
    def select_alternative_strategy(self) -> Strategy:
        """
        Choose alternative strategy using rotation
        
        Rotation: CONSERVATIVE → AGGRESSIVE → TARGETED → EXPERIMENTAL → CONSERVATIVE
        
        Returns:
            Next strategy in rotation
        """
        # Move to next strategy in rotation
        self._rotation_index = (self._rotation_index + 1) % len(self.STRATEGY_ROTATION)
        old_strategy = self.current_strategy
        self.current_strategy = self.STRATEGY_ROTATION[self._rotation_index]
        
        # Record switch
        self.strategy_history.append({
            'from': old_strategy.value,
            'to': self.current_strategy.value,
            'reason': f'consecutive_failures={self.consecutive_failures}'
        })
        
        # Reset failure counter on switch
        self.consecutive_failures = 0
        
        return self.current_strategy
    
    def record_result(self, success: bool):
        """
        Record fix result and update failure counter
        
        Args:
            success: Whether fix was successful
        """
        if success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
    
    def get_history(self) -> List[Dict]:
        """Get strategy switch history"""
        return self.strategy_history.copy()
    
    def reset(self):
        """Reset to initial state"""
        self.current_strategy = Strategy.CONSERVATIVE
        self.consecutive_failures = 0
        self.strategy_history.clear()
        self._rotation_index = 0