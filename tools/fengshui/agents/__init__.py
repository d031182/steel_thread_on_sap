"""
Feng Shui Multi-Agent System

Specialized agents for comprehensive architecture analysis:
- ArchitectAgent: Backend architecture patterns & design (DI, SOLID, GoF)
- UXArchitectAgent: SAP Fiori/SAPUI5 UX architecture & guidelines
- SecurityAgent: Security best practices (coming soon)
- PerformanceAgent: Performance optimization (coming soon)
- DocumentationAgent: Documentation quality (coming soon)
"""

from .base_agent import BaseAgent, AgentReport, Finding, Severity
from .architect_agent import ArchitectAgent
from .ux_architect_agent import UXArchitectAgent
from .security_agent import SecurityAgent
from .file_organization_agent import FileOrganizationAgent

# Coming soon:
# from .performance_agent import PerformanceAgent
# from .documentation_agent import DocumentationAgent
# from .orchestrator import AgentOrchestrator, ComprehensiveReport, SynthesizedPlan

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentReport',
    'Finding',
    'Severity',
    
    # Specialized agents (implemented)
    'ArchitectAgent',
    'UXArchitectAgent',
    'SecurityAgent',
    'FileOrganizationAgent',
    
    # Specialized agents (coming soon)
    # 'PerformanceAgent',
    # 'DocumentationAgent',
    
    # Orchestration (coming soon)
    # 'AgentOrchestrator',
    # 'ComprehensiveReport',
    # 'SynthesizedPlan',
]