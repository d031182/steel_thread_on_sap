"""
Preview Engine - Core validation orchestrator for Feng Shui Preview Mode

Coordinates validators and generates lightweight architecture feedback
during planning phase (before implementation).
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class Severity(Enum):
    """Finding severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class PreviewFinding:
    """Architecture finding from preview validation"""
    severity: Severity
    category: str
    message: str
    location: str
    suggestion: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'severity': self.severity.value,
            'category': self.category,
            'message': self.message,
            'location': self.location,
            'suggestion': self.suggestion
        }


@dataclass
class PreviewResult:
    """Result of preview validation"""
    module_name: str
    findings: List[PreviewFinding]
    validation_time_seconds: float
    validators_run: List[str]
    
    @property
    def has_blockers(self) -> bool:
        """Check if any CRITICAL or HIGH findings exist"""
        return any(
            f.severity in (Severity.CRITICAL, Severity.HIGH)
            for f in self.findings
        )
    
    @property
    def finding_counts(self) -> Dict[str, int]:
        """Count findings by severity"""
        counts = {s.value: 0 for s in Severity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'module_name': self.module_name,
            'findings': [f.to_dict() for f in self.findings],
            'validation_time_seconds': self.validation_time_seconds,
            'validators_run': self.validators_run,
            'has_blockers': self.has_blockers,
            'finding_counts': self.finding_counts
        }


class PreviewEngine:
    """
    Core engine for Preview Mode validation
    
    Orchestrates lightweight validators that check design documents
    and planned module structure BEFORE implementation starts.
    
    Target: <5 seconds execution time
    Accuracy: 80%+ common violations detected
    """
    
    def __init__(self, validators: List[Any] = None):
        """
        Initialize preview engine
        
        Args:
            validators: List of validator instances (NamingValidator, etc.)
        """
        self.validators = validators or []
        
    def validate_design(self, design_spec: Dict[str, Any]) -> PreviewResult:
        """
        Validate module design specification
        
        Args:
            design_spec: Dictionary containing:
                - module_name: str
                - module_id: str (optional)
                - routes: List[str] (optional)
                - api_endpoints: List[Dict] (optional)
                - dependencies: List[str] (optional)
                - structure: Dict (optional)
        
        Returns:
            PreviewResult with findings from all validators
        """
        import time
        
        start_time = time.time()
        module_name = design_spec.get('module_name', 'unknown')
        
        all_findings = []
        validators_run = []
        
        # Run each validator
        for validator in self.validators:
            try:
                findings = validator.validate(design_spec)
                all_findings.extend(findings)
                validators_run.append(validator.__class__.__name__)
            except Exception as e:
                # Log error but continue with other validators
                all_findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='validator_error',
                    message=f"Validator {validator.__class__.__name__} failed: {str(e)}",
                    location=module_name,
                    suggestion="Check validator configuration"
                ))
        
        validation_time = time.time() - start_time
        
        return PreviewResult(
            module_name=module_name,
            findings=all_findings,
            validation_time_seconds=validation_time,
            validators_run=validators_run
        )
    
    def format_output(self, result: PreviewResult, verbose: bool = False) -> str:
        """
        Format preview result for console output
        
        Args:
            result: PreviewResult to format
            verbose: Include full details
        
        Returns:
            Formatted string output
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"🔍 Feng Shui Preview Mode - {result.module_name}")
        lines.append("=" * 80)
        lines.append(f"⏱️  Validation Time: {result.validation_time_seconds:.2f}s")
        lines.append(f"✅ Validators Run: {', '.join(result.validators_run)}")
        lines.append("")
        
        # Summary
        counts = result.finding_counts
        lines.append("📊 Findings Summary:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = counts[severity]
            if count > 0:
                emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 
                        'LOW': '🔵', 'INFO': '⚪'}[severity]
                lines.append(f"   {emoji} {severity}: {count}")
        
        if result.has_blockers:
            lines.append("")
            lines.append("⚠️  BLOCKERS DETECTED - Review findings before implementation")
        
        # Findings
        if result.findings:
            lines.append("")
            lines.append("📋 Detailed Findings:")
            lines.append("-" * 80)
            
            for i, finding in enumerate(result.findings, 1):
                emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 
                        'LOW': '🔵', 'INFO': '⚪'}[finding.severity.value]
                
                lines.append(f"\n{i}. {emoji} [{finding.severity.value}] {finding.category}")
                lines.append(f"   Location: {finding.location}")
                lines.append(f"   Issue: {finding.message}")
                lines.append(f"   💡 Suggestion: {finding.suggestion}")
        else:
            lines.append("")
            lines.append("✅ No violations detected - Architecture looks good!")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)