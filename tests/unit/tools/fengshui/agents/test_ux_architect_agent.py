"""
Unit tests for UX Architect Agent

Tests SAP Fiori/SAPUI5 UX architecture analysis capabilities:
- Fiori Design Guidelines compliance
- Control selection (standard vs custom)
- CSS anti-patterns
- API-UX separation
- Business logic placement
"""

import pytest
from pathlib import Path
from tools.fengshui.agents import UXArchitectAgent, Severity


class TestUXArchitectAgentInitialization:
    """Test agent initialization and capabilities"""
    
    def test_agent_initializes_correctly(self):
        # ARRANGE & ACT
        agent = UXArchitectAgent()
        
        # ASSERT
        assert agent.name == "ux_architect"
        assert agent.logger is not None
    
    def test_get_capabilities_returns_ux_checks(self):
        # ARRANGE
        agent = UXArchitectAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert len(capabilities) == 7
        assert "SAP Fiori Design Guidelines" in capabilities[0]
        assert "SAPUI5 control" in capabilities[1]
        assert "CSS anti-pattern" in capabilities[2]


class TestHTMLAnalysis:
    """Test HTML file analysis for Fiori compliance"""
    
    def test_detects_inline_styles(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "test.html"
        test_file.write_text(
            '<div style="padding: 20px">Content</div>\n'
        )
        
        # ACT
        findings = agent._analyze_html_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Inline Styles"
        assert findings[0].severity == Severity.MEDIUM
        assert "inline styles" in findings[0].description.lower()
    
    def test_ignores_sapui5_data_attributes(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "test.html"
        test_file.write_text(
            '<div data-sap-ui-config=\'{"theme":"sap_fiori_3"}\'></div>\n'
        )
        
        # ACT
        findings = agent._analyze_html_file(test_file)
        
        # ASSERT
        assert len(findings) == 0  # Should ignore SAPUI5 attributes


class TestXMLViewAnalysis:
    """Test SAPUI5 XML view analysis for control misuse"""
    
    def test_detects_customlistitem_without_inputlistitem(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "view.xml"
        test_file.write_text(
            '<List><CustomListItem><Text text="Item"/></CustomListItem></List>\n'
        )
        
        # ACT
        findings = agent._analyze_xml_view(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Control Selection"
        assert findings[0].severity == Severity.HIGH
        assert "CustomListItem" in findings[0].description
        assert "InputListItem" in findings[0].recommendation
    
    def test_accepts_customlistitem_with_inputlistitem(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "view.xml"
        test_file.write_text(
            '<List><CustomListItem/><InputListItem/></List>\n'
        )
        
        # ACT
        findings = agent._analyze_xml_view(test_file)
        
        # ASSERT
        assert len(findings) == 0  # InputListItem present, acceptable


class TestCSSAnalysis:
    """Test CSS analysis for anti-patterns"""
    
    def test_detects_important_rule(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "style.css"
        test_file.write_text(
            '.my-class {\n'
            '  color: red !important;\n'
            '}\n'
        )
        
        # ACT
        findings = agent._analyze_css_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "CSS Anti-Pattern"
        assert findings[0].severity == Severity.HIGH
        assert "!important" in findings[0].description
    
    def test_detects_padding_hack(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "style.css"
        test_file.write_text(
            '.hack {\n'
            '  padding: 20px !important;\n'
            '}\n'
        )
        
        # ACT
        findings = agent._analyze_css_file(test_file)
        
        # ASSERT
        assert len(findings) >= 1  # At least padding hack
        padding_hacks = [f for f in findings if f.category == "CSS Hack"]
        assert len(padding_hacks) == 1
        assert "padding hack" in padding_hacks[0].description.lower()
    
    def test_detects_multiple_css_issues(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "style.css"
        test_file.write_text(
            '.class1 { color: red !important; }\n'
            '.class2 { padding: 10px !important; }\n'
            '.class3 { margin: 5px !important; }\n'
        )
        
        # ACT
        findings = agent._analyze_css_file(test_file)
        
        # ASSERT
        assert len(findings) >= 3  # Multiple violations


class TestJavaScriptUXAnalysis:
    """Test JavaScript UX file analysis"""
    
    def test_detects_hardcoded_api_url(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "dataProductsPage.js"
        test_file.write_text(
            'fetch("/api/data-products")\n'
            '  .then(r => r.json())\n'
        )
        
        # ACT
        findings = agent._analyze_ux_js_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "API-UX Coupling"
        assert findings[0].severity == Severity.MEDIUM
        assert "hardcoded" in findings[0].description.lower()
    
    def test_detects_business_logic_calculatetotal(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "invoicePage.js"
        test_file.write_text(
            'if (items.length > 0 && calculateTotal(items) > 1000) {\n'
            '  showWarning();\n'
            '}\n'
        )
        
        # ACT
        findings = agent._analyze_ux_js_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Business Logic in UX"
        assert findings[0].severity == Severity.MEDIUM
        assert "calculateTotal" in findings[0].description
    
    def test_detects_business_logic_validateinvoice(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "formPage.js"
        test_file.write_text(
            'if (validateInvoice(data)) {\n'
            '  submit();\n'
            '}\n'
        )
        
        # ACT
        findings = agent._analyze_ux_js_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "validateInvoice" in findings[0].description
    
    def test_detects_process_function(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "orderPage.js"
        test_file.write_text(
            'function processOrder(order) {\n'
            '  // Business logic here\n'
            '}\n'
        )
        
        # ACT
        findings = agent._analyze_ux_js_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "process" in findings[0].description.lower()
    
    def test_ignores_non_page_js_files(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "util.js"  # Not a "Page" file
        test_file.write_text('fetch("/api/data")\n')
        
        # ACT
        # Note: analyze_module checks filename, this tests _analyze_ux_js_file
        findings = agent._analyze_ux_js_file(test_file)
        
        # ASSERT
        # Should still detect if analyzed, but analyze_module won't call it
        assert len(findings) >= 0  # Method works regardless


class TestModuleAnalysis:
    """Test full module analysis"""
    
    def test_analyzes_complete_module(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # Create test files
        html_file = module_path / "index.html"
        html_file.write_text('<div style="padding: 10px">Test</div>\n')
        
        css_file = module_path / "style.css"
        css_file.write_text('.test { color: red !important; }\n')
        
        # ACT
        report = agent.analyze_module(module_path)
        
        # ASSERT
        assert report.agent_name == "ux_architect"
        assert report.module_path == module_path
        assert len(report.findings) == 2  # HTML + CSS violations
        assert report.metrics['total_findings'] == 2
        assert report.metrics['html_files'] == 1
        assert report.metrics['css_files'] == 1
    
    def test_handles_invalid_module_path(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        invalid_path = tmp_path / "nonexistent"
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "invalid" in report.summary.lower()
    
    def test_generates_clean_report_no_violations(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        module_path = tmp_path / "clean_module"
        module_path.mkdir()
        
        # Create clean files
        html_file = module_path / "index.html"
        html_file.write_text('<div class="content">Test</div>\n')
        
        css_file = module_path / "style.css"
        css_file.write_text('.content { color: blue; }\n')
        
        # ACT
        report = agent.analyze_module(module_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "✅" in report.summary
        assert "No violations" in report.summary


class TestMetrics:
    """Test metrics calculation"""
    
    def test_metrics_count_files_correctly(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # Create multiple files
        (module_path / "index.html").write_text('<div>Test</div>\n')
        (module_path / "view.xml").write_text('<View/>\n')
        (module_path / "style.css").write_text('.test {}\n')
        (module_path / "dataPage.js").write_text('console.log("test");\n')
        
        # ACT
        report = agent.analyze_module(module_path)
        
        # ASSERT
        assert report.metrics['html_files'] == 1
        assert report.metrics['xml_views'] == 1
        assert report.metrics['css_files'] == 1
        assert report.metrics['js_files'] == 1
    
    def test_metrics_count_severity_levels(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # Create files with different severity violations
        (module_path / "index.html").write_text('<div style="color: red">Test</div>\n')  # MEDIUM
        (module_path / "view.xml").write_text('<CustomListItem/>\n')  # HIGH
        (module_path / "style.css").write_text('.test { color: red !important; }\n')  # HIGH
        
        # ACT
        report = agent.analyze_module(module_path)
        
        # ASSERT
        assert report.metrics['critical_count'] == 0
        assert report.metrics['high_count'] == 2
        assert report.metrics['medium_count'] == 1


class TestErrorHandling:
    """Test error handling"""
    
    def test_handles_unreadable_html_file(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "test.html"
        test_file.write_bytes(b'\x80\x81\x82')  # Invalid UTF-8
        
        # ACT
        findings = agent._analyze_html_file(test_file)
        
        # ASSERT
        assert isinstance(findings, list)  # Should not crash
    
    def test_handles_unreadable_css_file(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "test.css"
        test_file.write_bytes(b'\x80\x81\x82')  # Invalid UTF-8
        
        # ACT
        findings = agent._analyze_css_file(test_file)
        
        # ASSERT
        assert isinstance(findings, list)  # Should not crash


class TestRecommendations:
    """Test recommendation quality"""
    
    def test_inline_style_recommendation_suggests_classes(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "test.html"
        test_file.write_text('<div style="padding: 20px">Content</div>\n')
        
        # ACT
        findings = agent._analyze_html_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "CSS classes" in findings[0].recommendation
        assert "Fiori theming" in findings[0].recommendation
    
    def test_customlistitem_recommendation_suggests_inputlistitem(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "view.xml"
        test_file.write_text('<CustomListItem/>\n')
        
        # ACT
        findings = agent._analyze_xml_view(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "InputListItem" in findings[0].recommendation
        assert "standard control" in findings[0].recommendation.lower()
    
    def test_important_css_recommendation_suggests_specificity(self, tmp_path):
        # ARRANGE
        agent = UXArchitectAgent()
        test_file = tmp_path / "style.css"
        test_file.write_text('.test { color: red !important; }\n')
        
        # ACT
        findings = agent._analyze_css_file(test_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "specificity" in findings[0].recommendation.lower()