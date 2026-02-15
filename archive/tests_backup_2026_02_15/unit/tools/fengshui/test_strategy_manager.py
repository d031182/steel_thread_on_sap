"""
Unit tests for Feng Shui Strategy Manager

Tests the strategy rotation system and execution patterns.
"""

import pytest
from tools.fengshui.strategy_manager import (
    StrategyManager,
    Strategy,
    StrategyConfig
)


@pytest.mark.unit
@pytest.mark.fast
class TestStrategyManager:
    """Test suite for StrategyManager"""
    
    def test_initialization_defaults_to_conservative(self):
        """Test manager initializes with CONSERVATIVE strategy"""
        # ARRANGE & ACT
        manager = StrategyManager()
        
        # ASSERT
        assert manager.current_strategy == Strategy.CONSERVATIVE
        config = manager.get_strategy_config()
        assert config.batch_size == 1
        assert config.risk_tolerance == 'LOW'
    
    def test_get_current_strategy_returns_active(self):
        """Test get_current_strategy returns active strategy"""
        # ARRANGE
        manager = StrategyManager()
        
        # ACT
        strategy = manager.get_current_strategy()
        
        # ASSERT
        assert isinstance(strategy, Strategy)
        assert strategy == Strategy.CONSERVATIVE
    
    def test_strategy_rotation_cycles_through_all(self):
        """Test strategy rotation cycles through all 4 strategies"""
        # ARRANGE
        manager = StrategyManager()
        expected_order = [
            Strategy.CONSERVATIVE,
            Strategy.AGGRESSIVE,
            Strategy.TARGETED,
            Strategy.EXPERIMENTAL
        ]
        
        # ACT & ASSERT
        for expected_type in expected_order:
            current = manager.get_current_strategy()
            assert current == expected_type
            manager.select_alternative_strategy()
        
        # After full rotation, should be back to CONSERVATIVE
        assert manager.get_current_strategy() == Strategy.CONSERVATIVE
    
    def test_aggressive_strategy_properties(self):
        """Test AGGRESSIVE strategy has correct properties"""
        # ARRANGE
        manager = StrategyManager()
        manager.select_alternative_strategy()  # Move to AGGRESSIVE
        
        # ACT
        strategy_enum = manager.get_current_strategy()
        config = manager.get_strategy_config(strategy_enum)
        
        # ASSERT
        assert strategy_enum == Strategy.AGGRESSIVE
        assert config.batch_size == 10
        assert config.risk_tolerance == 'HIGH'
        assert "multiple" in config.description.lower() or "quickly" in config.description.lower()
    
    def test_targeted_strategy_properties(self):
        """Test TARGETED strategy has correct properties"""
        # ARRANGE
        manager = StrategyManager()
        manager.select_alternative_strategy()  # AGGRESSIVE
        manager.select_alternative_strategy()  # TARGETED
        
        # ACT
        strategy_enum = manager.get_current_strategy()
        config = manager.get_strategy_config(strategy_enum)
        
        # ASSERT
        assert strategy_enum == Strategy.TARGETED
        assert config.batch_size == 3
        assert config.risk_tolerance == 'MEDIUM'
        assert "critical" in config.description.lower()
    
    def test_experimental_strategy_properties(self):
        """Test EXPERIMENTAL strategy has correct properties"""
        # ARRANGE
        manager = StrategyManager()
        for _ in range(3):
            manager.select_alternative_strategy()  # Move to EXPERIMENTAL
        
        # ACT
        strategy_enum = manager.get_current_strategy()
        config = manager.get_strategy_config(strategy_enum)
        
        # ASSERT
        assert strategy_enum == Strategy.EXPERIMENTAL
        assert config.batch_size == 2
        assert config.risk_tolerance == 'MEDIUM'
        assert "new" in config.description.lower()
    
    def test_should_switch_strategy_logic(self):
        """Test should_switch_strategy returns True after 3 failures"""
        # ARRANGE
        manager = StrategyManager()
        
        # ACT & ASSERT
        assert not manager.should_switch_strategy(consecutive_failures=0)
        assert not manager.should_switch_strategy(consecutive_failures=1)
        assert not manager.should_switch_strategy(consecutive_failures=2)
        assert manager.should_switch_strategy(consecutive_failures=3)
        assert manager.should_switch_strategy(consecutive_failures=5)
    
    def test_multiple_managers_independent(self):
        """Test multiple StrategyManager instances are independent"""
        # ARRANGE
        manager1 = StrategyManager()
        manager2 = StrategyManager()
        
        # ACT
        manager1.select_alternative_strategy()  # manager1 → AGGRESSIVE
        
        # ASSERT
        assert manager1.get_current_strategy() == Strategy.AGGRESSIVE
        assert manager2.get_current_strategy() == Strategy.CONSERVATIVE
    
    def test_strategy_rotation_is_deterministic(self):
        """Test strategy rotation follows consistent order"""
        # ARRANGE
        manager1 = StrategyManager()
        manager2 = StrategyManager()
        
        # ACT - Rotate both managers 3 times
        for _ in range(3):
            manager1.select_alternative_strategy()
            manager2.select_alternative_strategy()
        
        # ASSERT - Both should be at EXPERIMENTAL
        assert manager1.get_current_strategy() == Strategy.EXPERIMENTAL
        assert manager2.get_current_strategy() == Strategy.EXPERIMENTAL
    
    def test_record_result_tracks_failures(self):
        """Test record_result updates consecutive_failures counter"""
        # ARRANGE
        manager = StrategyManager()
        
        # ACT
        manager.record_result(success=False)
        manager.record_result(success=False)
        
        # ASSERT
        assert manager.consecutive_failures == 2
        
        # ACT - Success resets counter
        manager.record_result(success=True)
        
        # ASSERT
        assert manager.consecutive_failures == 0
    
    def test_strategy_switch_resets_failure_counter(self):
        """Test switching strategy resets consecutive_failures"""
        # ARRANGE
        manager = StrategyManager()
        manager.consecutive_failures = 5
        
        # ACT
        manager.select_alternative_strategy()
        
        # ASSERT
        assert manager.consecutive_failures == 0
    
    def test_get_history_returns_switches(self):
        """Test get_history tracks strategy switches"""
        # ARRANGE
        manager = StrategyManager()
        manager.consecutive_failures = 3
        
        # ACT
        manager.select_alternative_strategy()  # CONSERVATIVE → AGGRESSIVE
        manager.consecutive_failures = 3
        manager.select_alternative_strategy()  # AGGRESSIVE → TARGETED
        
        history = manager.get_history()
        
        # ASSERT
        assert len(history) == 2
        assert history[0]['from'] == 'conservative'
        assert history[0]['to'] == 'aggressive'
        assert history[1]['from'] == 'aggressive'
        assert history[1]['to'] == 'targeted'
    
    def test_reset_clears_all_state(self):
        """Test reset returns manager to initial state"""
        # ARRANGE
        manager = StrategyManager()
        manager.select_alternative_strategy()  # Change strategy
        manager.consecutive_failures = 5
        
        # ACT
        manager.reset()
        
        # ASSERT
        assert manager.get_current_strategy() == Strategy.CONSERVATIVE
        assert manager.consecutive_failures == 0
        assert len(manager.get_history()) == 0


@pytest.mark.unit
@pytest.mark.fast
class TestStrategyConfig:
    """Test suite for StrategyConfig dataclass"""
    
    def test_config_is_dataclass(self):
        """Test strategy config is a valid dataclass"""
        # ARRANGE
        manager = StrategyManager()
        config = manager.get_strategy_config()
        
        # ACT & ASSERT
        assert isinstance(config, StrategyConfig)
        assert hasattr(config, 'batch_size')
        assert hasattr(config, 'risk_tolerance')
        assert hasattr(config, 'description')
    
    def test_all_strategies_have_configs(self):
        """Test all 4 strategies have valid configurations"""
        # ARRANGE
        manager = StrategyManager()
        
        # ACT & ASSERT
        for strategy in Strategy:
            config = manager.get_strategy_config(strategy)
            assert isinstance(config, StrategyConfig)
            assert config.batch_size > 0
            assert config.risk_tolerance in ['LOW', 'MEDIUM', 'HIGH']
            assert len(config.description) > 0
