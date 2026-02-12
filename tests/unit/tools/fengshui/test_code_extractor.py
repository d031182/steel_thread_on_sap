"""
Unit Tests for CodeExtractor Utility

Tests code snippet extraction with context, highlighting, and error handling.
"""

import pytest
from pathlib import Path
from tools.fengshui.utils.code_extractor import CodeExtractor


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_basic():
    """Test basic code snippet extraction"""
    # Create temporary test file
    test_file = Path("test_extract.py")
    test_content = """# Line 1
def test_function():
    # Line 3
    x = 5
    y = 10
    return x + y
# Line 7
"""
    test_file.write_text(test_content)
    
    try:
        # Extract line 4 with default context (±3 lines)
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=4,
            context_lines=2
        )
        
        assert snippet is not None
        assert "x = 5" in snippet
        assert "def test_function():" in snippet  # Context above
        assert "return x + y" in snippet  # Context below
        assert "   2 |" in snippet  # Line numbers present
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_with_highlighting():
    """Test code snippet extraction with highlighted lines"""
    test_file = Path("test_highlight.py")
    test_content = """def example():
    for item in items:
        process(item)
        save(item)
    return True
"""
    test_file.write_text(test_content)
    
    try:
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=2,
            end_line=4,
            highlight_lines=[2, 4],
            context_lines=1
        )
        
        assert snippet is not None
        assert "# 🔴" in snippet  # Highlight markers present
        assert snippet.count("# 🔴") == 2  # Two highlighted lines
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_handles_missing_file():
    """Test graceful handling of missing file"""
    snippet = CodeExtractor.extract_snippet(
        "nonexistent_file.py",
        start_line=10
    )
    
    assert snippet is None  # Graceful degradation


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_truncates_long_lines():
    """Test that long lines are truncated to 120 chars"""
    test_file = Path("test_long.py")
    long_line = "x = " + "a" * 150  # 154 chars
    test_content = f"""def test():
    {long_line}
    return x
"""
    test_file.write_text(test_content)
    
    try:
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=2,
            context_lines=0
        )
        
        assert snippet is not None
        # Check that line is truncated with "..."
        lines = snippet.split('\n')
        truncated_line = [l for l in lines if 'x = aaa' in l][0]
        assert len(truncated_line) <= 130  # Line number (3) + " | " + content (<=120) + "..."
        assert "..." in truncated_line
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_handles_encoding():
    """Test handling of files with special characters"""
    test_file = Path("test_encoding.py")
    # Content with unicode characters
    test_content = """def test():
    # Comment with unicode: ✅ 🔴 🎯
    name = "François"
    return True
"""
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=2,
            context_lines=1
        )
        
        assert snippet is not None
        assert "François" in snippet or "Fran" in snippet  # Handle encoding
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_extract_function_context():
    """Test extraction of function containing a specific line"""
    test_file = Path("test_function.py")
    test_content = """class MyClass:
    def method_one(self):
        pass
    
    def method_two(self):
        x = 5
        y = 10
        return x + y  # Line 8
    
    def method_three(self):
        pass
"""
    test_file.write_text(test_content)
    
    try:
        # Extract function containing line 8
        snippet = CodeExtractor.extract_function_context(
            str(test_file),
            line_number=8,
            context_lines=5
        )
        
        assert snippet is not None
        assert "def method_two" in snippet
        assert "return x + y" in snippet
        assert "# 🔴" in snippet  # Line 8 should be highlighted
        # Note: May include adjacent methods as context (this is acceptable)
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_format_fix_example():
    """Test before/after code formatting"""
    current = """for item in items:
    cursor.execute("SELECT * FROM table WHERE id = ?", (item.id,))"""
    
    fixed = """item_ids = [item.id for item in items]
cursor.execute("SELECT * FROM table WHERE id IN (?)", (item_ids,))"""
    
    formatted = CodeExtractor.format_fix_example(
        current,
        fixed,
        description="Use bulk query instead of N queries"
    )
    
    assert "# Use bulk query instead of N queries" in formatted
    assert "# Current (problematic):" in formatted
    assert "# Fixed (optimized):" in formatted
    assert "for item in items:" in formatted
    assert "item_ids = [" in formatted


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_boundary_conditions():
    """Test edge cases: first line, last line, single line file"""
    test_file = Path("test_boundary.py")
    test_content = "x = 5\n"  # Single line
    test_file.write_text(test_content)
    
    try:
        # Extract first (and only) line
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=1,
            context_lines=3  # Should not crash even with no context available
        )
        
        assert snippet is not None
        assert "x = 5" in snippet
        
    finally:
        test_file.unlink()


@pytest.mark.unit
@pytest.mark.fast
def test_extract_snippet_line_numbers_formatted():
    """Test that line numbers are properly formatted (right-aligned, 3 digits)"""
    test_file = Path("test_format.py")
    test_content = "\n".join([f"# Line {i}" for i in range(1, 200)])
    test_file.write_text(test_content)
    
    try:
        # Extract line 150
        snippet = CodeExtractor.extract_snippet(
            str(test_file),
            start_line=150,
            context_lines=1
        )
        
        assert snippet is not None
        # Check formatting: "   150 | # Line 150"
        assert "   150 |" in snippet or "  150 |" in snippet
        
    finally:
        test_file.unlink()