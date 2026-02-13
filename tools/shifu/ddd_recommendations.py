"""
DDD Recommendations Engine - AI-Powered Pattern Adoption Guidance
==================================================================

Provides intelligent recommendations for DDD pattern adoption including:
- Pattern prioritization based on impact
- Code examples tailored to project
- Effort estimation
- Step-by-step implementation guidance
- Impact prediction

Philosophy:
"The Master doesn't just point to the mountain. The Master shows the path to climb it."
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class PatternPriority(Enum):
    """Priority levels for pattern implementation"""
    CRITICAL = "CRITICAL"  # 0% adoption, high impact
    HIGH = "HIGH"          # <40% adoption, medium-high impact
    MEDIUM = "MEDIUM"      # 40-79% adoption
    LOW = "LOW"            # 80%+ adoption (maintenance mode)


@dataclass
class CodeExample:
    """Code example for pattern implementation"""
    pattern_name: str
    language: str  # "Python", "JavaScript"
    code: str
    explanation: str
    file_path: str  # Suggested file location


@dataclass
class ImplementationStep:
    """Single step in implementation guide"""
    step_number: int
    title: str
    description: str
    command: Optional[str] = None  # CLI command if applicable
    code_example: Optional[CodeExample] = None
    validation: Optional[str] = None  # How to verify this step


@dataclass
class PatternRecommendation:
    """Complete recommendation for a DDD pattern"""
    pattern_name: str
    priority: PatternPriority
    current_adoption: float  # 0-100
    target_adoption: float   # 0-100
    expected_maturity_gain: float  # Points gained
    effort_hours: Tuple[int, int]  # (min, max) hours
    
    # WHY section
    rationale: str
    business_value: str
    technical_benefit: str
    
    # HOW section
    implementation_steps: List[ImplementationStep]
    code_examples: List[CodeExample]
    
    # IMPACT section
    modules_affected: List[str]
    files_to_create: List[str]
    files_to_modify: List[str]
    test_coverage_needed: int  # Number of tests
    
    # RISKS section
    complexity_level: str  # "Low", "Medium", "High"
    breaking_changes: bool
    prerequisites: List[str]
    common_pitfalls: List[str]


class DDDRecommendationsEngine:
    """
    AI-powered recommendations engine for DDD pattern adoption
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize recommendations engine
        
        Args:
            project_root: Root directory of project
        """
        self.project_root = project_root
        
        # Pattern impact weights (for prioritization)
        self.pattern_weights = {
            "Unit of Work": 19,         # Highest impact
            "Service Layer": 15,        # High impact
            "Repository Pattern": 12,   # Medium-high impact
            "Domain Events": 10,        # Medium impact
            "Aggregate Pattern": 8      # Medium impact
        }
    
    def generate_recommendations(
        self,
        ddd_report: Dict,
        max_recommendations: int = 3
    ) -> List[PatternRecommendation]:
        """
        Generate prioritized recommendations based on DDD maturity report
        
        Args:
            ddd_report: DDD maturity report from tracker
            max_recommendations: Maximum number of recommendations
        
        Returns:
            List of recommendations, sorted by priority
        """
        recommendations = []
        
        for pattern_score in ddd_report['pattern_scores']:
            pattern_name = pattern_score['pattern_name']
            adoption = pattern_score['adoption_percentage']
            
            # Skip if already excellent
            if adoption >= 80:
                continue
            
            # Generate recommendation
            rec = self._generate_pattern_recommendation(
                pattern_name=pattern_name,
                adoption=adoption,
                modules_using=pattern_score['modules_using'],
                modules_total=pattern_score['modules_total']
            )
            
            recommendations.append(rec)
        
        # Sort by priority (CRITICAL → LOW) then by impact
        priority_order = {
            PatternPriority.CRITICAL: 0,
            PatternPriority.HIGH: 1,
            PatternPriority.MEDIUM: 2,
            PatternPriority.LOW: 3
        }
        
        recommendations.sort(
            key=lambda r: (
                priority_order[r.priority],
                -r.expected_maturity_gain
            )
        )
        
        return recommendations[:max_recommendations]
    
    def _generate_pattern_recommendation(
        self,
        pattern_name: str,
        adoption: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Generate recommendation for specific pattern"""
        
        # Determine priority
        if adoption == 0:
            priority = PatternPriority.CRITICAL
        elif adoption < 40:
            priority = PatternPriority.HIGH
        elif adoption < 80:
            priority = PatternPriority.MEDIUM
        else:
            priority = PatternPriority.LOW
        
        # Calculate expected gain
        weight = self.pattern_weights.get(pattern_name, 10)
        modules_remaining = modules_total - modules_using
        expected_gain = (modules_remaining / modules_total) * weight
        
        # Target adoption
        if adoption < 50:
            target = 75.0  # Get to Good level
        else:
            target = 100.0  # Complete adoption
        
        # Generate pattern-specific content
        if pattern_name == "Unit of Work":
            return self._recommend_unit_of_work(
                priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
        elif pattern_name == "Service Layer":
            return self._recommend_service_layer(
                priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
        elif pattern_name == "Repository Pattern":
            return self._recommend_repository(
                priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
        elif pattern_name == "Domain Events":
            return self._recommend_domain_events(
                priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
        elif pattern_name == "Aggregate Pattern":
            return self._recommend_aggregate(
                priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
        else:
            # Generic recommendation
            return self._recommend_generic(
                pattern_name, priority, adoption, target, expected_gain,
                modules_using, modules_total
            )
    
    def _recommend_unit_of_work(
        self,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Recommendation for Unit of Work pattern"""
        
        # Code examples
        uow_example = CodeExample(
            pattern_name="Unit of Work",
            language="Python",
            code="""class UnitOfWork:
    \"\"\"
    Manages database transactions atomically.
    Ensures all-or-nothing for multi-step operations.
    \"\"\"
    def __init__(self, connection):
        self._connection = connection
        self._transaction = None
    
    def __enter__(self):
        self._transaction = self._connection.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._transaction.commit()
        else:
            self._transaction.rollback()
        return False

# Usage in service layer
def create_data_product_with_metadata(product_data, metadata):
    with UnitOfWork(db.connection) as uow:
        product = repository.create(product_data)
        metadata_service.attach(product.id, metadata)
        # Both succeed or both fail - atomic!
""",
            explanation="Unit of Work ensures all database operations in a business transaction succeed or fail together. Eliminates partial updates and test flakiness.",
            file_path="core/services/unit_of_work.py"
        )
        
        # Implementation steps
        steps = [
            ImplementationStep(
                step_number=1,
                title="Create Unit of Work base class",
                description="Create core/services/unit_of_work.py with context manager",
                code_example=uow_example,
                validation="Run: pytest tests/unit/core/services/test_unit_of_work.py"
            ),
            ImplementationStep(
                step_number=2,
                title="Update repositories to accept UnitOfWork",
                description="Modify repository methods to work within UnitOfWork context",
                command=None,
                validation="Check: repositories can commit/rollback via UnitOfWork"
            ),
            ImplementationStep(
                step_number=3,
                title="Refactor service layer for atomic operations",
                description="Wrap multi-step operations in UnitOfWork context",
                command=None,
                validation="Run integration tests, verify atomicity"
            ),
            ImplementationStep(
                step_number=4,
                title="Write comprehensive tests",
                description="Test happy path, rollback scenarios, nested transactions",
                command="pytest tests/unit/core/services/test_unit_of_work.py -v",
                validation="100% test coverage on UnitOfWork"
            ),
            ImplementationStep(
                step_number=5,
                title="Validate maturity improvement",
                description="Re-run DDD tracker to confirm adoption",
                command="python -m tools.shifu.ddd_visualizer --dashboard",
                validation="Unit of Work adoption should show 25-50%+"
            )
        ]
        
        return PatternRecommendation(
            pattern_name="Unit of Work",
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(4, 6),
            rationale=f"You have {adoption:.0f}% adoption. Unit of Work has highest impact on maturity (+{expected_gain:.0f} points expected).",
            business_value="Prevents data corruption from partial updates. Ensures data consistency across all operations.",
            technical_benefit="Eliminates transaction management complexity. Reduces test flakiness. Atomic multi-step operations.",
            implementation_steps=steps,
            code_examples=[uow_example],
            modules_affected=[f"{modules_total - modules_using} modules need UnitOfWork"],
            files_to_create=["core/services/unit_of_work.py", "tests/unit/core/services/test_unit_of_work.py"],
            files_to_modify=[f"{modules_total - modules_using} service files", f"{modules_total - modules_using} repository files"],
            test_coverage_needed=8,
            complexity_level="Medium",
            breaking_changes=False,
            prerequisites=["Repository Pattern in place"],
            common_pitfalls=[
                "Forgetting to handle rollback on exceptions",
                "Nesting UnitOfWork contexts incorrectly",
                "Not testing rollback scenarios"
            ]
        )
    
    def _recommend_service_layer(
        self,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Recommendation for Service Layer pattern"""
        
        service_example = CodeExample(
            pattern_name="Service Layer",
            language="Python",
            code="""class DataProductService:
    \"\"\"
    Service Layer: Orchestrates business logic, delegates to repositories.
    Keeps Flask routes thin (routes should only call services).
    \"\"\"
    def __init__(self, repository):
        self._repository = repository
    
    def create_data_product(self, data: Dict) -> DataProduct:
        # Business validation
        self._validate_product_data(data)
        
        # Business logic
        product = self._enrich_product_data(data)
        
        # Delegate persistence
        return self._repository.create(product)
    
    def _validate_product_data(self, data: Dict):
        if not data.get('name'):
            raise ValueError("Product name required")
        # More business rules...
    
    def _enrich_product_data(self, data: Dict) -> Dict:
        data['created_at'] = datetime.now()
        data['status'] = 'active'
        return data

# In Flask route (thin controller)
@bp.route('/products', methods=['POST'])
def create_product():
    data = request.json
    product = service.create_data_product(data)  # Just call service
    return jsonify(product.to_dict()), 201
""",
            explanation="Service Layer extracts business logic from routes. Makes code testable without Flask, enables reuse across different interfaces.",
            file_path="modules/data_products_v2/backend/service.py"
        )
        
        steps = [
            ImplementationStep(
                step_number=1,
                title="Create Service class for module",
                description="Extract business logic from Flask routes into Service class",
                code_example=service_example,
                validation="Service can be tested without Flask"
            ),
            ImplementationStep(
                step_number=2,
                title="Inject repository into Service",
                description="Use dependency injection: service = Service(repository)",
                command=None,
                validation="Service is decoupled from repository implementation"
            ),
            ImplementationStep(
                step_number=3,
                title="Update Flask routes to use Service",
                description="Routes become thin: just call service methods",
                command=None,
                validation="Routes are <10 lines, just HTTP handling"
            ),
            ImplementationStep(
                step_number=4,
                title="Write service layer tests",
                description="Test business logic in isolation (mock repository)",
                command="pytest tests/unit/modules/*/test_service.py -v",
                validation="100% coverage on business logic"
            )
        ]
        
        return PatternRecommendation(
            pattern_name="Service Layer",
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(3, 4),
            rationale=f"You have {adoption:.0f}% adoption ({modules_using}/{modules_total} modules). Service Layer improves testability significantly.",
            business_value="Enables business logic reuse. Decouples from web framework. Easier to change UI without touching logic.",
            technical_benefit="Testable without HTTP. Clear separation of concerns. Reduces route complexity by 70%.",
            implementation_steps=steps,
            code_examples=[service_example],
            modules_affected=[f"{modules_total - modules_using} modules with thick routes"],
            files_to_create=[f"modules/*/backend/service.py ({modules_total - modules_using} files)"],
            files_to_modify=[f"{modules_total - modules_using} api.py files (make routes thin)"],
            test_coverage_needed=15,
            complexity_level="Low",
            breaking_changes=False,
            prerequisites=["None - can start immediately"],
            common_pitfalls=[
                "Putting database logic in service (should delegate to repository)",
                "Service methods that are just pass-throughs (no value)",
                "Not injecting dependencies (tight coupling)"
            ]
        )
    
    def _recommend_repository(
        self,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Recommendation for Repository Pattern"""
        
        repo_example = CodeExample(
            pattern_name="Repository Pattern",
            language="Python",
            code="""from core.repositories.base import AbstractRepository

class SQLiteDataProductRepository(AbstractRepository):
    \"\"\"
    Repository Pattern: Encapsulates data access logic.
    Business code talks to repository, not database directly.
    \"\"\"
    def __init__(self, connection):
        self._connection = connection
    
    def get_by_id(self, id: str) -> Optional[DataProduct]:
        cursor = self._connection.execute(
            "SELECT * FROM data_products WHERE id = ?", (id,)
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def create(self, entity: DataProduct) -> DataProduct:
        self._connection.execute(
            "INSERT INTO data_products (id, name, description) VALUES (?, ?, ?)",
            (entity.id, entity.name, entity.description)
        )
        return entity
    
    def _row_to_entity(self, row) -> DataProduct:
        return DataProduct(id=row[0], name=row[1], description=row[2])
""",
            explanation="Repository Pattern abstracts data access. Business code doesn't know if data comes from SQLite, HANA, or API. Easy to swap.",
            file_path="modules/data_products_v2/repositories/sqlite_repository.py"
        )
        
        steps = [
            ImplementationStep(
                step_number=1,
                title="Inherit from AbstractRepository",
                description="Create repository class extending core.repositories.base.AbstractRepository",
                code_example=repo_example,
                validation="Repository implements all required methods"
            ),
            ImplementationStep(
                step_number=2,
                title="Move database logic to repository",
                description="Extract SQL queries from routes/services into repository",
                command=None,
                validation="No raw SQL in business logic"
            ),
            ImplementationStep(
                step_number=3,
                title="Inject repository into service",
                description="Service receives repository via constructor",
                command=None,
                validation="Service testable with mock repository"
            )
        ]
        
        return PatternRecommendation(
            pattern_name="Repository Pattern",
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(2, 3),
            rationale=f"You have {adoption:.0f}% adoption ({modules_using}/{modules_total} modules). Repository Pattern is foundation for other patterns.",
            business_value="Easy to switch databases. Isolates persistence concerns. Enables data source flexibility.",
            technical_benefit="Testable data access. No vendor lock-in. Clear data contracts.",
            implementation_steps=steps,
            code_examples=[repo_example],
            modules_affected=[f"{modules_total - modules_using} modules with direct DB access"],
            files_to_create=[f"modules/*/repositories/*.py ({modules_total - modules_using} files)"],
            files_to_modify=[f"{modules_total - modules_using} service files"],
            test_coverage_needed=10,
            complexity_level="Low",
            breaking_changes=False,
            prerequisites=["AbstractRepository in core.repositories.base"],
            common_pitfalls=[
                "Leaking database details into repository interface",
                "Repository methods that return database cursors",
                "Not using dependency injection"
            ]
        )
    
    def _recommend_domain_events(
        self,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Recommendation for Domain Events pattern"""
        
        # Simplified implementation
        return PatternRecommendation(
            pattern_name="Domain Events",
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(4, 6),
            rationale=f"You have {adoption:.0f}% adoption. Domain Events enable loose coupling between modules.",
            business_value="Modules can react to changes without direct dependencies. Enables extensibility.",
            technical_benefit="Decoupled architecture. Easy to add new reactions. Improves maintainability.",
            implementation_steps=[],
            code_examples=[],
            modules_affected=[],
            files_to_create=["core/events/event_bus.py"],
            files_to_modify=[],
            test_coverage_needed=6,
            complexity_level="Medium",
            breaking_changes=False,
            prerequisites=["Service Layer"],
            common_pitfalls=["Overusing events", "Circular event dependencies"]
        )
    
    def _recommend_aggregate(
        self,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Recommendation for Aggregate Pattern"""
        
        # Simplified implementation
        return PatternRecommendation(
            pattern_name="Aggregate Pattern",
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(3, 5),
            rationale=f"You have {adoption:.0f}% adoption. Aggregates enforce consistency boundaries.",
            business_value="Guarantees data consistency. Enforces business invariants.",
            technical_benefit="Clear consistency boundaries. Prevents invalid states.",
            implementation_steps=[],
            code_examples=[],
            modules_affected=[],
            files_to_create=["core/domain/aggregate_root.py"],
            files_to_modify=[],
            test_coverage_needed=8,
            complexity_level="Medium",
            breaking_changes=False,
            prerequisites=["Repository Pattern"],
            common_pitfalls=["Aggregates too large", "Multiple aggregate roots per transaction"]
        )
    
    def _recommend_generic(
        self,
        pattern_name: str,
        priority: PatternPriority,
        adoption: float,
        target: float,
        expected_gain: float,
        modules_using: int,
        modules_total: int
    ) -> PatternRecommendation:
        """Generic recommendation template"""
        
        return PatternRecommendation(
            pattern_name=pattern_name,
            priority=priority,
            current_adoption=adoption,
            target_adoption=target,
            expected_maturity_gain=expected_gain,
            effort_hours=(2, 4),
            rationale=f"You have {adoption:.0f}% adoption of {pattern_name}.",
            business_value="Improves architecture quality.",
            technical_benefit="Better code organization.",
            implementation_steps=[],
            code_examples=[],
            modules_affected=[f"{modules_total - modules_using} modules"],
            files_to_create=[],
            files_to_modify=[],
            test_coverage_needed=5,
            complexity_level="Medium",
            breaking_changes=False,
            prerequisites=[],
            common_pitfalls=[]
        )
    
    def format_recommendation_markdown(self, rec: PatternRecommendation) -> str:
        """Format recommendation as beautiful markdown"""
        
        output = []
        
        # Header
        priority_emoji = {
            PatternPriority.CRITICAL: "🔴",
            PatternPriority.HIGH: "🟠",
            PatternPriority.MEDIUM: "🟡",
            PatternPriority.LOW: "🟢"
        }
        
        emoji = priority_emoji.get(rec.priority, "⚪")
        output.append(f"# {emoji} {rec.pattern_name} - {rec.priority.value} Priority")
        output.append("")
        
        # WHY Section
        output.append("## 🎯 WHY Implement This Pattern?")
        output.append("")
        output.append(f"**Current State**: {rec.current_adoption:.0f}% adoption")
        output.append(f"**Target State**: {rec.target_adoption:.0f}% adoption")
        output.append(f"**Expected Gain**: +{rec.expected_maturity_gain:.1f} maturity points")
        output.append("")
        output.append(f"**Rationale**: {rec.rationale}")
        output.append("")
        output.append(f"**Business Value**: {rec.business_value}")
        output.append("")
        output.append(f"**Technical Benefit**: {rec.technical_benefit}")
        output.append("")
        
        # EFFORT Section
        output.append("## ⏱️ EFFORT & COMPLEXITY")
        output.append("")
        output.append(f"**Estimated Time**: {rec.effort_hours[0]}-{rec.effort_hours[1]} hours")
        output.append(f"**Complexity**: {rec.complexity_level}")
        output.append(f"**Breaking Changes**: {'Yes ⚠️' if rec.breaking_changes else 'No ✅'}")
        output.append("")
        
        # HOW Section
        if rec.implementation_steps:
            output.append("## 🛠️ HOW TO IMPLEMENT")
            output.append("")
            for step in rec.implementation_steps:
                output.append(f"### Step {step.step_number}: {step.title}")
                output.append("")
                output.append(step.description)
                output.append("")
                
                if step.code_example:
                    output.append("```python")
                    output.append(step.code_example.code)
                    output.append("```")
                    output.append("")
                    output.append(f"**File**: `{step.code_example.file_path}`")
                    output.append("")
                    output.append(f"**Explanation**: {step.code_example.explanation}")
                    output.append("")
                
                if step.command:
                    output.append(f"**Command**: `{step.command}`")
                    output.append("")
                
                if step.validation:
                    output.append(f"✅ **Validation**: {step.validation}")
                    output.append("")
        
        # IMPACT Section
        output.append("## 📊 IMPACT")
        output.append("")
        output.append(f"**Modules Affected**: {len(rec.modules_affected)}")
        for module in rec.modules_affected:
            output.append(f"  - {module}")
        output.append("")
        
        output.append(f"**Files to Create**: {len(rec.files_to_create)}")
        for file in rec.files_to_create[:5]:  # Limit to 5
            output.append(f"  - {file}")
        output.append("")
        
        output.append(f"**Tests Needed**: ~{rec.test_coverage_needed} tests")
        output.append("")
        
        # RISKS Section
        if rec.prerequisites or rec.common_pitfalls:
            output.append("## ⚠️ PREREQUISITES & PITFALLS")
            output.append("")
            
            if rec.prerequisites:
                output.append("**Prerequisites**:")
                for prereq in rec.prerequisites:
                    output.append(f"  - {prereq}")
                output.append("")
            
            if rec.common_pitfalls:
                output.append("**Common Pitfalls to Avoid**:")
                for pitfall in rec.common_pitfalls:
                    output.append(f"  - ❌ {pitfall}")
                output.append("")
        
        return "\n".join(output)


def main():
    """CLI entry point for recommendations engine"""
    import argparse
    from tools.shifu.ddd_pattern_tracker import DDDPatternTracker
    
    parser = argparse.ArgumentParser(
        description="DDD Recommendations Engine - AI-Powered Guidance"
    )
    parser.add_argument(
        '--top',
        type=int,
        default=3,
        help='Number of recommendations to show (default: 3)'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        help='Get recommendation for specific pattern'
    )
    parser.add_argument(
        '--save',
        type=str,
        help='Save recommendations to file'
    )
    
    args = parser.parse_args()
    
    # Analyze codebase
    tracker = DDDPatternTracker()
    report = tracker.analyze_codebase()
    
    # Generate recommendations
    engine = DDDRecommendationsEngine()
    recommendations = engine.generate_recommendations(
        report.to_dict(),
        max_recommendations=args.top
    )
    
    # Filter by pattern if specified
    if args.pattern:
        recommendations = [r for r in recommendations if r.pattern_name == args.pattern]
    
    # Output
    if not recommendations:
        print("No recommendations available. All patterns at excellent level! 🎉")
        return
    
    print("=" * 70)
    print("🤖 DDD Pattern Recommendations")
    print("=" * 70)
    print()
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{'=' * 70}")
        print(f"Recommendation #{i}")
        print('=' * 70)
        print(engine.format_recommendation_markdown(rec))
        
        if args.save:
            filename = f"{args.save}_recommendation_{i}.md"
            with open(filename, 'w') as f:
                f.write(engine.format_recommendation_markdown(rec))
            print(f"\n💾 Saved to: {filename}")


if __name__ == '__main__':
    main()