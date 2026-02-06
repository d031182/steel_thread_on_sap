"""
Base Agent Interface for Feng Shui Multi-Agent System

Defines common interface and data structures for all specialized agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum
import logging


class Severity(Enum):
    """Issue severity levels (consistent across all agents)"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """
    Single issue found by an agent
    
    Attributes:
        category: Type of issue (e.g., "DI Violation", "SQL Injection")
        severity: Impact level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        file_path: Path to file with issue
        line_number: Line number (None if file-level issue)
        description: Human-readable description of issue
        recommendation: How to fix the issue
        code_snippet: Relevant code (optional)
    """
    category: str
    severity: Severity
    file_path: Path
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'category': self.category,
            'severity': self.severity.value,
            'file_path': str(self.file_path),
            'line_number': self.line_number,
            'description': self.description,
            'recommendation': self.recommendation,
            'code_snippet': self.code_snippet
        }


@dataclass
class AgentReport:
    """
    Report from single agent analysis
    
    Attributes:
        agent_name: Name of agent (architect, security, performance, documentation)
        module_path: Path to analyzed module
        execution_time_seconds: How long analysis took
        findings: List of issues discovered
        metrics: Agent-specific metrics (e.g., files_analyzed, violation_count)
        summary: Human-readable summary
    """
    agent_name: str
    module_path: Path
    execution_time_seconds: float
    findings: List[Finding]
    metrics: Dict[str, float]
    summary: str
    
    def get_critical_count(self) -> int:
        """Count CRITICAL findings"""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
    
    def get_high_count(self) -> int:
        """Count HIGH findings"""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)
    
    def get_medium_count(self) -> int:
        """Count MEDIUM findings"""
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
    
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
    
    All agents follow same interface for consistency and orchestration.
    """
    
    def __init__(self, name: str):
        """
        Initialize agent
        
        Args:
            name: Agent name (e.g., "architect", "security")
        """
        self.name = name
        self.logger = logging.getLogger(f"fengshui.agents.{name}")
    
    @abstractmethod
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module and generate report
        
        This is the main entry point for agent analysis.
        Each agent implements their specialized analysis logic here.
        
        Args:
            module_path: Path to module directory to analyze
            
        Returns:
            AgentReport with findings, metrics, and summary
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of what this agent can detect
        
        Used for:
        - User documentation (what each agent does)
        - Orchestrator decision-making (which agents to run)
        - Capability discovery
        
        Returns:
            List of capability descriptions (human-readable)
        """
        pass
    
    def validate_module_path(self, module_path: Path) -> bool:
        """
        Validate module path exists and is analyzable
        
        Checks:
        - Path exists
        - Path is a directory
        - Path contains Python files (optional, agent-specific)
        
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
    
    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(name='{self.name}')"