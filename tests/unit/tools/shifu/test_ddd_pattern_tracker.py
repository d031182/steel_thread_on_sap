"""
Unit Tests for DDD Pattern Tracker
===================================

Tests the DDD pattern adoption analysis system.
"""

import pytest
from pathlib import Path
from tools.shifu.ddd_pattern_tracker import (
    DDDPatternTracker,
    PatternAdoptionScore,
    DDDMaturityReport
)


class TestDDDPatternTracker:
    """Test suite for DDD Pattern Tracker"""
    
    def test_initialization(self):
        """Test tracker initializes with project root"""
        tracker = DDDPatternTracker(verbose=False)
        assert tracker.project_root == Path.cwd()
        assert tracker.verbose == False
    
    def test_initialization_with_custom_root(self, tmp_path):
        """Test tracker accepts custom project root"""
        tracker = DDDPatternTracker(project_root=tmp_path, verbose=True)
        assert tracker.project_root == tmp_path
        assert tracker.verbose == True
    
    def test_should_skip_test_files(self):
        """Test that test files are skipped"""
        tracker = DDDPatternTracker()
        
        assert tracker._should_skip(Path("tests/unit/test_something.py"))
        assert tracker._should_skip(Path("test_module.py"))
        assert tracker._should_skip(Path("modules/something/tests/test_api.py"))
    
    def test_should_skip_pycache(self):
        """Test that __pycache__ is skipped"""
        tracker = DDDPatternTracker()
        
        assert tracker._should_skip(Path("__pycache__/module.py"))
        assert tracker._should_skip(Path("modules/__pycache__/something.py"))
    
    def test_should_skip_archive(self):
        """Test that archive/ directory is skipped"""
        tracker = DDDPatternTracker()
        
        assert tracker._should_skip(Path("archive/old_module.py"))
        assert tracker._should_skip(Path("archive/feature_manager/backend/api.py"))
    
    def test_should_not_skip_valid_files(self):
        """Test that valid module files are NOT skipped"""
        tracker = DDDPatternTracker()
        
        assert not tracker._should_skip(Path("modules/knowledge_graph_v2/backend/api.py"))
        assert not tracker._should_skip(Path("core/services/my_service.py"))
        assert not tracker._should_skip(Path("server.py"))
    
    def test_determine_maturity_level(self):
        """Test maturity level calculation"""
        tracker = DDDPatternTracker()
        
        assert tracker._determine_maturity_level(90.0) == "Master"
        assert tracker._determine_maturity_level(70.0) == "Skilled"
        assert tracker._determine_maturity_level(50.0) == "Practicing"
        assert tracker._determine_maturity_level(30.0) == "Learning"
        assert tracker._determine_maturity_level(10.0) == "Beginner"
    
    def test_analyze_repository_pattern_not_started(self, tmp_path):
        """Test Repository Pattern detection when not implemented"""
        # Create test file without repository
        test_file = tmp_path / "modules" / "test_module" / "api.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def get_data(): return []")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_repository_pattern([test_file])
        
        assert score.pattern_name == "Repository Pattern"
        assert score.adoption_percentage == 0.0
        assert score.maturity_level == "Not Started"
        assert "⭐ Start with Repository Pattern" in score.recommendation
    
    def test_analyze_repository_pattern_with_abstract_repository(self, tmp_path):
        """Test Repository Pattern detection with AbstractRepository"""
        # Create test file with AbstractRepository
        test_file = tmp_path / "modules" / "test_module" / "repository.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("""
from core.repositories import AbstractRepository

class MyRepository(AbstractRepository):
    def get(self, id): pass
""")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_repository_pattern([test_file])
        
        assert score.pattern_name == "Repository Pattern"
        assert score.adoption_percentage == 100.0  # 1/1 module
        assert score.modules_using == 1
        assert score.modules_total == 1
        assert score.maturity_level == "Excellent"
    
    def test_analyze_service_layer_not_started(self, tmp_path):
        """Test Service Layer detection when not implemented"""
        test_file = tmp_path / "modules" / "test_module" / "api.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def get_data(): return []")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_service_layer([test_file])
        
        assert score.pattern_name == "Service Layer"
        assert score.adoption_percentage == 0.0
        assert score.maturity_level == "Not Started"
        assert "⭐ Implement Service Layer" in score.recommendation
    
    def test_analyze_service_layer_with_service_class(self, tmp_path):
        """Test Service Layer detection with *Service class"""
        test_file = tmp_path / "modules" / "test_module" / "service.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("""
class KPIService:
    def __init__(self, repository):
        self.repository = repository
    
    def calculate_kpis(self):
        return {}
""")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_service_layer([test_file])
        
        assert score.pattern_name == "Service Layer"
        assert score.adoption_percentage == 100.0
        assert score.modules_using == 1
        assert score.maturity_level == "Excellent"
    
    def test_analyze_unit_of_work_not_started(self, tmp_path):
        """Test Unit of Work detection when not implemented"""
        test_file = tmp_path / "modules" / "test_module" / "api.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def process(): pass")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_unit_of_work([test_file])
        
        assert score.pattern_name == "Unit of Work"
        assert score.adoption_percentage == 0.0
        assert score.maturity_level == "Not Started"
        assert "⭐⭐ START HERE" in score.recommendation
    
    def test_analyze_aggregate_pattern_not_started(self, tmp_path):
        """Test Aggregate Pattern detection when not implemented"""
        test_file = tmp_path / "modules" / "test_module" / "model.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("class Order: pass")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_aggregate_pattern([test_file])
        
        assert score.pattern_name == "Aggregate Pattern"
        assert score.adoption_percentage == 0.0
        assert score.maturity_level == "Not Started"
    
    def test_analyze_aggregate_with_aggregate_root(self, tmp_path):
        """Test Aggregate detection with AggregateRoot"""
        test_file = tmp_path / "modules" / "test_module" / "domain.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("""
class Order(AggregateRoot):
    def add_item(self, item):
        self._items.append(item)
""")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_aggregate_pattern([test_file])
        
        assert score.pattern_name == "Aggregate Pattern"
        assert score.adoption_percentage == 100.0
        assert score.modules_using == 1
    
    def test_analyze_domain_events_not_started(self, tmp_path):
        """Test Domain Events detection when not implemented"""
        test_file = tmp_path / "modules" / "test_module" / "api.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("def handle_request(): pass")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_domain_events([test_file])
        
        assert score.pattern_name == "Domain Events"
        assert score.adoption_percentage == 0.0
        assert score.maturity_level == "Not Started"
    
    def test_analyze_domain_events_with_event_bus(self, tmp_path):
        """Test Domain Events detection with EventBus"""
        test_file = tmp_path / "modules" / "test_module" / "events.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("""
class EventBus:
    def publish(self, event):
        pass

class OrderCreated:
    pass
""")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        score = tracker._analyze_domain_events([test_file])
        
        assert score.pattern_name == "Domain Events"
        assert score.adoption_percentage == 100.0
        assert score.modules_using == 1
    
    def test_analyze_codebase_returns_report(self, tmp_path):
        """Test full codebase analysis returns valid report"""
        # Create minimal module structure
        module_path = tmp_path / "modules" / "test_module"
        module_path.mkdir(parents=True)
        
        (module_path / "repository.py").write_text("""
class TestRepository(AbstractRepository):
    pass
""")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        report = tracker.analyze_codebase()
        
        assert isinstance(report, DDDMaturityReport)
        assert 0 <= report.overall_score <= 100
        assert report.maturity_level in ["Beginner", "Learning", "Practicing", "Skilled", "Master"]
        assert len(report.pattern_scores) == 5
        assert report.modules_analyzed >= 0
    
    def test_report_to_dict(self):
        """Test DDDMaturityReport converts to dictionary"""
        score = PatternAdoptionScore(
            pattern_name="Test Pattern",
            adoption_percentage=50.0,
            modules_using=2,
            modules_total=4,
            maturity_level="Partial",
            evidence=["file1.py", "file2.py"],
            recommendation="Keep going"
        )
        
        report = DDDMaturityReport(
            overall_score=50.0,
            maturity_level="Practicing",
            pattern_scores=[score],
            timestamp="2026-02-13T00:00:00",
            modules_analyzed=10
        )
        
        report_dict = report.to_dict()
        
        assert report_dict['overall_score'] == 50.0
        assert report_dict['maturity_level'] == "Practicing"
        assert len(report_dict['pattern_scores']) == 1
        assert report_dict['pattern_scores'][0]['pattern_name'] == "Test Pattern"
    
    def test_maturity_levels_correct(self):
        """Test maturity level boundaries"""
        tracker = DDDPatternTracker()
        
        # Test all boundary conditions
        assert tracker._determine_maturity_level(100) == "Master"
        assert tracker._determine_maturity_level(81) == "Master"
        assert tracker._determine_maturity_level(80) == "Skilled"
        assert tracker._determine_maturity_level(61) == "Skilled"
        assert tracker._determine_maturity_level(60) == "Practicing"
        assert tracker._determine_maturity_level(41) == "Practicing"
        assert tracker._determine_maturity_level(40) == "Learning"
        assert tracker._determine_maturity_level(21) == "Learning"
        assert tracker._determine_maturity_level(20) == "Beginner"
        assert tracker._determine_maturity_level(0) == "Beginner"


class TestPatternAdoptionScore:
    """Test PatternAdoptionScore dataclass"""
    
    def test_pattern_adoption_score_creation(self):
        """Test creating PatternAdoptionScore"""
        score = PatternAdoptionScore(
            pattern_name="Repository",
            adoption_percentage=75.0,
            modules_using=3,
            modules_total=4,
            maturity_level="Good",
            evidence=["file1.py", "file2.py"],
            recommendation="Keep it up"
        )
        
        assert score.pattern_name == "Repository"
        assert score.adoption_percentage == 75.0
        assert score.modules_using == 3
        assert score.modules_total == 4
        assert score.maturity_level == "Good"
        assert len(score.evidence) == 2
    
    def test_pattern_score_with_no_evidence(self):
        """Test pattern score with empty evidence"""
        score = PatternAdoptionScore(
            pattern_name="Unit of Work",
            adoption_percentage=0.0,
            modules_using=0,
            modules_total=5,
            maturity_level="Not Started",
            evidence=[],
            recommendation="Start implementation"
        )
        
        assert score.adoption_percentage == 0.0
        assert len(score.evidence) == 0


class TestDDDMaturityReport:
    """Test DDDMaturityReport dataclass"""
    
    def test_maturity_report_creation(self):
        """Test creating DDDMaturityReport"""
        scores = [
            PatternAdoptionScore(
                pattern_name="Repository",
                adoption_percentage=50.0,
                modules_using=2,
                modules_total=4,
                maturity_level="Good",
                evidence=[],
                recommendation="Expand"
            )
        ]
        
        report = DDDMaturityReport(
            overall_score=50.0,
            maturity_level="Practicing",
            pattern_scores=scores,
            timestamp="2026-02-13T00:00:00",
            modules_analyzed=100
        )
        
        assert report.overall_score == 50.0
        assert report.maturity_level == "Practicing"
        assert len(report.pattern_scores) == 1
        assert report.modules_analyzed == 100
    
    def test_report_to_dict_serialization(self):
        """Test report serializes to dictionary correctly"""
        scores = [
            PatternAdoptionScore(
                pattern_name="Repository",
                adoption_percentage=50.0,
                modules_using=2,
                modules_total=4,
                maturity_level="Good",
                evidence=["file1.py"],
                recommendation="Good work"
            ),
            PatternAdoptionScore(
                pattern_name="Service Layer",
                adoption_percentage=25.0,
                modules_using=1,
                modules_total=4,
                maturity_level="Partial",
                evidence=[],
                recommendation="Add more"
            )
        ]
        
        report = DDDMaturityReport(
            overall_score=37.5,
            maturity_level="Learning",
            pattern_scores=scores,
            timestamp="2026-02-13T00:00:00",
            modules_analyzed=50
        )
        
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert report_dict['overall_score'] == 37.5
        assert report_dict['maturity_level'] == "Learning"
        assert len(report_dict['pattern_scores']) == 2
        assert report_dict['pattern_scores'][0]['pattern_name'] == "Repository"
        assert report_dict['pattern_scores'][1]['pattern_name'] == "Service Layer"


class TestRealProjectAnalysis:
    """Test against real project structure"""
    
    def test_analyze_real_project(self):
        """Test analyzing the actual project"""
        tracker = DDDPatternTracker(verbose=False)
        report = tracker.analyze_codebase()
        
        # Validate report structure
        assert isinstance(report, DDDMaturityReport)
        assert 0 <= report.overall_score <= 100
        assert report.maturity_level in ["Beginner", "Learning", "Practicing", "Skilled", "Master"]
        assert len(report.pattern_scores) == 5
        assert report.modules_analyzed > 0
        
        # Validate each pattern score
        for ps in report.pattern_scores:
            assert isinstance(ps, PatternAdoptionScore)
            assert 0 <= ps.adoption_percentage <= 100
            assert ps.modules_using >= 0
            assert ps.modules_total > 0
            assert ps.modules_using <= ps.modules_total
            assert ps.maturity_level in ["Not Started", "Partial", "Good", "Excellent"]
    
    def test_repository_pattern_detected(self):
        """Test that Repository Pattern is detected in real project"""
        tracker = DDDPatternTracker(verbose=False)
        report = tracker.analyze_codebase()
        
        repo_score = next(ps for ps in report.pattern_scores if ps.pattern_name == "Repository Pattern")
        
        # We know we have repositories in the project
        assert repo_score.adoption_percentage > 0
        assert repo_score.modules_using > 0
        assert len(repo_score.evidence) > 0
    
    def test_service_layer_detected(self):
        """Test that Service Layer is detected in real project"""
        tracker = DDDPatternTracker(verbose=False)
        report = tracker.analyze_codebase()
        
        service_score = next(ps for ps in report.pattern_scores if ps.pattern_name == "Service Layer")
        
        # We know we have services in the project
        assert service_score.adoption_percentage > 0
        assert service_score.modules_using > 0
    
    def test_unit_of_work_not_implemented_yet(self):
        """Test that Unit of Work shows as not implemented (expected)"""
        tracker = DDDPatternTracker(verbose=False)
        report = tracker.analyze_codebase()
        
        uow_score = next(ps for ps in report.pattern_scores if ps.pattern_name == "Unit of Work")
        
        # Unit of Work not implemented yet in modules (only in tools/)
        assert uow_score.modules_using == 0
        assert uow_score.maturity_level == "Not Started"
        assert "⭐⭐ START HERE" in uow_score.recommendation


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_project(self, tmp_path):
        """Test analyzing empty project"""
        tracker = DDDPatternTracker(project_root=tmp_path)
        report = tracker.analyze_codebase()
        
        assert report.overall_score >= 0
        assert report.modules_analyzed == 0
        for ps in report.pattern_scores:
            assert ps.adoption_percentage >= 0
    
    def test_project_with_no_modules_directory(self, tmp_path):
        """Test project without modules/ directory"""
        (tmp_path / "core").mkdir()
        (tmp_path / "core" / "api.py").write_text("def test(): pass")
        
        tracker = DDDPatternTracker(project_root=tmp_path)
        report = tracker.analyze_codebase()
        
        # Should handle gracefully
        assert isinstance(report, DDDMaturityReport)
        assert report.modules_analyzed >= 0
    
    def test_file_read_error_handling(self, tmp_path):
        """Test handling of files that cannot be read"""
        tracker = DDDPatternTracker(project_root=tmp_path, verbose=False)
        
        # Create file that will fail to read (permissions, encoding, etc.)
        # For testing, we just ensure no crash on problematic files
        files = [Path("nonexistent.py")]
        
        # Should not crash
        score = tracker._analyze_repository_pattern(files)
        assert score.adoption_percentage >= 0