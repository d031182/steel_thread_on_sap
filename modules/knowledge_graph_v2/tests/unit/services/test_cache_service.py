"""
Unit Tests for GraphCacheService

Tests cache orchestration with automatic rebuild capability.
This tests the KEY feature: cache resilience!
"""
import pytest
from unittest.mock import Mock, MagicMock
from modules.knowledge_graph_v2.services.graph_cache_service import GraphCacheService
from modules.knowledge_graph_v2.domain import Graph, GraphType


@pytest.fixture
def mock_cache_repo():
    """Create mock cache repository"""
    repo = Mock()
    repo.get = Mock(return_value=None)
    repo.save = Mock()
    repo.exists = Mock(return_value=False)
    repo.delete = Mock(return_value=True)
    return repo


@pytest.fixture
def mock_schema_builder():
    """Create mock schema builder"""
    builder = Mock()
    # Default: returns empty graph
    builder.build_from_csn = Mock(return_value=Graph('schema', GraphType.SCHEMA))
    return builder


@pytest.fixture
def cache_service(mock_cache_repo, mock_schema_builder):
    """Create cache service with mocked dependencies"""
    return GraphCacheService(
        cache_repository=mock_cache_repo,
        schema_builder=mock_schema_builder
    )


@pytest.mark.unit
@pytest.mark.fast
class TestCacheServiceInitialization:
    """Test service initialization"""
    
    def test_init_succeeds(self, mock_cache_repo, mock_schema_builder):
        """Test service initializes with dependencies"""
        # ACT
        service = GraphCacheService(mock_cache_repo, mock_schema_builder)
        
        # ASSERT
        assert service.cache_repo == mock_cache_repo
        assert service.schema_builder == mock_schema_builder


@pytest.mark.unit
@pytest.mark.fast
class TestCacheHit:
    """Test cache HIT scenarios (fast path)"""
    
    def test_get_or_rebuild_uses_cache_when_available(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test cache HIT: Returns cached graph, does NOT rebuild"""
        # ARRANGE
        cached_graph = Graph('schema', GraphType.SCHEMA)
        mock_cache_repo.get.return_value = cached_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        assert result == cached_graph
        mock_cache_repo.get.assert_called_once_with('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.assert_not_called()  # Did NOT rebuild!


@pytest.mark.unit
@pytest.mark.fast
class TestCacheMiss:
    """Test cache MISS scenarios (rebuild path)"""
    
    def test_get_or_rebuild_rebuilds_when_cache_empty(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test cache MISS: Rebuilds from CSN when cache empty"""
        # ARRANGE
        mock_cache_repo.get.return_value = None  # Cache miss
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        assert result == fresh_graph
        mock_cache_repo.get.assert_called_once()
        mock_schema_builder.build_from_csn.assert_called_once()  # DID rebuild
        mock_cache_repo.save.assert_called_once_with(fresh_graph)  # Saved to cache
    
    def test_get_or_rebuild_rebuilds_when_cache_corrupted(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test cache CORRUPTED: Rebuilds when cache load fails"""
        # ARRANGE
        mock_cache_repo.get.side_effect = Exception("Cache corrupted!")
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        assert result == fresh_graph
        mock_schema_builder.build_from_csn.assert_called_once()  # DID rebuild
        mock_cache_repo.save.assert_called_once_with(fresh_graph)  # Saved to cache


@pytest.mark.unit
@pytest.mark.fast
class TestForceRebuild:
    """Test force rebuild scenarios"""
    
    def test_force_rebuild_deletes_old_cache(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test force rebuild: Deletes old cache before rebuilding"""
        # ARRANGE
        mock_cache_repo.exists.return_value = True  # Cache exists
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.force_rebuild_schema()
        
        # ASSERT
        mock_cache_repo.exists.assert_called_once_with('schema', GraphType.SCHEMA)
        mock_cache_repo.delete.assert_called_once_with('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.assert_called_once()
        mock_cache_repo.save.assert_called_once_with(fresh_graph)
    
    def test_force_rebuild_ignores_cache(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test force rebuild: Does NOT call get (ignores cache)"""
        # ARRANGE
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.force_rebuild_schema()
        
        # ASSERT
        mock_cache_repo.get.assert_not_called()  # Did NOT check cache
        mock_schema_builder.build_from_csn.assert_called_once()  # DID rebuild


@pytest.mark.unit
@pytest.mark.fast
class TestCacheUtilities:
    """Test utility methods"""
    
    def test_exists_in_cache_returns_true_when_cached(
        self, cache_service, mock_cache_repo
    ):
        """Test exists check returns true when cached"""
        # ARRANGE
        mock_cache_repo.exists.return_value = True
        
        # ACT
        result = cache_service.exists_in_cache('schema', GraphType.SCHEMA)
        
        # ASSERT
        assert result is True
        mock_cache_repo.exists.assert_called_once_with('schema', GraphType.SCHEMA)
    
    def test_exists_in_cache_returns_false_when_not_cached(
        self, cache_service, mock_cache_repo
    ):
        """Test exists check returns false when not cached"""
        # ARRANGE
        mock_cache_repo.exists.return_value = False
        
        # ACT
        result = cache_service.exists_in_cache('schema', GraphType.SCHEMA)
        
        # ASSERT
        assert result is False
    
    def test_clear_cache_deletes_schema_cache(
        self, cache_service, mock_cache_repo
    ):
        """Test clear cache deletes schema graphs"""
        # ACT
        result = cache_service.clear_cache(GraphType.SCHEMA)
        
        # ASSERT
        mock_cache_repo.delete.assert_called_once_with('schema', GraphType.SCHEMA)
        assert result is True


@pytest.mark.unit
@pytest.mark.fast
class TestRebuildErrorHandling:
    """Test error handling during rebuild"""
    
    def test_get_or_rebuild_propagates_build_errors(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test rebuild errors are propagated to caller"""
        # ARRANGE
        mock_cache_repo.get.return_value = None  # Cache miss
        mock_schema_builder.build_from_csn.side_effect = Exception("CSN parse error!")
        
        # ACT & ASSERT
        with pytest.raises(Exception, match="CSN parse error"):
            cache_service.get_or_rebuild_schema_graph()
    
    def test_force_rebuild_propagates_build_errors(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test force rebuild errors are propagated"""
        # ARRANGE
        mock_schema_builder.build_from_csn.side_effect = Exception("Build failed!")
        
        # ACT & ASSERT
        with pytest.raises(Exception, match="Build failed"):
            cache_service.force_rebuild_schema()


@pytest.mark.unit
@pytest.mark.fast
class TestCachePerformancePath:
    """Test performance characteristics"""
    
    def test_cache_hit_is_fast_path(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test cache hit path is faster (no build)"""
        # ARRANGE
        cached_graph = Graph('schema', GraphType.SCHEMA)
        mock_cache_repo.get.return_value = cached_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        # Fast path: only 1 call (get), no build, no save
        assert mock_cache_repo.get.call_count == 1
        assert mock_schema_builder.build_from_csn.call_count == 0
        assert mock_cache_repo.save.call_count == 0
    
    def test_cache_miss_is_slow_path(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """Test cache miss path is slower (build + save)"""
        # ARRANGE
        mock_cache_repo.get.return_value = None
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        # Slow path: 3 calls (get + build + save)
        assert mock_cache_repo.get.call_count == 1
        assert mock_schema_builder.build_from_csn.call_count == 1
        assert mock_cache_repo.save.call_count == 1


@pytest.mark.unit
@pytest.mark.fast
class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_scenario_cache_deleted_by_user(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """
        Scenario: User deletes cache file manually
        Expected: Automatic rebuild on next access
        """
        # ARRANGE
        mock_cache_repo.get.return_value = None  # Cache deleted
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.get_or_rebuild_schema_graph()
        
        # ASSERT
        assert result == fresh_graph  # Got fresh graph
        mock_schema_builder.build_from_csn.assert_called_once()  # Rebuilt
    
    def test_scenario_csn_files_updated(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """
        Scenario: CSN files updated, need fresh graph
        Expected: Force rebuild ignores stale cache
        """
        # ARRANGE
        mock_cache_repo.exists.return_value = True  # Stale cache exists
        fresh_graph = Graph('schema', GraphType.SCHEMA)
        mock_schema_builder.build_from_csn.return_value = fresh_graph
        
        # ACT
        result = cache_service.force_rebuild_schema()
        
        # ASSERT
        mock_cache_repo.delete.assert_called_once()  # Deleted stale cache
        mock_schema_builder.build_from_csn.assert_called_once()  # Built fresh
        mock_cache_repo.save.assert_called_once()  # Saved fresh cache
    
    def test_scenario_repeated_access_uses_cache(
        self, cache_service, mock_cache_repo, mock_schema_builder
    ):
        """
        Scenario: Multiple accesses to same graph
        Expected: Only first access rebuilds, rest use cache
        """
        # ARRANGE
        # First call: cache miss
        # Second call: cache hit
        cached_graph = Graph('schema', GraphType.SCHEMA)
        mock_cache_repo.get.side_effect = [None, cached_graph]
        mock_schema_builder.build_from_csn.return_value = cached_graph
        
        # ACT
        result1 = cache_service.get_or_rebuild_schema_graph()  # First: rebuild
        result2 = cache_service.get_or_rebuild_schema_graph()  # Second: cache hit
        
        # ASSERT
        assert mock_schema_builder.build_from_csn.call_count == 1  # Only built once
        assert mock_cache_repo.get.call_count == 2  # Checked cache twice