"""
Gu Wu Framework Example Test - Validates Metrics Collection

This is a simple test to verify that the Gu Wu framework is working correctly.
It demonstrates:
- Test naming convention
- Test markers
- AAA pattern
- Basic assertions
"""

import pytest
import time


@pytest.mark.unit
@pytest.mark.fast
def test_simple_calculation_succeeds():
    """Test basic arithmetic (fast unit test example)"""
    # ARRANGE
    a = 2
    b = 2
    
    # ACT
    result = a + b
    
    # ASSERT
    assert result == 4, f"Expected 4, got {result}"


@pytest.mark.unit
@pytest.mark.fast
def test_string_concatenation_succeeds():
    """Test string operations (another fast unit test)"""
    # ARRANGE
    greeting = "Hello"
    name = "Gu Wu"
    
    # ACT
    message = f"{greeting}, {name}!"
    
    # ASSERT
    assert message == "Hello, Gu Wu!"
    assert len(message) > 0


@pytest.mark.unit
def test_list_operations_succeed():
    """Test list operations (demonstrates fixture-less test)"""
    # ARRANGE
    items = [1, 2, 3]
    
    # ACT
    items.append(4)
    total = sum(items)
    
    # ASSERT
    assert len(items) == 4
    assert total == 10


@pytest.mark.unit
@pytest.mark.slow
def test_intentionally_slow_operation():
    """Test that takes > 1 second (will be flagged by Gu Wu as slow)"""
    # ARRANGE
    start = time.time()
    
    # ACT
    time.sleep(1.2)  # Simulate slow operation
    duration = time.time() - start
    
    # ASSERT
    assert duration >= 1.0, "Operation should take at least 1 second"


@pytest.mark.unit
@pytest.mark.parametrize("input_value,expected", [
    (0, 0),
    (1, 1),
    (5, 25),
    (10, 100),
])
def test_square_function_with_multiple_inputs(input_value, expected):
    """Test square function with parametrized inputs (demonstrates parametrization)"""
    # ARRANGE & ACT
    result = input_value ** 2
    
    # ASSERT
    assert result == expected, f"Expected {input_value}² = {expected}, got {result}"


# This test will be tracked by Gu Wu:
# - Duration: Each execution time recorded
# - Outcome: Pass/fail tracked in metrics.db
# - Markers: 'unit' and 'fast' stored
# - Layer: Detected as 'unit' from path
# - Module: Detected as 'core' from path
#
# After 3+ runs, Gu Wu will calculate flaky score.
# The slow test above will be flagged if avg duration > 5s.