"""
Unit tests for Performance Agent

Tests performance optimization analysis:
- N+1 query pattern detection
- Nested loop (O(n²)) detection
- Missing cache opportunities
- Inefficient operations
"""

import pytest
from pathlib import Path
from tools.fengshui.agents import PerformanceAgent, Severity


class TestPerformanceAgentInitialization:
    """Test agent initialization and capabilities"""
    
    def test_agent_initializes_correctly(self):
        # ARRANGE & ACT
        agent = PerformanceAgent()
        
        # ASSERT
        assert agent.name == "performance"
        assert agent.logger is not None
        assert len(agent.db_call_methods) > 0
    
    def test_get_capabilities_returns_performance_checks(self):
        # ARRANGE
        agent = PerformanceAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert len(capabilities) == 6
        assert "N+1" in capabilities[0]
        assert "Nested loop" in capabilities[1]
        assert "cache" in capabilities[2].lower()


class TestNPlusOneDetection:
    """Test N+1 query pattern detection"""
    
    def test_detects_database_call_in_for_loop(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
def process_items(items):
    for item in items:
        result = db.execute(query)  # N+1 pattern!
        process(result)
""")
        
        # ACT
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "N+1 Query Pattern"
        assert findings[0].severity == Severity.HIGH
        assert "bulk query" in findings[0].recommendation.lower()
    
    def test_detects_query_method_in_loop(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
def get_all_data(ids):
    results = []
    for id in ids:
        data = session.query(Model).filter_by(id=id).first()
        results.append(data)
    return results
""")
        
        # ACT
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "N+1" in findings[0].category
    
    def test_detects_fetchone_in_while_loop(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'reader.py'
        py_file.write_text("""
def read_all():
    results = []
    while True:
        row = cursor.fetchone()
        if not row:
            break
        results.append(row)
""")
        
        # ACT
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert len(findings) == 1
    
    def test_allows_loop_without_database_calls(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'processor.py'
        py_file.write_text("""
def process_items(items):
    for item in items:
        process(item)  # No DB call
        transform(item)
""")
        
        # ACT
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert len(findings) == 0


class TestNestedLoopDetection:
    """Test nested loop (O(n²)) detection"""
    
    def test_detects_nested_for_loops(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'algorithm.py'
        py_file.write_text("""
def find_pairs(items):
    for i in items:
        for j in items:
            if i != j:
                check_pair(i, j)
""")
        
        # ACT
        findings = agent._detect_nested_loops(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Nested Loop"
        assert findings[0].severity == Severity.MEDIUM
        assert "dictionary" in findings[0].recommendation.lower()
    
    def test_detects_for_inside_while(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'processor.py'
        py_file.write_text("""
def process():
    while condition:
        for item in batch:
            process(item)
""")
        
        # ACT
        findings = agent._detect_nested_loops(py_file)
        
        # ASSERT
        assert len(findings) == 1
    
    def test_allows_single_level_loop(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'simple.py'
        py_file.write_text("""
def process_items(items):
    for item in items:
        result = transform(item)
        save(result)
""")
        
        # ACT
        findings = agent._detect_nested_loops(py_file)
        
        # ASSERT
        assert len(findings) == 0


class TestMissingCacheDetection:
    """Test cache opportunity detection"""
    
    def test_detects_get_method_with_loop_without_cache(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
def get_expensive_data(self):
    results = []
    for item in heavy_computation():
        results.append(item)
    return results
""")
        
        # ACT
        findings = agent._detect_missing_cache(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Missing Cache"
        assert findings[0].severity == Severity.LOW
        assert "@lru_cache" in findings[0].recommendation
    
    def test_detects_load_method_without_cache(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'loader.py'
        py_file.write_text("""
def load_config(self):
    data = {}
    for key in keys:
        data[key] = compute(key)
    return data
""")
        
        # ACT
        findings = agent._detect_missing_cache(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "load_config" in findings[0].description
    
    def test_allows_cached_get_method(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'cached.py'
        py_file.write_text("""
from functools import lru_cache

@lru_cache(maxsize=128)
def get_data(self):
    for item in items:
        process(item)
    return result
""")
        
        # ACT
        findings = agent._detect_missing_cache(py_file)
        
        # ASSERT
        assert len(findings) == 0  # Has @lru_cache
    
    def test_allows_simple_methods_without_loops(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'simple.py'
        py_file.write_text("""
def get_value(self):
    return self.value  # No expensive operation
""")
        
        # ACT
        findings = agent._detect_missing_cache(py_file)
        
        # ASSERT
        assert len(findings) == 0  # Simple getter, no loop


class TestInefficientOperations:
    """Test inefficient operation detection"""
    
    def test_detects_string_concat_in_loop(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'builder.py'
        py_file.write_text("""
def build_string(items):
    result = ""
    for item in items:
        result += str(item)  # Inefficient!
    return result
""")
        
        # ACT
        findings = agent._detect_inefficient_operations(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Inefficient String Operation"
        assert findings[0].severity == Severity.LOW
        assert "join" in findings[0].recommendation.lower()
    
    def test_allows_efficient_operations(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'efficient.py'
        py_file.write_text("""
def build_string(items):
    parts = []
    for item in items:
        parts.append(str(item))
    return ''.join(parts)  # Efficient!
""")
        
        # ACT
        findings = agent._detect_inefficient_operations(py_file)
        
        # ASSERT
        assert len(findings) == 0


class TestModuleAnalysis:
    """Test full module analysis"""
    
    def test_analyzes_complete_module(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        backend_dir = tmp_path / 'backend'
        backend_dir.mkdir()
        
        # Create service with N+1 pattern
        (backend_dir / 'service.py').write_text("""
def get_all(items):
    for item in items:
        db.query(item)
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.agent_name == "performance"
        assert report.module_path == tmp_path
        assert len(report.findings) >= 1
        assert report.metrics['files_analyzed'] >= 1
    
    def test_handles_invalid_module_path(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        invalid_path = tmp_path / "nonexistent"
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "invalid" in report.summary.lower()
    
    def test_generates_clean_report_no_issues(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        (tmp_path / 'clean.py').write_text("""
def simple_function():
    return 42
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "no issues" in report.summary.lower()
    
    def test_skips_test_files(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        test_file = tmp_path / 'test_something.py'
        test_file.write_text("""
def test_with_loop():
    for i in range(10):
        db.execute(query)  # Should be ignored in test file
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert len(report.findings) == 0  # Test files skipped


class TestMetrics:
    """Test metrics calculation"""
    
    def test_metrics_count_findings_by_severity(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'mixed.py'
        py_file.write_text("""
def func1():
    for i in items:
        db.execute(q)  # HIGH
    
def func2():
    for i in range(10):
        for j in range(10):  # MEDIUM
            pass
    
def get_data():
    for x in y:  # LOW (missing cache)
        pass
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['high_count'] >= 1  # N+1
        assert report.metrics['medium_count'] >= 1  # Nested loop
    
    def test_metrics_count_files_analyzed(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        (tmp_path / 'file1.py').write_text('def f(): pass')
        (tmp_path / 'file2.py').write_text('def g(): pass')
        (tmp_path / 'file3.py').write_text('def h(): pass')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['files_analyzed'] == 3


class TestErrorHandling:
    """Test error handling"""
    
    def test_handles_invalid_python_gracefully(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'invalid.py'
        py_file.write_text('this is not valid python {{{')
        
        # ACT (should not crash)
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert isinstance(findings, list)


class TestRecommendations:
    """Test recommendation quality"""
    
    def test_n_plus_one_recommendation_suggests_bulk(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
for item in items:
    db.execute(query)
""")
        
        # ACT
        findings = agent._detect_n_plus_one(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert "bulk" in findings[0].recommendation.lower()
    
    def test_nested_loop_recommendation_suggests_optimization(self, tmp_path):
        # ARRANGE
        agent = PerformanceAgent()
        py_file = tmp_path / 'algorithm.py'
        py_file.write_text("""
for i in items:
    for j in items:
        compare(i, j)
""")
        
        # ACT
        findings = agent._detect_nested_loops(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert any(word in findings[0].recommendation.lower() 
                  for word in ['dictionary', 'set', 'comprehension'])