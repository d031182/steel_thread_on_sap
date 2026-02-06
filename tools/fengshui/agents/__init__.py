"""
Feng Shui Multi-Agent System

Specialized agents for comprehensive architecture analysis:
- ArchitectAgent: Architecture patterns & design
- SecurityAgent: Security best practices
- UXArchitectAgent: SAP Fiori/SAPUI5 UX compliance
- PerformanceAgent: Performance optimization
- DocumentationAgent: Documentation quality
"""

from .base_agent import (
    BaseAgent,
    Finding,
    Severity,
    AgentReport
)
from .architect_agent import ArchitectAgent
from .security_agent import SecurityAgent
from .ux_architect_agent import UXArchitectAgent
from .file_organization_agent import FileOrganizationAgent
from .performance_agent import PerformanceAgent
from .documentation_agent import DocumentationAgent
from .orchestrator import AgentOrchestrator, ComprehensiveReport, SynthesizedPlan

__all__ = [
    'BaseAgent',
    'Finding',
    'Severity',
    'AgentReport',
    'ArchitectAgent',
    'SecurityAgent',
    'UXArchitectAgent',
    'FileOrganizationAgent',
    'PerformanceAgent',
    'DocumentationAgent',
    'AgentOrchestrator',
    'ComprehensiveReport',
    'SynthesizedPlan'
]
