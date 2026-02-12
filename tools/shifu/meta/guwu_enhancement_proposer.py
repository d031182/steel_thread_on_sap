"""
Shi Fu Gu Wu Enhancement Proposer

Generates enhancement proposals for Gu Wu testing framework gaps.

Philosophy:
"The master teaches the testing disciple to improve continuously."

Similar to Feng Shui enhancement consultation, but focused on:
- Test framework gaps (missing test types)
- Intelligence engine improvements
- Test generation strategies
- Coverage analysis enhancements
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json


@dataclass
class GuWuCapability:
    """Represents a Gu Wu capability/component"""
    name: str
    purpose: str
    scope: List[str]
    examples: List[str]  # Example enhancements
    current_features: List[str]
    fits_criteria: List[str]  # Keywords that indicate this capability should handle
    does_not_fit: List[str]  # What this capability should NOT handle


# Registry of Gu Wu capabilities
GUWU_CAPABILITIES = {
    "TestGeneration": GuWuCapability(
        name="TestGeneration",
        purpose="Generates new tests automatically from code analysis",
        scope=[
            "Test file creation",
            "Test case generation from code structure",
            "AAA pattern test scaffolding",
            "Fixture generation",
            "Mock object creation"
        ],
        examples=[
            "Generate unit tests for new service class",
            "Create integration tests for API endpoints",
            "Auto-generate fixtures from database schema",
            "Generate E2E tests for user workflows"
        ],
        current_features=[
            "App V2 test generator (modules/frontend)",
            "Test scaffolding with AAA pattern",
            "Pytest marks (unit/integration/e2e)",
            "Module-aware test generation"
        ],
        fits_criteria=[
            "generate", "create", "scaffold", "test", "coverage gap",
            "untested", "missing test", "no test", "test creation"
        ],
        does_not_fit=[
            "fix failing test", "improve test performance", "flaky test",
            "test execution", "test reporting", "analyze metrics"
        ]
    ),
    
    "IntelligenceEngine": GuWuCapability(
        name="IntelligenceEngine",
        purpose="Analyzes test execution patterns and provides insights",
        scope=[
            "Test metrics analysis",
            "Flaky test detection",
            "Performance trend analysis",
            "Coverage analysis",
            "Predictive analytics",
            "Recommendations generation"
        ],
        examples=[
            "Improve flaky test detection algorithm",
            "Add new recommendation types",
            "Enhance predictive failure model",
            "Add test health dashboard metrics"
        ],
        current_features=[
            "8 recommendation types",
            "Flaky test scoring (transition-based)",
            "Slow test detection (>5s)",
            "Coverage gap identification",
            "ML failure prediction",
            "Pre-flight checks"
        ],
        fits_criteria=[
            "intelligence", "insight", "recommendation", "predict",
            "analyze", "metrics", "dashboard", "health", "trend",
            "flaky", "slow", "pattern", "learn"
        ],
        does_not_fit=[
            "generate test", "create test", "write test",
            "execute test", "run test"
        ]
    ),
    
    "TestExecution": GuWuCapability(
        name="TestExecution",
        purpose="Manages test execution, prioritization, and optimization",
        scope=[
            "Test runner integration",
            "Parallel execution",
            "Test prioritization",
            "Execution hooks (pre/post)",
            "Result collection"
        ],
        examples=[
            "Improve parallel test execution",
            "Add test sharding support",
            "Optimize test order based on history",
            "Add custom pytest hooks"
        ],
        current_features=[
            "Pytest integration",
            "Auto-prioritization (likely-to-fail first)",
            "Frontend + Backend unified execution",
            "Human-readable error plugin",
            "Coverage collection"
        ],
        fits_criteria=[
            "execution", "run", "parallel", "priority", "order",
            "performance", "speed", "optimize execution", "hook"
        ],
        does_not_fit=[
            "generate test", "analyze metrics", "recommendation"
        ]
    ),
    
    "TestFramework": GuWuCapability(
        name="TestFramework",
        purpose="Core testing infrastructure and utilities",
        scope=[
            "Test fixtures",
            "Test utilities",
            "Assertion helpers",
            "Mock factories",
            "Test data builders"
        ],
        examples=[
            "Add new shared fixtures",
            "Create assertion helper for common patterns",
            "Build mock factory for complex objects",
            "Add test data builders"
        ],
        current_features=[
            "conftest.py fixtures",
            "Shared test utilities",
            "Database fixtures",
            "Module fixtures"
        ],
        fits_criteria=[
            "fixture", "utility", "helper", "mock", "factory",
            "test data", "builder", "shared", "common"
        ],
        does_not_fit=[
            "test execution", "metrics", "intelligence"
        ]
    )
}


def get_guwu_capability(issue_description: str) -> Optional[str]:
    """
    Determine which Gu Wu capability should handle the issue
    
    Args:
        issue_description: Description of the gap/enhancement
        
    Returns:
        Capability name or None
    """
    issue_lower = issue_description.lower()
    
    best_match = None
    best_score = 0.0
    
    for capability_name, capability in GUWU_CAPABILITIES.items():
        score = 0.0
        
        # Check fit criteria (positive matches)
        for criterion in capability.fits_criteria:
            if criterion.lower() in issue_lower:
                score += 2.0  # Strong positive signal
        
        # Check does_not_fit (negative matches)
        for exclusion in capability.does_not_fit:
            if exclusion.lower() in issue_lower:
                score -= 1.0  # Negative signal
        
        # Check examples (moderate positive)
        for example in capability.examples:
            if any(word in issue_lower for word in example.lower().split()):
                score += 1.0
        
        if score > best_score:
            best_score = score
            best_match = capability_name
    
    return best_match if best_score > 0 else None


@dataclass
class GuWuEnhancementProposal:
    """Proposal for Gu Wu enhancement"""
    proposal_id: str
    date_created: str
    capability: str  # Which capability handles this
    title: str
    problem_statement: str
    proposed_solution: str
    implementation_steps: List[str]
    effort_estimate: str  # e.g., "2-3 hours"
    priority: str  # P0/P1/P2/P3
    confidence: float  # How confident we are this fits the capability


class GuWuEnhancementProposer:
    """
    Generates enhancement proposals for Gu Wu testing framework
    
    Similar to Feng Shui enhancement proposer, but focused on testing:
    - Missing test types (E2E, performance, security)
    - Intelligence engine improvements
    - Test generation strategies
    - Framework utilities
    """
    
    def __init__(self, proposals_dir: Optional[Path] = None):
        """
        Initialize proposer
        
        Args:
            proposals_dir: Directory to save proposals
                          (default: docs/guwu-proposals/)
        """
        self.proposals_dir = proposals_dir or Path("docs/guwu-proposals")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_gap(
        self,
        issue_description: str,
        user_notes: Optional[str] = None
    ) -> GuWuEnhancementProposal:
        """
        Analyze a Gu Wu gap and generate enhancement proposal
        
        Args:
            issue_description: Description of the testing gap
            user_notes: Additional context from user
            
        Returns:
            GuWuEnhancementProposal object
        """
        # Determine capability
        capability = get_guwu_capability(issue_description)
        
        if not capability:
            capability = "TestFramework"  # Default fallback
        
        # Generate proposal
        proposal_id = self._generate_proposal_id(capability)
        
        # Create basic proposal structure
        proposal = GuWuEnhancementProposal(
            proposal_id=proposal_id,
            date_created=datetime.now().strftime("%Y-%m-%d"),
            capability=capability,
            title=self._generate_title(issue_description),
            problem_statement=issue_description,
            proposed_solution=self._generate_solution(capability, issue_description),
            implementation_steps=self._generate_steps(capability),
            effort_estimate=self._estimate_effort(capability, issue_description),
            priority=self._estimate_priority(issue_description),
            confidence=self._calculate_confidence(capability, issue_description)
        )
        
        return proposal
    
    def _generate_proposal_id(self, capability: str) -> str:
        """Generate unique proposal ID"""
        date_str = datetime.now().strftime("%Y%m%d")
        prefix = capability[:4].upper()
        return f"{date_str}-{prefix}-{capability.lower()[:10]}"
    
    def _generate_title(self, issue: str) -> str:
        """Generate concise title from issue"""
        # Take first 60 chars
        return issue[:60] + ("..." if len(issue) > 60 else "")
    
    def _generate_solution(self, capability: str, issue: str) -> str:
        """Generate proposed solution based on capability"""
        cap_obj = GUWU_CAPABILITIES.get(capability)
        if not cap_obj:
            return f"Implement enhancement for {issue}"
        
        return f"Enhance {capability} to handle: {issue}"
    
    def _generate_steps(self, capability: str) -> List[str]:
        """Generate implementation steps"""
        return [
            f"1. Analyze current {capability} implementation",
            "2. Design enhancement architecture",
            "3. Implement core functionality",
            "4. Write unit tests (Gu Wu standards)",
            "5. Integrate with existing system",
            "6. Validate with real test cases",
            "7. Update documentation"
        ]
    
    def _estimate_effort(self, capability: str, issue: str) -> str:
        """Estimate implementation effort"""
        issue_lower = issue.lower()
        
        if "new" in issue_lower or "create" in issue_lower:
            return "4-6 hours"  # New features take longer
        elif "improve" in issue_lower or "enhance" in issue_lower:
            return "2-3 hours"  # Improvements are faster
        else:
            return "3-4 hours"  # Default estimate
    
    def _estimate_priority(self, issue: str) -> str:
        """Estimate priority based on keywords"""
        issue_lower = issue.lower()
        
        if any(word in issue_lower for word in ["critical", "broken", "failing"]):
            return "P0"
        elif any(word in issue_lower for word in ["flaky", "slow", "coverage"]):
            return "P1"
        elif any(word in issue_lower for word in ["improve", "enhance", "optimize"]):
            return "P2"
        else:
            return "P3"
    
    def _calculate_confidence(self, capability: str, issue: str) -> float:
        """Calculate confidence that this capability should handle issue"""
        cap_obj = GUWU_CAPABILITIES.get(capability)
        if not cap_obj:
            return 0.5
        
        issue_lower = issue.lower()
        score = 0.0
        total_checks = 0
        
        # Check fit criteria
        for criterion in cap_obj.fits_criteria:
            total_checks += 1
            if criterion.lower() in issue_lower:
                score += 1.0
        
        # Check examples
        for example in cap_obj.examples:
            total_checks += 1
            if any(word in issue_lower for word in example.lower().split()):
                score += 0.5
        
        return score / total_checks if total_checks > 0 else 0.5
    
    def save_proposal(self, proposal: GuWuEnhancementProposal) -> Path:
        """Save proposal to markdown file"""
        file_path = self.proposals_dir / f"{proposal.proposal_id}.md"
        
        content = f"""# Gu Wu Enhancement Proposal: {proposal.title}

**Proposal ID**: {proposal.proposal_id}  
**Date**: {proposal.date_created}  
**Capability**: {proposal.capability}  
**Priority**: {proposal.priority}  
**Effort**: {proposal.effort_estimate}  
**Confidence**: {proposal.confidence:.2f}

## Problem Statement

{proposal.problem_statement}

## Proposed Solution

{proposal.proposed_solution}

## Implementation Steps

{chr(10).join(proposal.implementation_steps)}

## Acceptance Criteria

- [ ] Core functionality implemented
- [ ] Unit tests written and passing (Gu Wu standards)
- [ ] Integration tests if applicable
- [ ] Documentation updated
- [ ] Performance validated
- [ ] No test pyramid violations (70/20/10 ratio maintained)

## Testing Strategy

- Unit tests: Test core logic in isolation
- Integration tests: Test with real test suite
- Validation: Run on actual codebase

## Capability Details

**{proposal.capability}**:
{GUWU_CAPABILITIES[proposal.capability].purpose if proposal.capability in GUWU_CAPABILITIES else 'N/A'}

## Status

- [ ] Proposal reviewed
- [ ] Implementation approved
- [ ] Work in progress
- [ ] Completed
- [ ] Validated
"""
        
        file_path.write_text(content, encoding='utf-8')
        return file_path


def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.shifu.meta.guwu_enhancement_proposer '<issue description>'")
        print()
        print("Example:")
        print('  python -m tools.shifu.meta.guwu_enhancement_proposer "Add E2E test support for Playwright"')
        sys.exit(1)
    
    issue = sys.argv[1]
    
    print("=" * 60)
    print("Shi Fu Gu Wu Enhancement Proposer")
    print("=" * 60)
    print()
    print(f"Analyzing: {issue}")
    print()
    
    proposer = GuWuEnhancementProposer()
    proposal = proposer.analyze_gap(issue)
    
    print(f"✅ Proposal Generated!")
    print(f"   ID: {proposal.proposal_id}")
    print(f"   Capability: {proposal.capability}")
    print(f"   Priority: {proposal.priority}")
    print(f"   Effort: {proposal.effort_estimate}")
    print(f"   Confidence: {proposal.confidence:.2f}")
    print()
    
    file_path = proposer.save_proposal(proposal)
    print(f"📄 Proposal saved to: {file_path}")
    print()
    print("Next steps:")
    print(f"1. Review proposal: code {file_path}")
    print("2. Decide: Approve, Modify, or Reject")
    print("3. If approved: Implement enhancement")


if __name__ == "__main__":
    main()