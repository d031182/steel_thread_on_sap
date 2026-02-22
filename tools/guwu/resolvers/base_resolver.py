"""
Base Resolver - Abstract interface for issue resolution

All Gu Wu resolvers inherit from this base class.
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any
import logging


class ResolutionStatus(Enum):
    """Status of resolution attempt"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


@dataclass
class ResolutionResult:
    """
    Result of a resolution attempt
    
    Attributes:
        status: Overall resolution status
        findings_resolved: Number of findings successfully resolved
        findings_failed: Number of findings that failed to resolve
        findings_skipped: Number of findings skipped (user choice, safety)
        actions_taken: List of actions performed (for logging/rollback)
        errors: List of errors encountered
        warnings: List of warnings (non-fatal issues)
        dry_run_actions: If dry_run=True, actions that WOULD be taken
    """
    status: ResolutionStatus
    findings_resolved: int = 0
    findings_failed: int = 0
    findings_skipped: int = 0
    actions_taken: List[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    dry_run_actions: List[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.actions_taken is None:
            self.actions_taken = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.dry_run_actions is None:
            self.dry_run_actions = []
    
    @property
    def total_findings(self) -> int:
        """Total number of findings processed"""
        return self.findings_resolved + self.findings_failed + self.findings_skipped
    
    def add_action(self, action: str):
        """Record an action taken"""
        self.actions_taken.append(action)
    
    def add_error(self, error: str):
        """Record an error"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Record a warning"""
        self.warnings.append(warning)
    
    def add_dry_run_action(self, action: str):
        """Record a dry-run action"""
        self.dry_run_actions.append(action)


class BaseResolver(ABC):
    """
    Abstract base class for all Gu Wu resolvers
    
    Resolvers handle specific categories of findings from Feng Shui agents
    and other quality tools. Each resolver:
    
    1. Accepts findings in standard format
    2. Determines which findings it can resolve
    3. Executes resolution actions (with dry-run support)
    4. Returns detailed results
    
    Resolvers follow these principles:
    - SAFETY FIRST: Dry-run by default, require explicit confirmation
    - TRANSPARENCY: Log all actions taken
    - ROLLBACK: Support undo operations where possible
    - SELECTIVE: Allow user to choose which findings to resolve
    """
    
    def __init__(self, resolver_name: str):
        """
        Initialize resolver
        
        Args:
            resolver_name: Unique identifier for this resolver
        """
        self.name = resolver_name
        self.logger = logging.getLogger(f"guwu.resolvers.{resolver_name}")
    
    @abstractmethod
    def can_resolve(self, finding: Any) -> bool:
        """
        Check if this resolver can handle a given finding
        
        Args:
            finding: Finding object from Feng Shui agent
            
        Returns:
            True if this resolver can resolve the finding
        """
        pass
    
    @abstractmethod
    def resolve_finding(self, finding: Any, dry_run: bool = True) -> ResolutionResult:
        """
        Resolve a single finding
        
        Args:
            finding: Finding object to resolve
            dry_run: If True, only simulate actions (default: True for safety)
            
        Returns:
            ResolutionResult with status and details
        """
        pass
    
    def resolve_findings(self, findings: List[Any], dry_run: bool = True, 
                         interactive: bool = False) -> ResolutionResult:
        """
        Resolve multiple findings
        
        Args:
            findings: List of finding objects
            dry_run: If True, only simulate actions
            interactive: If True, prompt user for each finding
            
        Returns:
            Combined ResolutionResult
        """
        combined_result = ResolutionResult(status=ResolutionStatus.SUCCESS)
        
        self.logger.info(f"Processing {len(findings)} findings (dry_run={dry_run}, interactive={interactive})")
        
        for finding in findings:
            # Check if we can resolve this finding
            if not self.can_resolve(finding):
                combined_result.findings_skipped += 1
                combined_result.add_warning(f"Cannot resolve finding: {self._get_finding_description(finding)}")
                continue
            
            # Interactive mode: Ask user
            if interactive and not dry_run:
                if not self._confirm_resolution(finding):
                    combined_result.findings_skipped += 1
                    combined_result.add_warning(f"User skipped finding: {self._get_finding_description(finding)}")
                    continue
            
            # Resolve the finding
            try:
                result = self.resolve_finding(finding, dry_run=dry_run)
                
                # Merge results
                combined_result.findings_resolved += result.findings_resolved
                combined_result.findings_failed += result.findings_failed
                combined_result.findings_skipped += result.findings_skipped
                combined_result.actions_taken.extend(result.actions_taken)
                combined_result.errors.extend(result.errors)
                combined_result.warnings.extend(result.warnings)
                combined_result.dry_run_actions.extend(result.dry_run_actions)
                
            except Exception as e:
                combined_result.findings_failed += 1
                combined_result.add_error(f"Failed to resolve finding: {str(e)}")
                self.logger.error(f"Resolution failed: {str(e)}", exc_info=True)
        
        # Determine overall status
        if combined_result.findings_failed > 0:
            combined_result.status = ResolutionStatus.PARTIAL if combined_result.findings_resolved > 0 else ResolutionStatus.FAILED
        elif combined_result.findings_resolved == 0:
            combined_result.status = ResolutionStatus.SKIPPED
        elif dry_run:
            combined_result.status = ResolutionStatus.DRY_RUN
        else:
            combined_result.status = ResolutionStatus.SUCCESS
        
        self.logger.info(f"Resolution complete: {combined_result.status.value} ({combined_result.findings_resolved} resolved, {combined_result.findings_failed} failed, {combined_result.findings_skipped} skipped)")
        
        return combined_result
    
    def _get_finding_description(self, finding: Any) -> str:
        """
        Get human-readable description of a finding
        
        Args:
            finding: Finding object
            
        Returns:
            String description
        """
        # Try to extract description from common finding formats
        if hasattr(finding, 'description'):
            return finding.description
        elif hasattr(finding, 'message'):
            return finding.message
        elif isinstance(finding, dict) and 'description' in finding:
            return finding['description']
        else:
            return str(finding)
    
    def _confirm_resolution(self, finding: Any) -> bool:
        """
        Ask user to confirm resolution of a finding
        
        Args:
            finding: Finding to confirm
            
        Returns:
            True if user confirms, False otherwise
        """
        description = self._get_finding_description(finding)
        print(f"\n🔍 Finding: {description}")
        
        response = input("Resolve this finding? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of resolver capabilities
        
        Returns:
            List of capability descriptions
        """
        pass