"""
Base Agent Interface for Feng Shui Multi-Agent System

Defines common interface and data structures for all specialized agents.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """
    Single issue found by agent
    
    Enhanced in v4.34 with actionable reporting fields:
    - code_snippet_with_context: Code showing issue (with line numbers)
    - issue_explanation: WHY this is problematic
    - fix_example: Concrete fix with before/after code
    - impact_estimate: Expected benefit (e.g., "10-20% speedup")
    - effort_estimate: Time to fix (e.g., "30 min")
    """
    category: str           # e.g., "DI Violation", "SQL Injection", etc.
    severity: Severity
    file_path: Path
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None  # Legacy: single line only
    
    # NEW in v4.34: Actionable reporting fields
    code_snippet_with_context: Optional[str] = None  # Multi-line with context
    issue_explanation: Optional[str] = None          # WHY problematic
    fix_example: Optional[str] = None                # Concrete fix code
    impact_estimate: Optional[str] = None            # Performance/quality gain
    effort_estimate: Optional[str] = None            # Time to implement fix
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = {
            'category': self.category,
            'severity': self.severity.value,
            'file_path': str(self.file_path),
            'line_number': self.line_number,
            'description': self.description,
            'recommendation': self.recommendation,
            'code_snippet': self.code_snippet
        }
        
        # Add new fields if present (backward compatible)
        if self.code_snippet_with_context:
            result['code_snippet_with_context'] = self.code_snippet_with_context
        if self.issue_explanation:
            result['issue_explanation'] = self.issue_explanation
        if self.fix_example:
            result['fix_example'] = self.fix_example
        if self.impact_estimate:
            result['impact_estimate'] = self.impact_estimate
        if self.effort_estimate:
            result['effort_estimate'] = self.effort_estimate
        
        return result


@dataclass
class AgentReport:
    """Report from single agent analysis"""
    agent_name: str
    module_path: Path
    execution_time_seconds: float
    findings: List[Finding] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    summary: str = ""
    
    def get_critical_count(self) -> int:
        """Count CRITICAL findings"""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
    
    def get_high_count(self) -> int:
        """Count HIGH findings"""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)
    
    def get_medium_count(self) -> int:
        """Count MEDIUM findings"""
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
    
    def get_low_count(self) -> int:
        """Count LOW findings"""
        return sum(1 for f in self.findings if f.severity == Severity.LOW)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'agent_name': self.agent_name,
            'module_path': str(self.module_path),
            'execution_time_seconds': self.execution_time_seconds,
            'findings': [f.to_dict() for f in self.findings],
            'metrics': self.metrics,
            'summary': self.summary
        }


class BaseAgent(ABC):
    """
    Abstract base class for specialized Feng Shui agents
    
    Each agent specializes in a specific domain:
    - ArchitectAgent: Architecture patterns & design
    - SecurityAgent: Security best practices
    - PerformanceAgent: Performance optimization
    - DocumentationAgent: Documentation quality
    """
    
    def __init__(self, name: str):
        """
        Initialize agent
        
        Args:
            name: Agent name (e.g., 'architect', 'security')
        """
        self.name = name
        self.logger = logging.getLogger(f"fengshui.agents.{name}")
    
    @abstractmethod
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module and generate report
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with findings and metrics
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of what this agent can detect
        
        Returns:
            List of capability descriptions
        """
        pass
    
    def validate_module_path(self, module_path: Path) -> bool:
        """
        Validate module path exists and is analyzable
        
        Args:
            module_path: Path to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not module_path.exists():
            self.logger.error(f"Module path does not exist: {module_path}")
            return False
        
        if not module_path.is_dir():
            self.logger.error(f"Module path is not a directory: {module_path}")
            return False
        
        return True
    
    def _create_empty_report(self, module_path: Path, reason: str = "Invalid module path") -> AgentReport:
        """
        Create empty report for invalid modules
        
        Args:
            module_path: Path that was analyzed
            reason: Reason for empty report
            
        Returns:
            Empty AgentReport
        """
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=0.0,
            findings=[],
            metrics={},
            summary=reason
        )