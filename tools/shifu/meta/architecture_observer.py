"""
Shi Fu Architecture Observer

Runs Feng Shui ON Feng Shui itself to discover capability gaps automatically.

Philosophy:
"The master observes their own practice to identify areas for improvement."

Workflow:
1. Run Feng Shui analysis on tools/fengshui/ directory
2. Capture violations that Feng Shui CANNOT detect
3. Generate enhancement proposals for missing capabilities
4. Track which gaps are real vs false positives
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json

from .agent_registry import get_agent_for_issue, AGENT_PURPOSES
from .enhancement_proposer import EnhancementProposer, EnhancementProposal


@dataclass
class ObservedGap:
    """Represents a capability gap discovered by observing Feng Shui"""
    gap_id: str
    date_discovered: str
    gap_type: str  # "missing_detector", "false_negative", "coverage_gap"
    description: str
    evidence: str  # What we found that Feng Shui missed
    file_path: str  # Where the issue was found
    suggested_agent: str  # Which agent should handle this
    confidence: float  # How confident we are this is a real gap (0.0-1.0)
    status: str  # "OBSERVED", "PROPOSED", "APPROVED", "REJECTED", "IMPLEMENTED"


class ArchitectureObserver:
    """
    Observes Feng Shui's own architecture to discover capability gaps
    
    Key Insight:
    By running Feng Shui on itself, we can discover:
    - Issues Feng Shui should catch but doesn't
    - Missing detector patterns
    - Coverage gaps in agent capabilities
    """
    
    def __init__(
        self,
        fengshui_dir: Optional[Path] = None,
        gaps_db_path: Optional[Path] = None
    ):
        """
        Initialize observer
        
        Args:
            fengshui_dir: Path to Feng Shui source (default: tools/fengshui/)
            gaps_db_path: Path to gaps database (default: tools/shifu/meta/observed_gaps.json)
        """
        self.fengshui_dir = fengshui_dir or Path("tools/fengshui")
        self.gaps_db_path = gaps_db_path or Path("tools/shifu/meta/observed_gaps.json")
        self.proposer = EnhancementProposer()
        
        # Load existing gaps
        self.observed_gaps: Dict[str, ObservedGap] = self._load_gaps()
    
    def observe_architecture(self) -> Dict[str, any]:
        """
        Run Feng Shui on itself to discover capability gaps
        
        Returns:
            {
                "gaps_discovered": List[ObservedGap],
                "total_gaps": int,
                "new_gaps": int,
                "proposals_generated": int,
                "timestamp": str
            }
        """
        print("=" * 60)
        print("Shi Fu Architecture Observer")
        print("Running Feng Shui on Feng Shui itself...")
        print("=" * 60)
        print()
        
        # 1. Analyze Feng Shui source code
        gaps_discovered = self._analyze_fengshui_source()
        
        # 2. Filter out known gaps
        new_gaps = [gap for gap in gaps_discovered 
                   if gap.gap_id not in self.observed_gaps]
        
        # 3. Generate proposals for high-confidence gaps
        proposals_generated = 0
        for gap in new_gaps:
            if gap.confidence >= 0.6:  # High confidence threshold
                proposal = self._generate_proposal_from_gap(gap)
                if proposal:
                    proposals_generated += 1
                    print(f"📄 Generated proposal: {proposal.proposal_id}")
        
        # 4. Save gaps to database
        for gap in gaps_discovered:
            self.observed_gaps[gap.gap_id] = gap
        self._save_gaps()
        
        # 5. Generate summary
        summary = {
            "gaps_discovered": gaps_discovered,
            "total_gaps": len(self.observed_gaps),
            "new_gaps": len(new_gaps),
            "proposals_generated": proposals_generated,
            "timestamp": datetime.now().isoformat()
        }
        
        print()
        print("=" * 60)
        print("Observation Complete")
        print("=" * 60)
        print(f"Total gaps tracked: {summary['total_gaps']}")
        print(f"New gaps found: {summary['new_gaps']}")
        print(f"Proposals generated: {summary['proposals_generated']}")
        print()
        
        return summary
    
    def _analyze_fengshui_source(self) -> List[ObservedGap]:
        """
        Analyze Feng Shui source code to find gaps
        
        This is where the magic happens - we look for patterns that
        Feng Shui SHOULD catch but doesn't.
        """
        gaps = []
        
        # 1. Check for empty directories
        gaps.extend(self._check_empty_directories())
        
        # 2. Check for complex detectors (potential performance issues)
        gaps.extend(self._check_complex_detectors())
        
        # 3. Check for missing docstrings in detectors
        gaps.extend(self._check_missing_docstrings())
        
        # 4. Check for duplicate code patterns
        gaps.extend(self._check_duplicate_patterns())
        
        # 5. Check for missing unit tests
        gaps.extend(self._check_missing_tests())
        
        return gaps
    
    def _check_empty_directories(self) -> List[ObservedGap]:
        """Check for empty directories (your use case!)"""
        gaps = []
        
        # Scan all directories recursively
        artifact_files = {'__pycache__', '.DS_Store', 'Thumbs.db', '.pytest_cache'}
        
        for dir_path in self.fengshui_dir.rglob("*"):
            if not dir_path.is_dir():
                continue
            
            # Get directory contents
            contents = list(dir_path.iterdir())
            if not contents:
                # Completely empty directory
                gap = ObservedGap(
                    gap_id=f"empty_dir_{dir_path.name}_{datetime.now().strftime('%Y%m%d')}",
                    date_discovered=datetime.now().strftime("%Y-%m-%d"),
                    gap_type="missing_detector",
                    description="Empty directory with no files",
                    evidence=f"Directory {dir_path} is completely empty",
                    file_path=str(dir_path.relative_to(Path.cwd())),
                    suggested_agent="FileOrganizationAgent",
                    confidence=0.8,
                    status="OBSERVED"
                )
                gaps.append(gap)
            
            # Check if only artifacts
            non_artifact_files = [f for f in contents if f.name not in artifact_files]
            if contents and not non_artifact_files:
                gap = ObservedGap(
                    gap_id=f"artifact_only_dir_{dir_path.name}_{datetime.now().strftime('%Y%m%d')}",
                    date_discovered=datetime.now().strftime("%Y-%m-%d"),
                    gap_type="missing_detector",
                    description="Directory contains only build artifacts (__pycache__, .DS_Store, etc.)",
                    evidence=f"Directory {dir_path} contains only: {[f.name for f in contents]}",
                    file_path=str(dir_path.relative_to(Path.cwd())),
                    suggested_agent="FileOrganizationAgent",
                    confidence=0.9,
                    status="OBSERVED"
                )
                gaps.append(gap)
        
        return gaps
    
    def _check_complex_detectors(self) -> List[ObservedGap]:
        """Check for overly complex detector methods"""
        gaps = []
        
        # Scan agent files
        for agent_file in self.fengshui_dir.glob("agents/*_agent.py"):
            try:
                content = agent_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Find detector methods
                in_detector = False
                detector_name = ""
                detector_lines = 0
                detector_start_line = 0
                
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("def _detect_"):
                        in_detector = True
                        detector_name = line.split("def ")[1].split("(")[0]
                        detector_start_line = i
                        detector_lines = 0
                    elif in_detector:
                        if line.strip().startswith("def ") and not line.strip().startswith("def _"):
                            # End of detector
                            if detector_lines > 100:  # Threshold for "complex"
                                gap = ObservedGap(
                                    gap_id=f"complex_detector_{detector_name}_{datetime.now().strftime('%Y%m%d')}",
                                    date_discovered=datetime.now().strftime("%Y-%m-%d"),
                                    gap_type="coverage_gap",
                                    description=f"Detector {detector_name} is overly complex ({detector_lines} lines)",
                                    evidence=f"Detector spans lines {detector_start_line}-{i} in {agent_file.name}",
                                    file_path=str(agent_file.relative_to(Path.cwd())),
                                    suggested_agent="PerformanceAgent",
                                    confidence=0.7,
                                    status="OBSERVED"
                                )
                                gaps.append(gap)
                            in_detector = False
                        else:
                            detector_lines += 1
            except Exception as e:
                # Skip files that can't be read
                pass
        
        return gaps
    
    def _check_missing_docstrings(self) -> List[ObservedGap]:
        """Check for detectors without docstrings"""
        gaps = []
        
        for agent_file in self.fengshui_dir.glob("agents/*_agent.py"):
            try:
                content = agent_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if line.strip().startswith("def _detect_"):
                        detector_name = line.split("def ")[1].split("(")[0]
                        # Check if next non-empty line is a docstring
                        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                        
                        if not next_line.startswith('"""') and not next_line.startswith("'''"):
                            gap = ObservedGap(
                                gap_id=f"missing_docstring_{detector_name}_{datetime.now().strftime('%Y%m%d')}",
                                date_discovered=datetime.now().strftime("%Y-%m-%d"),
                                gap_type="missing_detector",
                                description=f"Detector {detector_name} missing docstring",
                                evidence=f"Function at line {i+1} in {agent_file.name} has no docstring",
                                file_path=str(agent_file.relative_to(Path.cwd())),
                                suggested_agent="DocumentationAgent",
                                confidence=0.6,
                                status="OBSERVED"
                            )
                            gaps.append(gap)
            except Exception:
                pass
        
        return gaps
    
    def _check_duplicate_patterns(self) -> List[ObservedGap]:
        """Check for duplicate code patterns across agents"""
        # Simplified version - just check for similar detector names
        gaps = []
        
        detector_patterns = {}  # pattern -> [agent_files]
        
        for agent_file in self.fengshui_dir.glob("agents/*_agent.py"):
            try:
                content = agent_file.read_text(encoding='utf-8')
                # Extract detector names
                for line in content.split('\n'):
                    if line.strip().startswith("def _detect_"):
                        detector_name = line.split("def ")[1].split("(")[0]
                        # Extract pattern (e.g., "di_violations" from "_detect_di_violations")
                        pattern = detector_name.replace("_detect_", "")
                        
                        if pattern not in detector_patterns:
                            detector_patterns[pattern] = []
                        detector_patterns[pattern].append(agent_file.name)
            except Exception:
                pass
        
        # Find duplicate patterns
        for pattern, files in detector_patterns.items():
            if len(files) > 1:
                gap = ObservedGap(
                    gap_id=f"duplicate_pattern_{pattern}_{datetime.now().strftime('%Y%m%d')}",
                    date_discovered=datetime.now().strftime("%Y-%m-%d"),
                    gap_type="coverage_gap",
                    description=f"Duplicate detector pattern '{pattern}' across agents",
                    evidence=f"Pattern found in: {', '.join(files)}",
                    file_path="tools/fengshui/agents/",
                    suggested_agent="ArchitectAgent",
                    confidence=0.5,
                    status="OBSERVED"
                )
                gaps.append(gap)
        
        return gaps
    
    def _check_missing_tests(self) -> List[ObservedGap]:
        """Check for detectors without corresponding tests"""
        gaps = []
        
        # Get all detector names
        detectors = set()
        for agent_file in self.fengshui_dir.glob("agents/*_agent.py"):
            try:
                content = agent_file.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.strip().startswith("def _detect_"):
                        detector_name = line.split("def ")[1].split("(")[0]
                        detectors.add(detector_name)
            except Exception:
                pass
        
        # Get all test files
        test_files = set()
        test_dir = Path("tests/unit/tools/fengshui")
        if test_dir.exists():
            for test_file in test_dir.glob("test_*.py"):
                test_files.add(test_file.stem)  # e.g., "test_di_violations"
        
        # Find detectors without tests
        for detector in detectors:
            expected_test_file = f"test_{detector[1:]}"  # Remove leading underscore
            if expected_test_file not in test_files:
                gap = ObservedGap(
                    gap_id=f"missing_test_{detector}_{datetime.now().strftime('%Y%m%d')}",
                    date_discovered=datetime.now().strftime("%Y-%m-%d"),
                    gap_type="coverage_gap",
                    description=f"Detector {detector} has no corresponding unit test",
                    evidence=f"Expected test file: tests/unit/tools/fengshui/{expected_test_file}.py (not found)",
                    file_path="tests/unit/tools/fengshui/",
                    suggested_agent="DocumentationAgent",  # Tests are part of documentation
                    confidence=0.8,
                    status="OBSERVED"
                )
                gaps.append(gap)
        
        return gaps
    
    def _generate_proposal_from_gap(self, gap: ObservedGap) -> Optional[EnhancementProposal]:
        """
        Generate enhancement proposal from observed gap
        
        Args:
            gap: ObservedGap object
            
        Returns:
            EnhancementProposal or None if generation fails
        """
        try:
            # Use Enhancement Proposer to create proposal
            proposal = self.proposer.analyze_gap(
                issue_description=gap.description,
                user_notes=f"Auto-discovered by Architecture Observer\n\nEvidence: {gap.evidence}"
            )
            
            # Update gap status
            gap.status = "PROPOSED"
            
            # Save proposal
            self.proposer.save_proposal(proposal)
            
            return proposal
        except Exception as e:
            print(f"⚠️ Failed to generate proposal for gap {gap.gap_id}: {e}")
            return None
    
    def _load_gaps(self) -> Dict[str, ObservedGap]:
        """Load observed gaps from database"""
        if not self.gaps_db_path.exists():
            return {}
        
        try:
            data = json.loads(self.gaps_db_path.read_text(encoding='utf-8'))
            return {
                gap_id: ObservedGap(**gap_data)
                for gap_id, gap_data in data.items()
            }
        except Exception:
            return {}
    
    def _save_gaps(self):
        """Save observed gaps to database"""
        data = {
            gap_id: {
                'gap_id': gap.gap_id,
                'date_discovered': gap.date_discovered,
                'gap_type': gap.gap_type,
                'description': gap.description,
                'evidence': gap.evidence,
                'file_path': gap.file_path,
                'suggested_agent': gap.suggested_agent,
                'confidence': gap.confidence,
                'status': gap.status
            }
            for gap_id, gap in self.observed_gaps.items()
        }
        
        self.gaps_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.gaps_db_path.write_text(
            json.dumps(data, indent=2),
            encoding='utf-8'
        )
    
    def get_high_confidence_gaps(self, min_confidence: float = 0.7) -> List[ObservedGap]:
        """Get gaps with confidence >= threshold"""
        return [
            gap for gap in self.observed_gaps.values()
            if gap.confidence >= min_confidence and gap.status == "OBSERVED"
        ]
    
    def get_gaps_by_agent(self, agent_name: str) -> List[ObservedGap]:
        """Get all gaps for a specific agent"""
        return [
            gap for gap in self.observed_gaps.values()
            if gap.suggested_agent == agent_name
        ]


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for architecture observer"""
    print("=" * 60)
    print("Shi Fu Architecture Observer")
    print("=" * 60)
    print()
    print("Running Feng Shui on Feng Shui itself...")
    print("(This is meta! 🧘‍♂️)")
    print()
    
    observer = ArchitectureObserver()
    summary = observer.observe_architecture()
    
    print()
    print("=" * 60)
    print("High-Confidence Gaps (>= 0.7)")
    print("=" * 60)
    
    high_conf_gaps = observer.get_high_confidence_gaps()
    if high_conf_gaps:
        for gap in high_conf_gaps:
            print(f"\n{gap.gap_type.upper()}: {gap.description}")
            print(f"  Agent: {gap.suggested_agent}")
            print(f"  Confidence: {gap.confidence:.2f}")
            print(f"  Evidence: {gap.evidence[:100]}...")
    else:
        print("\n✅ No high-confidence gaps found!")
        print("   Feng Shui's architecture is looking good!")
    
    print()
    print("=" * 60)
    print(f"Full report: {observer.gaps_db_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()