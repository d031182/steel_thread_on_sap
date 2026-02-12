"""
Shi Fu Enhancement Proposer

Generates proposals for new Feng Shui capabilities based on gaps discovered.

Workflow:
1. User reports: "Feng Shui missed X"
2. Proposer analyzes: Which agent should handle X?
3. Proposer validates: Does X fit agent's purpose?
4. Proposer generates: Complete proposal with implementation plan
5. User reviews and approves

Philosophy:
"The consultant proposes, the user decides, the system implements."
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from .agent_registry import (
    get_agent_for_issue,
    get_agent_purpose,
    validate_enhancement,
    AGENT_PURPOSES
)


@dataclass
class EnhancementProposal:
    """Complete enhancement proposal"""
    proposal_id: str
    date: str
    agent_name: str
    detector_name: str
    issue_description: str
    purpose_fit: Dict[str, any]
    implementation_plan: Dict[str, any]
    estimated_effort: str
    priority: str
    status: str  # "PROPOSED", "APPROVED", "IMPLEMENTED", "REJECTED"


class EnhancementProposer:
    """
    Generates enhancement proposals for Feng Shui agents
    
    Takes user-reported gaps and creates detailed proposals with:
    - Agent routing and validation
    - Detector implementation skeleton
    - Test generation plan
    - Effort estimation
    - Priority scoring
    """
    
    def __init__(self, proposals_dir: Optional[Path] = None):
        """
        Initialize proposer
        
        Args:
            proposals_dir: Directory to store proposals (default: docs/feng-shui-proposals/)
        """
        self.proposals_dir = proposals_dir or Path("docs/feng-shui-proposals")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_gap(self, issue_description: str, user_notes: Optional[str] = None) -> EnhancementProposal:
        """
        Analyze gap and generate complete enhancement proposal
        
        Args:
            issue_description: What Feng Shui missed (e.g., "Empty /app folder")
            user_notes: Optional additional context from user
            
        Returns:
            Complete EnhancementProposal object
            
        Example:
            >>> proposer = EnhancementProposer()
            >>> proposal = proposer.analyze_gap("Empty /app folder with only __pycache__")
            >>> print(proposal.agent_name)  # "FileOrganizationAgent"
        """
        # 1. Route to correct agent
        agent_name = get_agent_for_issue(issue_description)
        if not agent_name:
            # Fallback: Ask user to classify
            agent_name = self._prompt_user_for_agent(issue_description)
        
        # 2. Validate fit
        validation = validate_enhancement(agent_name, issue_description)
        
        # 3. Generate detector name
        detector_name = self._generate_detector_name(issue_description)
        
        # 4. Create implementation plan
        implementation_plan = self._create_implementation_plan(
            agent_name, detector_name, issue_description
        )
        
        # 5. Estimate effort
        effort = self._estimate_effort(implementation_plan)
        
        # 6. Calculate priority
        priority = self._calculate_priority(issue_description, validation)
        
        # 7. Generate proposal ID
        proposal_id = self._generate_proposal_id(agent_name, detector_name)
        
        # 8. Create proposal object
        proposal = EnhancementProposal(
            proposal_id=proposal_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            agent_name=agent_name,
            detector_name=detector_name,
            issue_description=issue_description,
            purpose_fit=validation,
            implementation_plan=implementation_plan,
            estimated_effort=effort,
            priority=priority,
            status="PROPOSED"
        )
        
        return proposal
    
    def generate_proposal_document(self, proposal: EnhancementProposal) -> str:
        """
        Generate markdown proposal document
        
        Args:
            proposal: EnhancementProposal object
            
        Returns:
            Complete markdown document as string
        """
        agent = get_agent_purpose(proposal.agent_name)
        
        doc = f"""# Feng Shui Enhancement Proposal: {proposal.detector_name}

**Proposal ID**: {proposal.proposal_id}  
**Date**: {proposal.date}  
**Status**: {proposal.status}  
**Priority**: {proposal.priority}  
**Estimated Effort**: {proposal.estimated_effort}

---

## 📋 Issue Description

**What Feng Shui Missed**:
{proposal.issue_description}

**User Impact**:
- Feng Shui did not flag this issue
- Manual discovery required
- Could have been caught automatically

---

## 🎯 Proposed Solution

### Agent: {proposal.agent_name}

**Purpose**: {agent.purpose}

**Why This Agent?**
{proposal.purpose_fit['reasoning']}

**Confidence**: {proposal.purpose_fit['confidence']:.2f} ({"STRONG FIT" if proposal.purpose_fit['confidence'] >= 0.5 else "MODERATE FIT" if proposal.purpose_fit['confidence'] >= 0.3 else "WEAK FIT"})

---

## 🛠️ Implementation Plan

### 1. Detector: `{proposal.detector_name}`

**What It Detects**:
{proposal.implementation_plan['detector']['what_it_detects']}

**How It Works**:
{proposal.implementation_plan['detector']['how_it_works']}

**Example Violations**:
```python
{proposal.implementation_plan['detector']['example_violation']}
```

### 2. Implementation Steps

**Files to Modify**:
"""
        
        for file_path, changes in proposal.implementation_plan['files_to_modify'].items():
            doc += f"\n- `{file_path}`\n"
            for change in changes:
                doc += f"  - {change}\n"
        
        doc += f"""
**Files to Create**:
"""
        
        for file_path, purpose in proposal.implementation_plan['files_to_create'].items():
            doc += f"\n- `{file_path}` - {purpose}\n"
        
        doc += f"""
### 3. Testing Plan

**Unit Tests**:
- File: `tests/unit/tools/fengshui/test_{proposal.detector_name}.py`
- Coverage: {proposal.implementation_plan['testing']['unit_test_scenarios']} test scenarios
- Execution time: < 1s

**Integration Tests**:
- Validate detector in full Feng Shui analysis
- Test across multiple modules
- Verify no false positives

---

## 📊 Estimated Effort

**Total**: {proposal.estimated_effort}

**Breakdown**:
"""
        
        for task, time in proposal.implementation_plan['effort_breakdown'].items():
            doc += f"- {task}: {time}\n"
        
        doc += f"""
---

## 🎯 Priority Justification

**Priority**: {proposal.priority}

**Reasoning**:
{proposal.implementation_plan['priority_reasoning']}

**Impact**:
- Improves Feng Shui coverage
- Prevents similar issues in future
- Reduces manual discovery burden

---

## ✅ Acceptance Criteria

**Definition of Done**:
1. ✅ Detector implemented in `{proposal.agent_name}`
2. ✅ Unit tests passing (100% coverage)
3. ✅ Integration test passing
4. ✅ Documentation updated
5. ✅ No false positives on existing codebase
6. ✅ Feng Shui quality gate passing

**Validation**:
```bash
# Run detector on test case
python -c "from pathlib import Path; from tools.fengshui.agents.orchestrator import FengShuiOrchestrator; \\
orchestrator = FengShuiOrchestrator(); \\
report = orchestrator.analyze_module(Path('modules/test_module')); \\
print(report.findings)"
```

---

## 📚 Related Documentation

**Agent Documentation**:
- Purpose: {agent.purpose}
- Existing Detectors: {len(agent.current_detectors)}
- Scope: {', '.join(agent.scope[:3])}

**Similar Detectors**:
"""
        
        for detector in agent.current_detectors[:3]:
            doc += f"- `{detector}`\n"
        
        doc += f"""
---

## 🎬 Next Steps

**For User** (Review & Approve):
1. Review this proposal
2. Decide: Approve, Modify, or Reject
3. If approved: Request AI to implement

**For AI** (After Approval):
1. Implement detector in `{proposal.agent_name}`
2. Write comprehensive unit tests
3. Validate across codebase
4. Update documentation
5. Commit with proposal reference

**For Shi Fu** (After Implementation):
1. Track adoption in quality metrics
2. Validate no false positives
3. Update Agent Registry with new detector

---

## 📝 Decision Log

**Status**: {proposal.status}  
**Date**: {proposal.date}  
**Reviewer**: [Awaiting User Review]  
**Decision**: [Pending]  
**Notes**: [To be added after review]

---

**Proposal Generated by**: Shi Fu Phase 6 Enhancement Consultant  
**Document Version**: 1.0  
**Last Updated**: {proposal.date}
"""
        
        return doc
    
    def save_proposal(self, proposal: EnhancementProposal) -> Path:
        """
        Save proposal to docs/feng-shui-proposals/
        
        Args:
            proposal: EnhancementProposal object
            
        Returns:
            Path to saved proposal file
        """
        filename = f"{proposal.proposal_id}.md"
        filepath = self.proposals_dir / filename
        
        doc = self.generate_proposal_document(proposal)
        filepath.write_text(doc, encoding='utf-8')
        
        # Also save JSON for programmatic access
        json_path = self.proposals_dir / f"{proposal.proposal_id}.json"
        proposal_dict = {
            'proposal_id': proposal.proposal_id,
            'date': proposal.date,
            'agent_name': proposal.agent_name,
            'detector_name': proposal.detector_name,
            'issue_description': proposal.issue_description,
            'estimated_effort': proposal.estimated_effort,
            'priority': proposal.priority,
            'status': proposal.status,
        }
        json_path.write_text(json.dumps(proposal_dict, indent=2), encoding='utf-8')
        
        return filepath
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_detector_name(self, issue_description: str) -> str:
        """Generate detector name from issue description"""
        # Simple heuristic: extract key terms
        desc_lower = issue_description.lower()
        
        if "empty" in desc_lower and ("directory" in desc_lower or "folder" in desc_lower):
            return "_detect_empty_directories"
        elif "sql injection" in desc_lower:
            return "_detect_sql_injection_advanced"
        elif "missing" in desc_lower and "readme" in desc_lower:
            return "_detect_missing_readmes"
        elif "n+1" in desc_lower or "n plus 1" in desc_lower:
            return "_detect_n_plus_one_advanced"
        else:
            # Generic name
            terms = [word for word in desc_lower.split() if len(word) > 3][:2]
            return f"_detect_{'_'.join(terms)}"
    
    def _create_implementation_plan(self, agent_name: str, detector_name: str, issue_description: str) -> Dict:
        """Create detailed implementation plan"""
        agent = get_agent_purpose(agent_name)
        
        # Detector-specific plans
        if detector_name == "_detect_empty_directories":
            plan = {
                'detector': {
                    'what_it_detects': "Directories containing only build artifacts (__pycache__, .DS_Store, Thumbs.db, etc.) with no actual source files",
                    'how_it_works': "Scan all directories recursively, check contents, flag if only artifacts present",
                    'example_violation': "app/  # Contains only __pycache__/ subdirectory"
                },
                'files_to_modify': {
                    f'tools/fengshui/agents/{agent_name.lower().replace("agent", "_agent")}.py': [
                        f"Add {detector_name} method",
                        "Update analyze_module() to call new detector",
                        "Add ARTIFACT_FILES constant"
                    ]
                },
                'files_to_create': {
                    f'tests/unit/tools/fengshui/test_{detector_name[1:]}.py': "Unit tests for detector"
                },
                'testing': {
                    'unit_test_scenarios': "5-7",
                    'test_cases': [
                        "Empty directory (only __pycache__)",
                        "Empty directory (only .DS_Store)",
                        "Directory with source files (should pass)",
                        "Nested empty directories",
                        "Mixed (some empty, some not)"
                    ]
                },
                'effort_breakdown': {
                    'Detector implementation': "1-1.5 hours",
                    'Unit tests': "30-45 min",
                    'Integration validation': "15-30 min",
                    'Documentation': "15 min"
                },
                'priority_reasoning': "P2 (Medium) - Improves project cleanliness, but not critical"
            }
        else:
            # Generic plan
            plan = {
                'detector': {
                    'what_it_detects': f"Issues related to: {issue_description}",
                    'how_it_works': "Analyze code/files and flag violations",
                    'example_violation': "[To be determined during implementation]"
                },
                'files_to_modify': {
                    f'tools/fengshui/agents/{agent_name.lower().replace("agent", "_agent")}.py': [
                        f"Add {detector_name} method",
                        "Update analyze_module() to call new detector"
                    ]
                },
                'files_to_create': {
                    f'tests/unit/tools/fengshui/test_{detector_name[1:]}.py': "Unit tests for detector"
                },
                'testing': {
                    'unit_test_scenarios': "3-5",
                    'test_cases': ["[To be determined]"]
                },
                'effort_breakdown': {
                    'Detector implementation': "1-2 hours",
                    'Unit tests': "30-60 min",
                    'Integration validation': "15-30 min",
                    'Documentation': "15 min"
                },
                'priority_reasoning': "Priority TBD based on user input"
            }
        
        return plan
    
    def _estimate_effort(self, implementation_plan: Dict) -> str:
        """Estimate total effort from breakdown"""
        # Sum effort from breakdown
        total_min = 0
        total_max = 0
        
        for task, time_str in implementation_plan['effort_breakdown'].items():
            # Parse "1-2 hours" or "30-60 min"
            if "hour" in time_str:
                parts = time_str.split("hour")[0].strip().split("-")
                total_min += float(parts[0]) * 60
                total_max += float(parts[-1]) * 60
            elif "min" in time_str:
                parts = time_str.split("min")[0].strip().split("-")
                total_min += float(parts[0])
                total_max += float(parts[-1])
        
        # Convert back to hours
        hours_min = total_min / 60
        hours_max = total_max / 60
        
        return f"{hours_min:.1f}-{hours_max:.1f} hours"
    
    def _calculate_priority(self, issue_description: str, validation: Dict) -> str:
        """Calculate priority based on issue and validation"""
        desc_lower = issue_description.lower()
        confidence = validation['confidence']
        
        # Security issues = P0
        if any(word in desc_lower for word in ['security', 'vulnerability', 'injection', 'xss']):
            return "P0 (CRITICAL)"
        
        # High confidence + common issue = P1
        if confidence >= 0.5 and any(word in desc_lower for word in ['di violation', 'pattern', 'architecture']):
            return "P1 (HIGH)"
        
        # Moderate confidence or organization issue = P2
        if confidence >= 0.3 or any(word in desc_lower for word in ['empty', 'obsolete', 'misplaced']):
            return "P2 (MEDIUM)"
        
        # Low confidence = P3
        return "P3 (LOW)"
    
    def _generate_proposal_id(self, agent_name: str, detector_name: str) -> str:
        """Generate unique proposal ID"""
        date_str = datetime.now().strftime("%Y%m%d")
        agent_short = agent_name.replace("Agent", "")[:4].upper()
        detector_short = detector_name.replace("_detect_", "")[:10]
        return f"{date_str}-{agent_short}-{detector_short}"
    
    def _prompt_user_for_agent(self, issue_description: str) -> str:
        """Fallback: Let user choose agent"""
        # In real implementation, this would be interactive
        # For now, return FileOrganizationAgent as fallback
        return "FileOrganizationAgent"


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for enhancement proposer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhancement_proposer.py '<issue description>'")
        print("Example: python enhancement_proposer.py 'Empty /app folder with only __pycache__'")
        return
    
    issue_description = sys.argv[1]
    
    print("=" * 60)
    print("Shi Fu Enhancement Proposer")
    print("=" * 60)
    print()
    
    proposer = EnhancementProposer()
    
    print(f"Analyzing issue: {issue_description}")
    print()
    
    proposal = proposer.analyze_gap(issue_description)
    
    print(f"✅ Proposal Generated!")
    print(f"   ID: {proposal.proposal_id}")
    print(f"   Agent: {proposal.agent_name}")
    print(f"   Detector: {proposal.detector_name}")
    print(f"   Priority: {proposal.priority}")
    print(f"   Effort: {proposal.estimated_effort}")
    print()
    
    filepath = proposer.save_proposal(proposal)
    print(f"📄 Proposal saved to: {filepath}")
    print()
    print("Next steps:")
    print(f"1. Review proposal: code {filepath}")
    print("2. Decide: Approve, Modify, or Reject")
    print("3. If approved: Ask AI to implement")


if __name__ == "__main__":
    main()