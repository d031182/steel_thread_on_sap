"""
UX Architect Agent - SAP Fiori/SAPUI5 UX Architecture Analysis

Specializes in:
- SAP Fiori Design Guidelines compliance
- SAPUI5 control usage patterns (standard vs custom)
- CSS anti-patterns (no !important, no padding hacks)
- API-UX wiring patterns (proper separation, extensibility)
- Responsive design validation
- Frontend-backend communication architecture
"""

import re
import logging
from pathlib import Path
from typing import List, Dict
import time
from xml.etree import ElementTree as ET

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class UXArchitectAgent(BaseAgent):
    """
    Specializes in SAP Fiori/SAPUI5 UX architecture quality
    
    Focuses on:
    - Fiori Design Guidelines adherence
    - Control selection (prefer standard over custom)
    - CSS best practices (no hacks)
    - API-UX separation and wiring
    - Sustainable, extensible UX architecture
    """
    
    def __init__(self):
        super().__init__("ux_architect")
        
        # Fiori guidelines violations
        self.fiori_violations = {
            'custom_list_item': re.compile(r'<.*?CustomListItem', re.IGNORECASE),
            'important_css': re.compile(r'!important', re.IGNORECASE),
            'inline_styles': re.compile(r'style\s*=\s*["\']', re.IGNORECASE),
        }
        
        # Preferred patterns
        self.preferred_patterns = {
            'InputListItem': 'Standard Fiori control for list items',
            'ObjectListItem': 'Standard Fiori control for object displays',
            'StandardListItem': 'Standard Fiori control for basic lists'
        }
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze UX architecture quality
        
        Checks:
        - Fiori Design Guidelines compliance
        - Control misuse (CustomListItem vs InputListItem)
        - CSS anti-patterns (!important, padding hacks)
        - API-UX coupling issues
        - Responsive design patterns
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with UX architecture findings
        """
        start_time = time.time()
        findings = []
        
        if not self.validate_module_path(module_path):
            return AgentReport(
                agent_name=self.name,
                module_path=module_path,
                execution_time_seconds=0,
                findings=[],
                metrics={},
                summary="Invalid module path"
            )
        
        self.logger.info(f"Analyzing UX architecture of {module_path}")
        
        # Analyze HTML files
        for html_file in module_path.rglob('*.html'):
            findings.extend(self._analyze_html_file(html_file))
        
        # Analyze XML views (SAPUI5)
        for xml_file in module_path.rglob('*.xml'):
            findings.extend(self._analyze_xml_view(xml_file))
        
        # Analyze CSS files
        for css_file in module_path.rglob('*.css'):
            findings.extend(self._analyze_css_file(css_file))
        
        # Analyze JavaScript UX files
        for js_file in module_path.rglob('*.js'):
            if 'Page' in js_file.name or 'page' in js_file.name:
                findings.extend(self._analyze_ux_js_file(js_file))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'html_files': len(list(module_path.rglob('*.html'))),
            'xml_views': len(list(module_path.rglob('*.xml'))),
            'css_files': len(list(module_path.rglob('*.css'))),
            'js_files': len([f for f in module_path.rglob('*.js') if 'Page' in f.name or 'page' in f.name])
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"UX architecture analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of UX architecture analysis capabilities"""
        return [
            "SAP Fiori Design Guidelines compliance checking",
            "SAPUI5 control usage validation (standard vs custom)",
            "CSS anti-pattern detection (!important, padding hacks)",
            "API-UX wiring pattern analysis",
            "Frontend-backend separation validation",
            "Responsive design pattern checking",
            "Control selection recommendations (InputListItem vs CustomListItem)"
        ]
    
    def _analyze_html_file(self, file_path: Path) -> List[Finding]:
        """Analyze HTML file for Fiori compliance"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for inline styles (anti-pattern)
            for line_num, line in enumerate(lines, 1):
                if self.fiori_violations['inline_styles'].search(line):
                    # Skip SAPUI5 data-sap-ui attributes
                    if 'data-sap-ui' in line:
                        continue
                    
                    findings.append(Finding(
                        category="Inline Styles",
                        severity=Severity.MEDIUM,
                        file_path=file_path,
                        line_number=line_num,
                        description="Inline styles detected (Fiori anti-pattern)",
                        recommendation="Use CSS classes or Fiori theming instead of inline styles",
                        code_snippet=line.strip()[:100]
                    ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _analyze_xml_view(self, file_path: Path) -> List[Finding]:
        """Analyze SAPUI5 XML view for control misuse"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Detect CustomListItem when InputListItem might be better
            if 'CustomListItem' in content:
                # Check if InputListItem is NOT used (might be better choice)
                if 'InputListItem' not in content:
                    for line_num, line in enumerate(lines, 1):
                        if 'CustomListItem' in line:
                            findings.append(Finding(
                                category="Control Selection",
                                severity=Severity.HIGH,
                                file_path=file_path,
                                line_number=line_num,
                                description="CustomListItem used without considering InputListItem (standard control preferred)",
                                recommendation="Evaluate if InputListItem can achieve same result (standard controls preferred per Fiori guidelines)",
                                code_snippet=line.strip()[:100]
                            ))
                            break  # One finding per file sufficient
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _analyze_css_file(self, file_path: Path) -> List[Finding]:
        """Analyze CSS for anti-patterns"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Detect !important (CSS hack)
            for line_num, line in enumerate(lines, 1):
                if self.fiori_violations['important_css'].search(line):
                    findings.append(Finding(
                        category="CSS Anti-Pattern",
                        severity=Severity.HIGH,
                        file_path=file_path,
                        line_number=line_num,
                        description="!important CSS rule detected (Fiori anti-pattern)",
                        recommendation="Use proper CSS specificity or Fiori theming instead of !important",
                        code_snippet=line.strip()
                    ))
            
            # Detect padding hacks (e.g., padding: 20px !important)
            padding_hack = re.compile(r'padding[^:]*:\s*\d+px\s*!important', re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                if padding_hack.search(line):
                    findings.append(Finding(
                        category="CSS Hack",
                        severity=Severity.HIGH,
                        file_path=file_path,
                        line_number=line_num,
                        description="Padding hack with !important (Fiori anti-pattern)",
                        recommendation="Use Fiori spacing classes or content density instead of padding hacks",
                        code_snippet=line.strip()
                    ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _analyze_ux_js_file(self, file_path: Path) -> List[Finding]:
        """Analyze JavaScript UX file for API-UX coupling issues"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for hardcoded API URLs (should use API modules)
            hardcoded_url = re.compile(r'fetch\s*\(\s*["\']/(api|backend)', re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                if hardcoded_url.search(line):
                    findings.append(Finding(
                        category="API-UX Coupling",
                        severity=Severity.MEDIUM,
                        file_path=file_path,
                        line_number=line_num,
                        description="Hardcoded API URL in UX code (tight coupling)",
                        recommendation="Use API abstraction layer (e.g., app/static/js/api/*.js modules) for loose coupling",
                        code_snippet=line.strip()[:100]
                    ))
            
            # Check for business logic in UX (should be in backend)
            business_logic_patterns = [
                (r'if\s*\([^)]*calculateTotal', "Business logic (calculateTotal) in UX"),
                (r'if\s*\([^)]*validateInvoice', "Business logic (validateInvoice) in UX"),
                (r'function\s+process[A-Z]', "Business logic (process*) function in UX"),
            ]
            
            for pattern, description in business_logic_patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        findings.append(Finding(
                            category="Business Logic in UX",
                            severity=Severity.MEDIUM,
                            file_path=file_path,
                            line_number=line_num,
                            description=description,
                            recommendation="Move business logic to backend API, keep UX layer thin (presentation only)",
                            code_snippet=line.strip()[:100]
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        total_files = metrics['html_files'] + metrics['xml_views'] + metrics['css_files'] + metrics['js_files']
        
        if not findings:
            return f"✅ UX architecture analysis complete: No violations found in {total_files} files"
        
        return (
            f"⚠️ UX architecture analysis complete: "
            f"{metrics['total_findings']} violations found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {total_files} UX files"
        )