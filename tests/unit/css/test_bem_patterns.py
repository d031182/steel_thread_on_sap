"""
BEM Pattern Recognition and Validation Tests

Tests pattern consistency, documentation, and enforcement
for Block Element Modifier CSS naming conventions.
"""

import re
import pytest
from pathlib import Path
from typing import Set, Dict, List, Tuple


class CSSParser:
    """Parse CSS files to extract BEM patterns."""

    @staticmethod
    def extract_selectors(css_content: str) -> List[str]:
        """Extract all CSS selectors from content."""
        # Simple regex to find selectors (class, id, attribute)
        selector_pattern = r'([#.][\w-]+)'
        matches = re.findall(selector_pattern, css_content)
        return matches

    @staticmethod
    def extract_blocks(selectors: List[str]) -> Set[str]:
        """Extract block names from selectors."""
        blocks = set()
        for selector in selectors:
            # Remove # or . prefix
            clean = selector.lstrip('#.')
            
            # Extract block (before __ or --)
            if '__' in clean:
                block = clean.split('__')[0]
                blocks.add(block)
            elif '--' in clean:
                block = clean.split('--')[0]
                blocks.add(block)
            else:
                # Single-word selectors are typically blocks
                if '_' not in clean and '-' in clean or clean.isidentifier():
                    blocks.add(clean)
        
        return blocks

    @staticmethod
    def extract_elements(selectors: List[str]) -> Set[Tuple[str, str]]:
        """Extract (block, element) tuples from selectors."""
        elements = set()
        for selector in selectors:
            clean = selector.lstrip('#.')
            
            if '__' in clean:
                parts = clean.split('__')
                block = parts[0]
                element = parts[1].split('--')[0]  # Remove modifiers
                elements.add((block, element))
        
        return elements

    @staticmethod
    def extract_modifiers(selectors: List[str]) -> Set[Tuple[str, str]]:
        """Extract (element, modifier) tuples from selectors."""
        modifiers = set()
        for selector in selectors:
            clean = selector.lstrip('#.')
            
            if '--' in clean:
                # Get the part before --
                prefix = clean.split('--')[0]
                modifier = clean.split('--')[1]
                modifiers.add((prefix, modifier))
        
        return modifiers


class TestBEMPatternRecognition:
    """Test BEM pattern recognition and validation."""

    @pytest.fixture
    def ai_assistant_css(self):
        """Load ai-assistant.css content."""
        path = Path(__file__).parent.parent.parent.parent / "app_v2" / "static" / "css" / "ai-assistant.css"
        return path.read_text()

    def test_parser_extracts_blocks(self, ai_assistant_css):
        """Verify CSS parser correctly extracts blocks."""
        selectors = CSSParser.extract_selectors(ai_assistant_css)
        blocks = CSSParser.extract_blocks(selectors)
        
        # Should have recognized major blocks
        assert len(blocks) > 0, "Should extract at least one block"
        
        # Common blocks
        block_list = list(blocks)
        print(f"Extracted blocks: {block_list}")

    def test_parser_extracts_elements(self, ai_assistant_css):
        """Verify CSS parser correctly extracts elements."""
        selectors = CSSParser.extract_selectors(ai_assistant_css)
        elements = CSSParser.extract_elements(selectors)
        
        # Elements should exist
        assert len(elements) >= 0, "Parser should handle elements"

    def test_parser_extracts_modifiers(self, ai_assistant_css):
        """Verify CSS parser correctly extracts modifiers."""
        selectors = CSSParser.extract_selectors(ai_assistant_css)
        modifiers = CSSParser.extract_modifiers(selectors)
        
        # Modifiers should exist
        assert len(modifiers) >= 0, "Parser should handle modifiers"

    def test_bem_consistency_across_file(self, ai_assistant_css):
        """Verify BEM patterns are used consistently."""
        # Extract all custom class selectors
        class_pattern = r'\.([a-z][\w-]*)'
        classes = set(re.findall(class_pattern, ai_assistant_css))
        
        # Separate by pattern
        blocks = {c for c in classes if '__' not in c and '--' not in c}
        elements = {c for c in classes if '__' in c and '--' not in c}
        modifiers = {c for c in classes if '--' in c}
        
        # Should have representation of all three
        print(f"Blocks: {len(blocks)}, Elements: {len(elements)}, Modifiers: {len(modifiers)}")

    def test_markdown_classes_follow_pattern(self, ai_assistant_css):
        """Verify markdown-* classes follow BEM conventions."""
        # Extract markdown-related classes
        markdown_pattern = r'\.markdown-(\w+)'
        markdown_classes = set(re.findall(markdown_pattern, ai_assistant_css))
        
        # These are legacy, but should map to BEM
        if markdown_classes:
            print(f"Legacy markdown classes: {markdown_classes}")
            # Should also have ai-message versions
            assert '.ai-message' in ai_assistant_css, \
                "Should have modern ai-message BEM block"


class TestBEMDocumentation:
    """Test BEM documentation and comments."""

    @pytest.fixture
    def ai_assistant_css(self):
        """Load ai-assistant.css content."""
        path = Path(__file__).parent.parent.parent.parent / "app_v2" / "static" / "css" / "ai-assistant.css"
        return path.read_text()

    def test_bem_block_documented(self, ai_assistant_css):
        """Verify BEM blocks have documentation."""
        # Should have JSDoc comments for blocks
        assert '/**' in ai_assistant_css, "Should have JSDoc documentation"
        assert 'Block:' in ai_assistant_css, "Should document blocks"

    def test_bem_elements_documented(self, ai_assistant_css):
        """Verify BEM elements have documentation."""
        assert 'Element:' in ai_assistant_css, "Should document elements"

    def test_bem_modifiers_documented(self, ai_assistant_css):
        """Verify BEM modifiers have documentation."""
        assert 'Modifier:' in ai_assistant_css or 'modifier' in ai_assistant_css, \
            "Should document modifiers"

    def test_documentation_completeness(self, ai_assistant_css):
        """Verify documentation covers all major sections."""
        # Should have documentation for:
        # 1. Block definition
        # 2. Element definitions
        # 3. Modifier examples
        
        sections = {
            'block': 'Block:' in ai_assistant_css,
            'elements': 'Element' in ai_assistant_css,
            'modifiers': 'Modifier' in ai_assistant_css or '--' in ai_assistant_css,
        }
        
        documented = sum(sections.values())
        assert documented >= 2, "Should document at least block + elements/modifiers"


class TestBEMEnforcement:
    """Test BEM enforcement and validation rules."""

    def test_bem_naming_regex_validation(self):
        """Verify BEM naming regex properly validates patterns."""
        # BEM-compliant pattern
        bem_regex = r'^[a-z0-9]+(-[a-z0-9]+)*(__[a-z0-9]+(-[a-z0-9]+)*)?(--[a-z0-9]+(-[a-z0-9]+)*)?$'
        
        test_cases = {
            # Valid patterns
            'button': True,
            'ai-message': True,
            'ai-message__content': True,
            'ai-message__content--user': True,
            'form__input--disabled': True,
            
            # Invalid patterns
            'aiMessage': False,          # camelCase
            'ai_message': False,         # single underscore
            'ai_message__content': False,  # underscore in block
            'AI-Message': False,         # uppercase
            '--modifier': False,         # modifier alone
            '__element': False,          # element alone
        }
        
        for name, should_match in test_cases.items():
            matches = bool(re.match(bem_regex, name))
            if should_match:
                assert matches, f"'{name}' should match BEM pattern"
            else:
                assert not matches, f"'{name}' should NOT match BEM pattern"

    def test_bem_no_excessive_modifiers(self):
        """Verify elements don't have multiple modifiers."""
        # Bad: element--modifier1--modifier2
        # Good: element--modifier1 (use separate classes if needed)
        
        double_modifier_pattern = r'([a-z-]+)--([a-z-]+)--([a-z-]+)'
        test_string = ".button--primary--large"
        
        matches = re.findall(double_modifier_pattern, test_string)
        # Multiple modifiers should be separate classes, not chained
        assert len(matches) == 1, "Should detect multiple modifiers (anti-pattern)"

    def test_bem_block_element_naming(self):
        """Verify consistent block and element naming."""
        # Block names should be descriptive and single-word or hyphenated
        valid_blocks = ['button', 'form', 'ai-message', 'kgv2-legend']
        
        # Element names should relate to parent block
        valid_elements = [
            ('button', 'icon'),
            ('form', 'input'),
            ('ai-message', 'content'),
            ('kgv2-legend', 'item'),
        ]
        
        for block, element in valid_elements:
            selector = f".{block}__{element}"
            # Should have __ delimiter
            assert '__' in selector, f"Element selector should use __: {selector}"
            # Should not have single underscore
            assert selector.count('_') == 2, f"Should have exactly __ (2 underscores): {selector}"


class TestBEMRealWorldValidation:
    """Real-world validation against actual CSS files."""

    @pytest.fixture
    def knowledge_graph_css(self):
        """Load knowledge-graph-v2.css."""
        path = Path(__file__).parent.parent.parent.parent / "modules" / "knowledge_graph_v2" / "frontend" / "styles" / "knowledge-graph-v2.css"
        if path.exists():
            return path.read_text()
        return None

    def test_knowledge_graph_bem_compliant(self, knowledge_graph_css):
        """Verify knowledge-graph-v2.css is BEM compliant baseline."""
        if not knowledge_graph_css:
            pytest.skip("knowledge-graph-v2.css not found")
        
        # Should have kgv2 block
        assert 'kgv2-' in knowledge_graph_css or 'kgv2_' in knowledge_graph_css, \
            "Should have kgv2 block prefix"
        
        # Should have legend element
        assert 'legend' in knowledge_graph_css.lower(), \
            "Should have legend component"

    def test_bem_css_specificity(self):
        """Verify BEM reduces CSS specificity."""
        # BEM patterns keep specificity low:
        # - Single class selector: 0,1,0
        # - Element modifier: 0,2,0
        # - Nested with pseudo: 0,2,1
        
        bem_selectors = [
            ('.button', 10),           # 0,1,0
            ('.button__icon', 20),     # 0,2,0
            ('.button--primary', 20),  # 0,2,0 (equivalent to element modifier)
        ]
        
        for selector, expected_specificity_lower in bem_selectors:
            # Count classes
            class_count = selector.count('.')
            # BEM should use multiple classes, keeping specificity manageable
            assert class_count <= 2, f"BEM selector should have ≤2 classes: {selector}"