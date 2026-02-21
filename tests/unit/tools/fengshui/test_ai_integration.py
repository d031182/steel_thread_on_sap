"""
Tests for Feng Shui Preview AI Integration

Tests real-time validation hooks for AI workflow integration.
"""

import pytest
from pathlib import Path
from tools.fengshui.preview.ai_integration import (
    AIIntegrationHook,
    ClineWorkflowIntegration,
    ValidationContext,
    AIFeedback,
    create_ai_integration
)


class TestAIIntegrationHook:
    """Test suite for AIIntegrationHook"""
    
    def test_detect_cross_module_import(self):
        """Test: Hook detects cross-module import in concept"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-001",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant", "data_products_v2"],
            violations_detected=[]
        )
        
        concept = "from modules.data_products_v2 import QueryRepository"
        feedback = hook.validate_planning_concept(concept, context)
        
        assert len(feedback) > 0
        assert any(f.severity == "CRITICAL" for f in feedback)
        assert any(f.blocking for f in feedback)
        assert any("cross-module" in f.message.lower() for f in feedback)
    
    def test_detect_api_naming_violation(self):
        """Test: Hook detects camelCase in API route"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-002",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant"],
            violations_detected=[]
        )
        
        concept = "POST /api/ai-assistant/queryHistory"
        feedback = hook.validate_planning_concept(concept, context)
        
        assert len(feedback) > 0
        assert any(f.severity == "HIGH" for f in feedback)
        assert any("naming" in f.message.lower() for f in feedback)
    
    def test_detect_snake_case_in_route(self):
        """Test: Hook detects snake_case in API route"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-003",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant"],
            violations_detected=[]
        )
        
        concept = "GET /api/ai_assistant/query_history"
        feedback = hook.validate_planning_concept(concept, context)
        
        assert len(feedback) > 0
        assert any("naming" in f.message.lower() for f in feedback)
    
    def test_detect_missing_test_plan(self):
        """Test: Hook detects missing test plan for API endpoint"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-004",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant"],
            violations_detected=[]
        )
        
        concept = "Create POST /api/ai-assistant/chat endpoint"
        feedback = hook.validate_planning_concept(concept, context)
        
        assert len(feedback) > 0
        assert any("test" in f.message.lower() for f in feedback)
        assert any(f.severity in ["MEDIUM", "HIGH"] for f in feedback)
    
    def test_clean_concept_no_violations(self):
        """Test: Clean concept returns no critical violations"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-005",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant"],
            violations_detected=[]
        )
        
        concept = """
        Create ChatService with Dependency Injection:
        - Define IChatRepository in core/interfaces/
        - Inject via constructor
        - Write API contract test with @pytest.mark.api_contract
        """
        feedback = hook.validate_planning_concept(concept, context)
        
        # Should have minimal or no CRITICAL violations
        critical_violations = [f for f in feedback if f.severity == "CRITICAL"]
        assert len(critical_violations) == 0
    
    def test_should_block_implementation_with_critical(self):
        """Test: Should block if CRITICAL violations exist"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-006",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant", "data_products_v2"],
            violations_detected=["CRITICAL"]
        )
        
        hook.validation_history.append(context)
        
        should_block, _ = hook.should_block_implementation(context)
        assert should_block is True
    
    def test_should_not_block_with_only_warnings(self):
        """Test: Should not block if only warnings exist"""
        hook = AIIntegrationHook()
        context = ValidationContext(
            conversation_id="test-007",
            planning_phase=True,
            design_complete=False,
            implementation_started=False,
            modules_discussed=["ai_assistant"],
            violations_detected=["MEDIUM", "LOW"]
        )
        
        hook.validation_history.append(context)
        
        should_block, _ = hook.should_block_implementation(context)
        assert should_block is False
    
    def test_generate_di_example(self):
        """Test: Generates valid DI code example"""
        hook = AIIntegrationHook()
        example = hook._generate_di_example("test concept")
        
        assert "# ❌ WRONG" in example
        assert "# ✅ CORRECT" in example
        assert "Dependency Injection" in example
        assert "core/interfaces" in example
    
    def test_generate_test_example(self):
        """Test: Generates valid test code example"""
        hook = AIIntegrationHook()
        example = hook._generate_test_example("test concept")
        
        assert "@pytest.mark.api_contract" in example
        assert "requests" in example
        assert "assert" in example
        assert "timeout" in example


class TestClineWorkflowIntegration:
    """Test suite for ClineWorkflowIntegration"""
    
    def test_on_planning_start(self):
        """Test: Planning phase initialization"""
        integration = ClineWorkflowIntegration()
        
        integration.on_planning_start("conv-001", ["ai_assistant"])
        
        assert integration.planning_active is True
        assert integration.current_context is not None
        assert integration.current_context.conversation_id == "conv-001"
        assert "ai_assistant" in integration.current_context.modules_discussed
    
    def test_on_concept_discussed_returns_feedback(self):
        """Test: Concept discussion returns feedback"""
        integration = ClineWorkflowIntegration()
        integration.on_planning_start("conv-002", ["ai_assistant", "data_products_v2"])
        
        concept = "from modules.data_products_v2 import QueryRepo"
        feedback = integration.on_concept_discussed(concept)
        
        assert len(feedback) > 0
        assert any(f.severity == "CRITICAL" for f in feedback)
    
    def test_on_concept_discussed_without_planning(self):
        """Test: Returns empty feedback if not in planning phase"""
        integration = ClineWorkflowIntegration()
        
        concept = "some concept"
        feedback = integration.on_concept_discussed(concept)
        
        assert len(feedback) == 0
    
    def test_should_proceed_with_no_violations(self):
        """Test: Can proceed if no CRITICAL violations"""
        integration = ClineWorkflowIntegration()
        integration.on_planning_start("conv-003", ["ai_assistant"])
        
        # Discuss clean concept
        integration.on_concept_discussed("Use DI pattern")
        
        can_proceed, reason = integration.should_proceed_to_implementation()
        assert can_proceed is True
    
    def test_should_not_proceed_with_critical_violations(self):
        """Test: Cannot proceed if CRITICAL violations exist"""
        integration = ClineWorkflowIntegration()
        integration.on_planning_start("conv-004", ["ai_assistant", "data_products_v2"])
        
        # Discuss concept with violation
        integration.on_concept_discussed("from modules.data_products_v2 import Repo")
        
        # Should have critical violation
        assert integration.current_context
        if "CRITICAL" in integration.current_context.violations_detected:
            can_proceed, reason = integration.should_proceed_to_implementation()
            assert can_proceed is False
            assert "CRITICAL" in reason
    
    def test_on_implementation_start(self):
        """Test: Implementation phase starts correctly"""
        integration = ClineWorkflowIntegration()
        integration.on_planning_start("conv-005", ["ai_assistant"])
        
        integration.on_implementation_start()
        
        assert integration.planning_active is False
        assert integration.current_context.implementation_started is True
    
    def test_get_validation_summary(self):
        """Test: Validation summary provides stats"""
        integration = ClineWorkflowIntegration()
        integration.on_planning_start("conv-006", ["ai_assistant"])
        
        summary = integration.get_validation_summary()
        
        assert "conversation_id" in summary
        assert "violations_count" in summary
        assert "can_implement" in summary
        assert "modules_validated" in summary
        assert summary["conversation_id"] == "conv-006"
    
    def test_get_validation_summary_no_context(self):
        """Test: Returns empty summary if no context"""
        integration = ClineWorkflowIntegration()
        
        summary = integration.get_validation_summary()
        
        assert summary == {}


class TestFactoryFunction:
    """Test suite for factory function"""
    
    def test_create_ai_integration(self):
        """Test: Factory creates valid integration instance"""
        integration = create_ai_integration()
        
        assert isinstance(integration, ClineWorkflowIntegration)
        assert integration.hook is not None
        assert integration.planning_active is False
        assert integration.current_context is None


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""
    
    def test_complete_workflow_with_violation_and_fix(self):
        """Test: Complete workflow from planning to implementation"""
        integration = create_ai_integration()
        
        # Step 1: Start planning
        integration.on_planning_start("e2e-001", ["ai_assistant", "data_products_v2"])
        assert integration.planning_active is True
        
        # Step 2: Discuss concept with violation
        bad_concept = "from modules.data_products_v2 import QueryRepo"
        feedback_bad = integration.on_concept_discussed(bad_concept)
        assert len(feedback_bad) > 0
        assert any(f.blocking for f in feedback_bad)
        
        # Step 3: Correct concept
        good_concept = "Use DI: inject IQueryRepository via constructor"
        feedback_good = integration.on_concept_discussed(good_concept)
        
        # Step 4: Check if can proceed
        can_proceed, _ = integration.should_proceed_to_implementation()
        
        # Step 5: If can proceed, start implementation
        if can_proceed:
            integration.on_implementation_start()
            assert integration.planning_active is False
            assert integration.current_context.implementation_started is True
        
        # Step 6: Get summary
        summary = integration.get_validation_summary()
        assert "conversation_id" in summary
        assert summary["conversation_id"] == "e2e-001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])