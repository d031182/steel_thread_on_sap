"""
Code Extraction Utility for Feng Shui

Extracts code snippets with context for actionable findings.
"""

from pathlib import Path
from typing import Optional, Tuple


class CodeExtractor:
    """
    Extracts code snippets from source files with context
    
    Features:
    - Extract lines N to M with line numbers
    - Highlight problematic lines with 🔴
    - Handle file encoding issues gracefully
    - Truncate long lines (>120 chars)
    - Add context lines (±3 lines default)
    """
    
    MAX_LINE_LENGTH = 120
    DEFAULT_CONTEXT_LINES = 3
    
    @staticmethod
    def extract_snippet(
        file_path: str,
        start_line: int,
        end_line: Optional[int] = None,
        highlight_lines: Optional[list[int]] = None,
        context_lines: int = DEFAULT_CONTEXT_LINES
    ) -> Optional[str]:
        """
        Extract code snippet with context
        
        Args:
            file_path: Path to source file (relative to project root)
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed), defaults to start_line
            highlight_lines: List of line numbers to highlight with 🔴
            context_lines: Number of context lines before/after (default: 3)
            
        Returns:
            Formatted code snippet with line numbers, or None if extraction fails
            
        Example Output:
            137 | # Load nodes
            138 | cursor.execute("SELECT * FROM nodes")
            139 | for row in cursor.fetchall():  # 🔴 N+1 pattern
            140 |     json.loads(row[3])         # 🔴 Per-row parsing
            141 |     graph.add_node(node)
            142 |
        """
        try:
            # Convert to Path object
            path = Path(file_path)
            if not path.exists():
                return None
            
            # Read file with encoding fallback
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Fallback to latin-1 for files with special characters
                with open(path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            
            # Determine actual line range
            if end_line is None:
                end_line = start_line
            
            # Add context
            actual_start = max(1, start_line - context_lines)
            actual_end = min(len(lines), end_line + context_lines)
            
            # Prepare highlight set
            highlight_set = set(highlight_lines) if highlight_lines else set()
            
            # Build snippet
            snippet_lines = []
            for line_num in range(actual_start, actual_end + 1):
                # Get line content (0-indexed)
                line_content = lines[line_num - 1].rstrip()
                
                # Truncate long lines
                if len(line_content) > CodeExtractor.MAX_LINE_LENGTH:
                    line_content = line_content[:CodeExtractor.MAX_LINE_LENGTH - 3] + "..."
                
                # Add highlight marker if needed
                marker = "  # 🔴" if line_num in highlight_set else ""
                
                # Format: "139 | for row in cursor.fetchall():  # 🔴"
                snippet_lines.append(f"   {line_num:3d} | {line_content}{marker}")
            
            return "\n".join(snippet_lines)
            
        except Exception as e:
            # Graceful degradation - return None if extraction fails
            return None
    
    @staticmethod
    def extract_function_context(
        file_path: str,
        line_number: int,
        context_lines: int = 10
    ) -> Optional[str]:
        """
        Extract function/method containing the specified line
        
        Useful for showing complete function context for violations.
        
        Args:
            file_path: Path to source file
            line_number: Line number within function
            context_lines: Max lines to extract (default: 10)
            
        Returns:
            Function code snippet, or None if extraction fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find function start (def or class keyword with proper indentation)
            function_start = line_number
            target_indent = None
            
            # Search backwards for function definition
            for i in range(line_number - 1, max(0, line_number - 50), -1):
                line = lines[i]
                stripped = line.lstrip()
                
                # Check for function/method definition
                if stripped.startswith('def ') or stripped.startswith('class '):
                    # Track indentation level
                    if target_indent is None:
                        target_indent = len(line) - len(stripped)
                    
                    current_indent = len(line) - len(stripped)
                    if current_indent == target_indent:
                        function_start = i + 1  # 1-indexed
                        break
            
            # Extract function (limited to context_lines)
            end_line = min(line_number + context_lines, len(lines))
            
            return CodeExtractor.extract_snippet(
                file_path,
                function_start,
                end_line,
                highlight_lines=[line_number]
            )
            
        except Exception:
            return None
    
    @staticmethod
    def format_fix_example(
        current_code: str,
        fixed_code: str,
        description: str = ""
    ) -> str:
        """
        Format before/after code comparison
        
        Args:
            current_code: Current problematic code
            fixed_code: Proposed fixed code
            description: Optional description of the fix
            
        Returns:
            Formatted before/after comparison
            
        Example Output:
            # Current (problematic):
            for row in cursor.fetchall():
                json.loads(row[3])
            
            # Fixed (optimized):
            rows = [json.loads(r[3]) if r[3] else {} for r in cursor.fetchall()]
        """
        result = []
        
        if description:
            result.append(f"# {description}")
            result.append("")
        
        result.append("# Current (problematic):")
        result.append(current_code.strip())
        result.append("")
        result.append("# Fixed (optimized):")
        result.append(fixed_code.strip())
        
        return "\n".join(result)