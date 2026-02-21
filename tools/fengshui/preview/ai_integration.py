"""
Feng Shui Preview Mode - AI Integration Hooks
Provides real-time architecture validation during AI planning phase.

Integration Points:
1. Validate design during planning conversations
2. Suggest fixes before implementation
3. Hook into Cline workflow for proactive guidance

Version: 1.0
Created: 2026-02-21
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .engine import PreviewEngine, PreviewResult, Severity
from .parsers import DesignDocumentParser


@dataclass
class ValidationContext:
    """Context information for AI validation"""
    conversation_id: str
    planning_phase: bool
    design_complete: bool
    implementation_started: bool
    modules_discussed: List[str]
    violations_detected: List[str]


@dataclass
class AIFeedback:
    """Structured feedback for AI assistant"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    message: str
    fix_suggestion: str
    code_example: Optional[str] = None
    documentation_ref: Optional[str] = None
    blocking: bool = False  # Should stop implementation?


class AIIntegrationHook:
    """
    Integration hook for Cline workflow.
    Provides real-time validation during planning phase.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize AI integration hook.
        
        Args:
            project_root: Root directory of project (default: current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.engine = PreviewEngine()
        self.validation_history: List[ValidationContext] = []
    
    def validate_planning_concept(
        self,
        concept: str,
        context: ValidationContext
    ) -> List[AIFeedback]:
        """
        Validate a planning concept in real-time.
        
        Args:
            concept: Description of what AI is planning (e.g., "Add query history to ai_assistant")
            context: Current conversation context
            
        Returns:
            List of structured feedback items for AI
            
        Example:
            >>> hook = AIIntegrationHook()
            >>> context = ValidationContext(
            ...     conversation_id="conv-123",
            ...     planning_phase=True,
            ...     design_complete=False,
            ...     implementation_started=False,
            ...     modules_discussed=["ai_assistant", "data_products_v2"],
            ...     violations_detected=[]
            ... )
            >>> feedback = hook.validate_planning_concept(
            ...     "Import QueryRepository from data_products_v2",
            ...     context
            ... )
            >>> print(feedback[0].severity)  # "CRITICAL"
            >>> print(feedback[0].blocking)  # True
        """
        feedback: List[AIFeedback] = []
        
        # Check for cross-module import patterns
        if self._detect_cross_module_import(concept, context):
            feedback.append(AIFeedback(
                severity="CRITICAL",
                message="🚫 Cross-module import detected in planning",
                fix_suggestion=(
                    "Instead of importing from another module, use Dependency Injection:\n"
                    "1. Define interface in core/interfaces/\n"
                    "2. Inject implementation via constructor\n"
                    "3. Register in module's dependency container"
                ),
                code_example=self._generate_di_example(concept),
                documentation_ref="[[Module Isolation Enforcement Standard]]",
                blocking=True
            ))
        
        # Check API naming conventions
        if self._detect_api_naming_issue(concept):
            feedback.append(AIFeedback(
                severity="HIGH",
                message="⚠️ API naming convention violation detected",
                fix_suggestion=(
                    "Follow Module Federation Standard naming:\n"
                    "- Routes: /kebab-case (e.g., /ai-assistant/chat)\n"
                    "- Module IDs: snake_case (e.g., ai_assistant)\n"
                    "- Classes: PascalCase + Module suffix (e.g., AIAssistantModule)"
                ),
                documentation_ref="[[Module Federation Standard]]",
                blocking=False
            ))
        
        # Check for missing test plans
        if self._detect_missing_test_plan(concept, context):
            feedback.append(AIFeedback(
                severity="MEDIUM",
                message="⚠️ No API contract test plan detected",
                fix_suggestion=(
                    "Before implementation, plan API contract tests:\n"
                    "1. Create test file: tests/[module]/test_[module]_backend_api.py\n"
                    "2. Add @pytest.mark.api_contract decorator\n"
                    "3. Test via requests library (< 1s timeout)\n"
                    "4. Verify contract before building UX"
                ),
                code_example=self._generate_test_example(concept),
                documentation_ref="[[Gu Wu API Contract Testing Foundation]]",
                blocking=False
            ))
        
        # Store validation in history
        context.violations_detected.extend([f.severity for f in feedback if f.blocking])
        self.validation_history.append(context)
        
        return feedback
    
    def validate_design_document(
        self,
        doc_path: Path,
        context: ValidationContext
    ) -> List[AIFeedback]:
        """
        Validate a design document in real-time.
        
        Args:
            doc_path: Path to design document
            context: Current conversation context
            
        Returns:
            List of structured feedback items
        """
        feedback: List[AIFeedback] = []
        
        # Parse design document
        try:
            # Create parser with document's parent directory as module_path
            parser = DesignDocumentParser(doc_path.parent)
            spec = parser.parse_design_document(doc_path)
            
            # Run preview validation
            result = self.engine.preview(spec)
            
            # Convert findings to AI feedback
            for finding in result.findings:
                feedback.append(self._finding_to_feedback(finding))
            
        except Exception as e:
            feedback.append(AIFeedback(
                severity="HIGH",
                message=f"⚠️ Could not parse design document: {str(e)}",
                fix_suggestion="Ensure design document follows standard format with module.json and README.md sections",
                blocking=False
            ))
        
        return feedback
    
    def should_block_implementation(
        self,
        context: ValidationContext
    ) -> tuple[bool, List[AIFeedback]]:
        """
        Determine if implementation should be blocked based on validation.
        
        Args:
            context: Current conversation context
            
        Returns:
            Tuple of (should_block, blocking_feedback)
        """
        blocking_feedback = [
            f for f in self.validation_history
            if context.conversation_id == getattr(f, 'conversation_id', None)
        ]
        
        # Check if any CRITICAL violations exist
        has_critical = any(
            'CRITICAL' in context.violations_detected
            for context in self.validation_history
            if context.conversation_id == context.conversation_id
        )
        
        return has_critical, []
    
    def generate_fix_plan(
        self,
        feedback: List[AIFeedback]
    ) -> Dict[str, Any]:
        """
        Generate a structured fix plan from feedback.
        
        Args:
            feedback: List of feedback items
            
        Returns:
            Structured fix plan with steps
        """
        critical = [f for f in feedback if f.severity == "CRITICAL"]
        high = [f for f in feedback if f.severity == "HIGH"]
        
        return {
            "blocking_issues": len(critical),
            "critical_fixes": [
                {
                    "issue": f.message,
                    "fix": f.fix_suggestion,
                    "example": f.code_example,
                    "docs": f.documentation_ref
                }
                for f in critical
            ],
            "recommended_fixes": [
                {
                    "issue": f.message,
                    "fix": f.fix_suggestion,
                    "example": f.code_example,
                    "docs": f.documentation_ref
                }
                for f in high
            ],
            "can_proceed": len(critical) == 0
        }
    
    # Private helper methods
    
    def _detect_cross_module_import(
        self,
        concept: str,
        context: ValidationContext
    ) -> bool:
        """Detect cross-module import patterns in concept"""
        # Pattern: "from modules.X import" where X is another module
        cross_module_patterns = [
            "from modules.",
            "import modules.",
        ]
        
        # Check if importing from another discussed module
        for module in context.modules_discussed:
            for pattern in cross_module_patterns:
                if f"{pattern}{module}" in concept.lower():
                    return True
        
        return False
    
    def _detect_api_naming_issue(self, concept: str) -> bool:
        """Detect API naming convention violations"""
        # Pattern: CamelCase in routes (should be kebab-case)
        import re
        
        # Check for routes with camelCase (after last slash)
        route_pattern = r'/[a-z]+[A-Z]+'
        if re.search(route_pattern, concept):
            return True
        
        # Check for snake_case in routes (should be kebab-case)
        route_snake_pattern = r'/api/[a-z]+_[a-z]+'
        if re.search(route_snake_pattern, concept):
            return True
        
        return False
    
    def _detect_missing_test_plan(
        self,
        concept: str,
        context: ValidationContext
    ) -> bool:
        """Detect missing API contract test plans"""
        # If discussing API endpoints but no test mention
        api_keywords = ["api", "endpoint", "route", "post", "get", "delete"]
        test_keywords = ["test", "pytest", "@pytest.mark.api_contract"]
        
        has_api = any(keyword in concept.lower() for keyword in api_keywords)
        has_test = any(keyword in concept.lower() for keyword in test_keywords)
        
        return has_api and not has_test
    
    def _generate_di_example(self, concept: str) -> str:
        """Generate Dependency Injection code example"""
        return '''
# ❌ WRONG: Direct import from another module
from modules.data_products_v2.repositories import QueryRepository

class QueryHistoryService:
    def __init__(self):
        self.repo = QueryRepository()  # Cross-module coupling!

# ✅ CORRECT: Dependency Injection via interface
# Define interface in core/interfaces/
from core.interfaces.data_product_repository import IDataProductRepository

class QueryHistoryService:
    def __init__(self, data_repo: IDataProductRepository):
        self.data_repo = data_repo  # Injected dependency
        
# In module's dependency container:
# container.register(IDataProductRepository, SqliteDataProductRepository)
'''
    
    def _generate_test_example(self, concept: str) -> str:
        """Generate API contract test example"""
        return '''
import pytest
import requests

@pytest.mark.e2e
@pytest.mark.api_contract
def test_query_history_api_contract():
    """Test: Query history API returns valid contract"""
    # ARRANGE
    url = "http://localhost:5000/api/ai-assistant/history"
    
    # ACT
    response = requests.get(url, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert 'queries' in data
    assert isinstance(data['queries'], list)
'''
    
    def _finding_to_feedback(self, finding) -> AIFeedback:
        """Convert PreviewFinding to AIFeedback"""
        severity_map = {
            Severity.CRITICAL: "CRITICAL",
            Severity.HIGH: "HIGH",
            Severity.MEDIUM: "MEDIUM",
            Severity.LOW: "LOW"
        }
        
        return AIFeedback(
            severity=severity_map.get(finding.severity, "MEDIUM"),
            message=finding.message,
            fix_suggestion=finding.suggestion or "Review Module Federation Standard",
            documentation_ref="[[Module Federation Standard]]",
            blocking=finding.severity == Severity.CRITICAL
        )


class ClineWorkflowIntegration:
    """
    Integration with Cline AI workflow.
    Hooks into planning phase for proactive validation.
    """
    
    def __init__(self):
        """Initialize Cline workflow integration"""
        self.hook = AIIntegrationHook()
        self.planning_active = False
        self.current_context: Optional[ValidationContext] = None
    
    def on_planning_start(self, conversation_id: str, modules: List[str]) -> None:
        """
        Called when AI enters planning phase.
        
        Args:
            conversation_id: Unique conversation identifier
            modules: List of modules being discussed
        """
        self.planning_active = True
        self.current_context = ValidationContext(
            conversation_id=conversation_id,
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=modules,
            violations_detected=[]
        )
    
    def on_concept_discussed(self, concept: str) -> List[AIFeedback]:
        """
        Called when AI discusses a concept during planning.
        
        Args:
            concept: Description of concept being discussed
            
        Returns:
            List of feedback items for AI to consider
        """
        if not self.planning_active or not self.current_context:
            return []
        
        return self.hook.validate_planning_concept(concept, self.current_context)
    
    def on_design_complete(self, doc_path: Optional[Path] = None) -> List[AIFeedback]:
        """
        Called when design is complete, before implementation.
        
        Args:
            doc_path: Path to design document (if exists)
            
        Returns:
            List of feedback items for final validation
        """
        if not self.current_context:
            return []
        
        self.current_context.design_complete = True
        
        if doc_path and doc_path.exists():
            return self.hook.validate_design_document(doc_path, self.current_context)
        
        return []
    
    def should_proceed_to_implementation(self) -> tuple[bool, str]:
        """
        Check if implementation should proceed.
        
        Returns:
            Tuple of (can_proceed, reason)
        """
        if not self.current_context:
            return True, "No validation context"
        
        should_block, _ = self.hook.should_block_implementation(self.current_context)
        
        if should_block:
            return False, "CRITICAL violations detected. Fix design before implementing."
        
        return True, "Design validation passed"
    
    def on_implementation_start(self) -> None:
        """Called when implementation phase starts"""
        if self.current_context:
            self.current_context.implementation_started = True
            self.planning_active = False
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation for current conversation.
        
        Returns:
            Validation summary with statistics
        """
        if not self.current_context:
            return {}
        
        return {
            "conversation_id": self.current_context.conversation_id,
            "violations_count": len(self.current_context.violations_detected),
            "critical_violations": [
                v for v in self.current_context.violations_detected
                if v == "CRITICAL"
            ],
            "can_implement": len([
                v for v in self.current_context.violations_detected
                if v == "CRITICAL"
            ]) == 0,
            "modules_validated": self.current_context.modules_discussed
        }


def create_ai_integration() -> ClineWorkflowIntegration:
    """
    Factory function to create Cline workflow integration.
    
    Returns:
        Configured ClineWorkflowIntegration instance
        
    Example:
        >>> integration = create_ai_integration()
        >>> integration.on_planning_start("conv-123", ["ai_assistant"])
        >>> feedback = integration.on_concept_discussed("Import from data_products_v2")
        >>> print(feedback[0].severity)  # "CRITICAL"
    """
    return ClineWorkflowIntegration()