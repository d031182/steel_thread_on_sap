"""
Example: Using Feng Shui Preview with AI Integration

Demonstrates how AI assistant can use real-time validation
during planning phase to catch violations before implementation.
"""

from pathlib import Path
from tools.fengshui.preview.ai_integration import (
    create_ai_integration,
    ValidationContext,
    AIFeedback
)


def example_1_cross_module_import_detection():
    """
    Example 1: AI detects cross-module import during planning
    """
    print("=" * 70)
    print("EXAMPLE 1: Cross-Module Import Detection")
    print("=" * 70)
    
    # Create integration
    integration = create_ai_integration()
    
    # Start planning phase
    integration.on_planning_start(
        conversation_id="conv-001",
        modules=["ai_assistant", "data_products_v2"]
    )
    
    # AI discusses concept with violation
    concept = """
    I'll create QueryHistoryService that imports QueryRepository
    from modules.data_products_v2.repositories to store query history.
    """
    
    feedback = integration.on_concept_discussed(concept)
    
    # Display feedback
    print(f"\nConcept: {concept.strip()}\n")
    print("Feedback:")
    for i, f in enumerate(feedback, 1):
        print(f"\n{i}. {f.severity}: {f.message}")
        print(f"   Fix: {f.fix_suggestion}")
        if f.blocking:
            print(f"   ⚠️  BLOCKING: Must fix before implementing")
        if f.code_example:
            print(f"   Example:\n{f.code_example}")
    
    # Check if can proceed
    can_proceed, reason = integration.should_proceed_to_implementation()
    print(f"\n✓ Can proceed: {can_proceed}")
    print(f"  Reason: {reason}")


def example_2_api_naming_violation():
    """
    Example 2: AI detects API naming convention violation
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: API Naming Convention Violation")
    print("=" * 70)
    
    integration = create_ai_integration()
    integration.on_planning_start("conv-002", ["ai_assistant"])
    
    # API endpoint with camelCase (should be kebab-case)
    concept = """
    I'll create endpoint POST /api/ai-assistant/queryHistory
    to handle query history requests.
    """
    
    feedback = integration.on_concept_discussed(concept)
    
    print(f"\nConcept: {concept.strip()}\n")
    print("Feedback:")
    for f in feedback:
        print(f"\n{f.severity}: {f.message}")
        print(f"Fix: {f.fix_suggestion}")
        print(f"Docs: {f.documentation_ref}")


def example_3_missing_test_plan():
    """
    Example 3: AI detects missing API contract test plan
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Missing API Contract Test Plan")
    print("=" * 70)
    
    integration = create_ai_integration()
    integration.on_planning_start("conv-003", ["ai_assistant"])
    
    # Discussing API without test plan
    concept = """
    I'll implement GET /api/ai-assistant/history endpoint
    that returns conversation history from the database.
    """
    
    feedback = integration.on_concept_discussed(concept)
    
    print(f"\nConcept: {concept.strip()}\n")
    print("Feedback:")
    for f in feedback:
        print(f"\n{f.severity}: {f.message}")
        print(f"Fix: {f.fix_suggestion}")
        if f.code_example:
            print(f"Example:\n{f.code_example}")


def example_4_complete_workflow():
    """
    Example 4: Complete planning → validation → implementation workflow
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complete Workflow with Validation")
    print("=" * 70)
    
    integration = create_ai_integration()
    
    # Phase 1: Planning starts
    print("\n📋 PHASE 1: Planning Phase")
    integration.on_planning_start("conv-004", ["ai_assistant"])
    print("✓ Planning started for modules: ai_assistant")
    
    # Phase 2: Discuss concept (with violation)
    print("\n💭 PHASE 2: Discussing Concept")
    concept_bad = "Import DataService from modules.data_products_v2"
    feedback = integration.on_concept_discussed(concept_bad)
    
    if feedback:
        print(f"⚠️  Violations detected:")
        for f in feedback:
            print(f"   - {f.severity}: {f.message}")
    
    # Phase 3: Correct design
    print("\n🔧 PHASE 3: Correcting Design")
    concept_good = """
    Use Dependency Injection:
    - Define IDataService in core/interfaces/
    - Inject via constructor
    - Register in DI container
    """
    feedback = integration.on_concept_discussed(concept_good)
    print(f"✓ Corrected design: {concept_good.strip()}")
    print(f"✓ Violations: {len(feedback)}")
    
    # Phase 4: Check if can proceed
    print("\n✅ PHASE 4: Validation Check")
    can_proceed, reason = integration.should_proceed_to_implementation()
    print(f"Can implement: {can_proceed}")
    print(f"Reason: {reason}")
    
    # Phase 5: Implementation starts
    if can_proceed:
        print("\n🚀 PHASE 5: Implementation Phase")
        integration.on_implementation_start()
        print("✓ Implementation started")
        
        # Get summary
        summary = integration.get_validation_summary()
        print(f"\nValidation Summary:")
        print(f"  - Conversation: {summary['conversation_id']}")
        print(f"  - Violations: {summary['violations_count']}")
        print(f"  - Critical: {len(summary['critical_violations'])}")
        print(f"  - Can implement: {summary['can_implement']}")


def example_5_real_world_scenario():
    """
    Example 5: Real-world scenario - AI Assistant feature planning
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Real-World Scenario - AI Assistant Feature")
    print("=" * 70)
    
    integration = create_ai_integration()
    
    # User request
    print("\n👤 USER REQUEST:")
    print("Add query history feature to AI Assistant that stores")
    print("all user queries and AI responses for later review.")
    
    # AI Planning
    print("\n🤖 AI PLANNING:")
    integration.on_planning_start("conv-005", ["ai_assistant", "data_products_v2"])
    
    # AI's initial design (with violations)
    print("\n📝 Initial Design:")
    design_v1 = """
    1. Create QueryHistoryService in ai_assistant/backend/services/
    2. Import QueryRepository from data_products_v2 for storage
    3. Add POST endpoint /api/aiAssistant/saveQuery
    4. Store queries in database via QueryRepository
    """
    print(design_v1)
    
    # Validate initial design
    feedback_v1 = []
    for line in design_v1.split('\n'):
        feedback_v1.extend(integration.on_concept_discussed(line))
    
    print("\n⚠️  VIOLATIONS DETECTED:")
    for i, f in enumerate(feedback_v1, 1):
        if f.blocking:
            print(f"{i}. {f.severity}: {f.message}")
            print(f"   Fix: {f.fix_suggestion[:80]}...")
    
    # AI corrects design
    print("\n🔧 CORRECTED DESIGN:")
    design_v2 = """
    1. Create QueryHistoryService in ai_assistant/backend/services/
    2. Define IQueryStorage interface in core/interfaces/
    3. Inject IQueryStorage via constructor (DI pattern)
    4. Add POST endpoint /api/ai-assistant/save-query (kebab-case)
    5. Write API contract test: test_save_query_api_contract()
    6. Register SqliteQueryStorage implementation in DI container
    """
    print(design_v2)
    
    # Validate corrected design
    feedback_v2 = []
    for line in design_v2.split('\n'):
        feedback_v2.extend(integration.on_concept_discussed(line))
    
    blocking_issues = [f for f in feedback_v2 if f.blocking]
    
    print(f"\n✓ VALIDATION RESULT:")
    print(f"  Blocking issues: {len(blocking_issues)}")
    print(f"  Total feedback: {len(feedback_v2)}")
    
    # Check if can implement
    can_proceed, reason = integration.should_proceed_to_implementation()
    print(f"\n{'✅' if can_proceed else '❌'} Can proceed to implementation: {can_proceed}")
    print(f"  Reason: {reason}")
    
    if can_proceed:
        print("\n🚀 Ready to implement clean code!")
        print("  Expected violations in full Feng Shui audit: 0-2 (edge cases only)")
    else:
        print("\n⛔ Must fix violations before implementing")


if __name__ == "__main__":
    """Run all examples"""
    print("\n" + "=" * 70)
    print("FENG SHUI PREVIEW - AI INTEGRATION EXAMPLES")
    print("=" * 70)
    
    example_1_cross_module_import_detection()
    example_2_api_naming_violation()
    example_3_missing_test_plan()
    example_4_complete_workflow()
    example_5_real_world_scenario()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)