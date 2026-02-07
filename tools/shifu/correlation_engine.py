"""
Correlation Engine: Pattern Detection Across Code and Tests
===========================================================

The Master's wisdom - finding connections between code quality and test quality.

Phase 2 Enhancement: Uses specialized pattern detectors from patterns/ library.
"""

import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

# Import pattern library
from .patterns import (
    BasePattern,
    DIFlakinessPattern,
    ComplexityCoveragePattern,
    SecurityGapsPattern,
    PerformanceTimingPattern,
    ModuleHealthPattern
)
from .patterns.base_pattern import PatternMatch


logger = logging.getLogger(__name__)


@dataclass
class CorrelationPattern:
    """A detected pattern correlating code and test issues (legacy structure)"""
    id: str
    pattern_name: str
    confidence: float  # 0.0-1.0
    severity: str  # URGENT/HIGH/MEDIUM/LOW
    fengshui_evidence: str
    guwu_evidence: str
    root_cause: str
    recommendation: str
    estimated_effort: str
    combined_value: str
    timestamp: str


class CorrelationEngine:
    """
    Pattern detection engine for cross-domain quality issues
    
    Phase 2 Enhancement: Uses pluggable pattern detectors.
    Each pattern is a specialized class that implements BasePattern interface.
    
    Implements Shi Fu's core wisdom: seeing connections between
    code architecture problems and test quality problems.
    """
    
    def __init__(self):
        """Initialize correlation engine with pattern detectors"""
        self.patterns_detected = []
        
        # Initialize pattern detectors
        self.pattern_detectors: List[BasePattern] = [
            DIFlakinessPattern(),
            ComplexityCoveragePattern(),
            SecurityGapsPattern(),
            PerformanceTimingPattern(),
            ModuleHealthPattern()
        ]
        
        logger.info(f"[Correlation Engine] Initialized with {len(self.pattern_detectors)} pattern detectors")
    
    def detect_patterns(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> List[CorrelationPattern]:
        """
        Apply pattern detection algorithms to find correlations
        
        Phase 2: Uses pluggable pattern detectors instead of hardcoded methods.
        
        Args:
            fengshui_data: Code quality data from Feng Shui
            guwu_data: Test quality data from Gu Wu
        
        Returns:
            List of detected correlation patterns
        """
        logger.info("[Correlation Engine] Analyzing cross-domain patterns...")
        
        correlations = []
        
        # Run each pattern detector
        for detector in self.pattern_detectors:
            try:
                logger.debug(f"[Correlation Engine] Running {detector.pattern_name}...")
                
                match = detector.detect(fengshui_data, guwu_data)
                
                if match:
                    # Convert PatternMatch to CorrelationPattern (for backward compatibility)
                    correlation = self._convert_to_correlation_pattern(match)
                    correlations.append(correlation)
                    
                    logger.info(f"[Correlation Engine] ✓ Detected: {match.pattern_name} "
                              f"(confidence: {match.confidence:.2f}, severity: {match.severity})")
                else:
                    logger.debug(f"[Correlation Engine] ✗ No match for {detector.pattern_name}")
                    
            except Exception as e:
                logger.error(f"[Correlation Engine] Error in {detector.pattern_name}: {e}")
                continue
        
        logger.info(f"[Correlation Engine] Detected {len(correlations)} patterns total")
        self.patterns_detected = correlations
        
        return correlations
    
    def _convert_to_correlation_pattern(self, match: PatternMatch) -> CorrelationPattern:
        """
        Convert PatternMatch (from pattern detectors) to CorrelationPattern (legacy format)
        
        Args:
            match: PatternMatch from pattern detector
        
        Returns:
            CorrelationPattern for backward compatibility
        """
        # Convert evidence dicts to strings
        fengshui_evidence_str = self._format_evidence(match.fengshui_evidence)
        guwu_evidence_str = self._format_evidence(match.guwu_evidence)
        
        return CorrelationPattern(
            id=f"{match.pattern_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            pattern_name=match.pattern_name,
            confidence=match.confidence,
            severity=match.severity,
            fengshui_evidence=fengshui_evidence_str,
            guwu_evidence=guwu_evidence_str,
            root_cause=match.root_cause,
            recommendation=match.recommendation,
            estimated_effort=match.estimated_effort,
            combined_value=match.combined_value,
            timestamp=datetime.now().isoformat()
        )
    
    def _format_evidence(self, evidence: Dict) -> str:
        """Format evidence dictionary as readable string"""
        lines = []
        for key, value in evidence.items():
            if isinstance(value, (list, dict)):
                lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def get_prioritized_insights(self) -> List[CorrelationPattern]:
        """
        Get detected patterns sorted by priority
        
        Returns:
            List of patterns sorted by severity and confidence
        """
        severity_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        sorted_patterns = sorted(
            self.patterns_detected,
            key=lambda p: (severity_order.get(p.severity, 3), -p.confidence)
        )
        
        return sorted_patterns
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary of correlation analysis
        
        Returns:
            Dictionary with analysis statistics
        """
        if not self.patterns_detected:
            return {
                'total_patterns': 0,
                'urgent': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'avg_confidence': 0.0
            }
        
        severity_counts = {}
        for pattern in self.patterns_detected:
            severity = pattern.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        avg_confidence = sum(p.confidence for p in self.patterns_detected) / len(self.patterns_detected)
        
        return {
            'total_patterns': len(self.patterns_detected),
            'urgent': severity_counts.get('URGENT', 0),
            'high': severity_counts.get('HIGH', 0),
            'medium': severity_counts.get('MEDIUM', 0),
            'low': severity_counts.get('LOW', 0),
            'avg_confidence': avg_confidence,
            'patterns': [
                {
                    'id': p.id,
                    'name': p.pattern_name,
                    'severity': p.severity,
                    'confidence': p.confidence
                }
                for p in self.patterns_detected
            ]
        }