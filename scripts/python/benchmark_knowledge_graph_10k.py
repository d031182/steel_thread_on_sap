"""
Knowledge Graph Performance Benchmark - 10K+ Nodes

Tests Knowledge Graph scalability with large datasets.
Validates performance at enterprise scale.

Usage:
    python scripts/python/benchmark_knowledge_graph_10k.py
    
Output:
    - Performance metrics (timing, throughput)
    - Bottleneck identification
    - Scalability recommendations
"""
import sys
import time
import sqlite3
import statistics
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.knowledge_graph_v2.domain import (
    Graph, GraphNode, GraphEdge, GraphType, NodeType, EdgeType
)
from modules.knowledge_graph_v2.repositories.sqlite_graph_cache_repository import (
    SqliteGraphCacheRepository
)


class PerformanceBenchmark:
    """Performance benchmark orchestrator"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.db_path = "modules/knowledge_graph_v2/database/graph_cache_benchmark.db"
        
        # Ensure database directory exists
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure clean slate
        if db_file.exists():
            db_file.unlink()
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        print("=" * 80)
        print("KNOWLEDGE GRAPH PERFORMANCE BENCHMARK - 10K+ NODES")
        print("=" * 80)
        print()
        
        # Benchmark 1: Write Performance
        print("📊 Benchmark 1: Write Performance (10K nodes)")
        self.benchmark_write_10k_nodes()
        print()
        
        # Benchmark 2: Read Performance
        print("📊 Benchmark 2: Read Performance")
        self.benchmark_read_performance()
        print()
        
        # Benchmark 3: Query Performance
        print("📊 Benchmark 3: Query Performance (node lookup)")
        self.benchmark_query_performance()
        print()
        
        # Benchmark 4: Graph Construction
        print("📊 Benchmark 4: In-Memory Graph Construction")
        self.benchmark_graph_construction()
        print()
        
        # Benchmark 5: Batch Operations
        print("📊 Benchmark 5: Batch Operations (1K iterations)")
        self.benchmark_batch_operations()
        print()
        
        # Summary
        self.print_summary()
        
        return self.results
    
    def benchmark_write_10k_nodes(self) -> None:
        """
        Benchmark: Write 10K nodes + 30K edges to database
        
        Tests:
        - Node insertion performance
        - Edge insertion performance
        - Transaction overhead
        """
        # Create graph with 10K nodes
        graph = Graph("benchmark-10k", GraphType.DATA)
        
        # Generate 10,000 nodes (simulate real-world entities)
        node_count = 10_000
        edge_count = 30_000  # 3 edges per node average
        
        print(f"   Generating {node_count:,} nodes...")
        start = time.time()
        
        for i in range(node_count):
            node_type = NodeType.TABLE if i % 100 == 0 else NodeType.RECORD
            properties = {
                'index': i,
                'category': f'category_{i % 50}',
                'value': f'value_{i}'
            }
            node = GraphNode(
                id=f"node_{i}",
                label=f"Node {i}",
                type=node_type,
                properties=properties
            )
            graph.add_node(node)
        
        generation_time = time.time() - start
        print(f"   ✅ Generated {node_count:,} nodes in {generation_time:.2f}s")
        print(f"   ✅ Throughput: {node_count / generation_time:,.0f} nodes/sec")
        
        # Generate 30,000 edges (create realistic graph structure)
        print(f"   Generating {edge_count:,} edges...")
        start = time.time()
        
        edges_added = 0
        for i in range(edge_count):
            source_idx = i % node_count
            target_idx = (i + 1) % node_count
            
            edge_type = EdgeType.FOREIGN_KEY if i % 10 == 0 else EdgeType.REFERENCES
            edge = GraphEdge(
                source_id=f"node_{source_idx}",
                target_id=f"node_{target_idx}",
                type=edge_type,
                label=f"edge_{i}",
                properties={'weight': i % 100}
            )
            graph.add_edge(edge)
            edges_added += 1
        
        edge_generation_time = time.time() - start
        print(f"   ✅ Generated {edges_added:,} edges in {edge_generation_time:.2f}s")
        print(f"   ✅ Throughput: {edges_added / edge_generation_time:,.0f} edges/sec")
        
        # Write to database
        print(f"   Writing to database...")
        repo = SqliteGraphCacheRepository(self.db_path)
        
        start = time.time()
        repo.save(graph)
        write_time = time.time() - start
        
        print(f"   ✅ Wrote {node_count:,} nodes + {edges_added:,} edges in {write_time:.2f}s")
        print(f"   ✅ Throughput: {(node_count + edges_added) / write_time:,.0f} ops/sec")
        
        # Store results
        self.results['write_10k'] = {
            'node_count': node_count,
            'edge_count': edges_added,
            'generation_time': generation_time + edge_generation_time,
            'write_time': write_time,
            'total_time': generation_time + edge_generation_time + write_time,
            'throughput_ops_per_sec': (node_count + edges_added) / write_time
        }
    
    def benchmark_read_performance(self) -> None:
        """
        Benchmark: Read 10K nodes + 30K edges from database
        
        Tests:
        - Node retrieval performance
        - Edge retrieval performance
        - Deserialization overhead
        """
        repo = SqliteGraphCacheRepository(self.db_path)
        
        # Single read
        print("   Reading graph from database...")
        start = time.time()
        graph = repo.get("benchmark-10k", GraphType.DATA)
        read_time = time.time() - start
        
        if graph is None:
            print("   ❌ Failed to read graph!")
            return
        
        node_count = len(graph.nodes)
        edge_count = len(graph.edges)
        
        print(f"   ✅ Read {node_count:,} nodes + {edge_count:,} edges in {read_time:.2f}s")
        print(f"   ✅ Throughput: {(node_count + edge_count) / read_time:,.0f} ops/sec")
        
        # Multiple reads (test caching behavior)
        print("   Testing repeated reads (5 iterations)...")
        read_times = []
        
        for i in range(5):
            start = time.time()
            graph = repo.get("benchmark-10k", GraphType.DATA)
            elapsed = time.time() - start
            read_times.append(elapsed)
        
        avg_read = statistics.mean(read_times)
        min_read = min(read_times)
        max_read = max(read_times)
        
        print(f"   ✅ Average: {avg_read:.2f}s | Min: {min_read:.2f}s | Max: {max_read:.2f}s")
        
        # Store results
        self.results['read_10k'] = {
            'node_count': node_count,
            'edge_count': edge_count,
            'single_read_time': read_time,
            'avg_read_time': avg_read,
            'min_read_time': min_read,
            'max_read_time': max_read,
            'throughput_ops_per_sec': (node_count + edge_count) / read_time
        }
    
    def benchmark_query_performance(self) -> None:
        """
        Benchmark: Query operations on 10K graph
        
        Tests:
        - Node lookup by ID
        - Node existence checks
        - Edge traversal
        """
        repo = SqliteGraphCacheRepository(self.db_path)
        graph = repo.get("benchmark-10k", GraphType.DATA)
        
        if graph is None:
            print("   ❌ Graph not found!")
            return
        
        # Test 1: Node lookup by ID
        print("   Testing node lookup (1,000 queries)...")
        lookup_times = []
        
        for i in range(0, 10_000, 10):  # 1,000 lookups
            node_id = f"node_{i}"
            start = time.time()
            node = graph.get_node(node_id)
            elapsed = time.time() - start
            lookup_times.append(elapsed)
            
            if node is None:
                print(f"   ⚠️ Node {node_id} not found!")
        
        avg_lookup = statistics.mean(lookup_times) * 1000  # Convert to ms
        print(f"   ✅ Average lookup: {avg_lookup:.3f}ms")
        print(f"   ✅ Throughput: {1 / statistics.mean(lookup_times):,.0f} lookups/sec")
        
        # Test 2: Node existence checks
        print("   Testing existence checks (1,000 queries)...")
        exists_times = []
        
        for i in range(0, 10_000, 10):  # 1,000 checks
            node_id = f"node_{i}"
            start = time.time()
            exists = graph.has_node(node_id)
            elapsed = time.time() - start
            exists_times.append(elapsed)
        
        avg_exists = statistics.mean(exists_times) * 1000  # Convert to ms
        print(f"   ✅ Average check: {avg_exists:.3f}ms")
        print(f"   ✅ Throughput: {1 / statistics.mean(exists_times):,.0f} checks/sec")
        
        # Store results
        self.results['query_10k'] = {
            'lookup_avg_ms': avg_lookup,
            'lookup_throughput': 1 / statistics.mean(lookup_times),
            'exists_avg_ms': avg_exists,
            'exists_throughput': 1 / statistics.mean(exists_times)
        }
    
    def benchmark_graph_construction(self) -> None:
        """
        Benchmark: In-memory graph construction
        
        Tests:
        - add_node() performance
        - add_edge() performance
        - Validation overhead
        """
        print("   Building graph in memory (10K nodes + 30K edges)...")
        
        graph = Graph("benchmark-memory", GraphType.DATA)
        
        # Add nodes
        start = time.time()
        for i in range(10_000):
            node = GraphNode(
                id=f"mem_node_{i}",
                label=f"Memory Node {i}",
                type=NodeType.RECORD,
                properties={'index': i}
            )
            graph.add_node(node)
        node_time = time.time() - start
        
        print(f"   ✅ Added 10,000 nodes in {node_time:.2f}s")
        print(f"   ✅ Throughput: {10_000 / node_time:,.0f} nodes/sec")
        
        # Add edges
        start = time.time()
        edges_added = 0
        for i in range(30_000):
            source_idx = i % 10_000
            target_idx = (i + 1) % 10_000
            
            edge = GraphEdge(
                source_id=f"mem_node_{source_idx}",
                target_id=f"mem_node_{target_idx}",
                type=EdgeType.REFERENCES,
                label=f"mem_edge_{i}",
                properties={}
            )
            graph.add_edge(edge)
            edges_added += 1
        edge_time = time.time() - start
        
        print(f"   ✅ Added {edges_added:,} edges in {edge_time:.2f}s")
        print(f"   ✅ Throughput: {edges_added / edge_time:,.0f} edges/sec")
        
        # Store results
        self.results['construction'] = {
            'node_time': node_time,
            'edge_time': edge_time,
            'total_time': node_time + edge_time,
            'node_throughput': 10_000 / node_time,
            'edge_throughput': edges_added / edge_time
        }
    
    def benchmark_batch_operations(self) -> None:
        """
        Benchmark: Repeated read/write cycles
        
        Tests:
        - Database I/O overhead
        - Cache effectiveness
        - Consistency under load
        """
        repo = SqliteGraphCacheRepository(self.db_path)
        
        print("   Running 1,000 save/read cycles...")
        save_times = []
        read_times = []
        
        for i in range(1_000):
            # Create small graph (100 nodes)
            graph = Graph(f"batch-{i}", GraphType.DATA)
            for j in range(100):
                node = GraphNode(
                    id=f"batch_{i}_node_{j}",
                    label=f"Batch {i} Node {j}",
                    type=NodeType.RECORD,
                    properties={}
                )
                graph.add_node(node)
            
            # Save
            start = time.time()
            repo.save(graph)
            save_time = time.time() - start
            save_times.append(save_time)
            
            # Read
            start = time.time()
            loaded_graph = repo.get(f"batch-{i}", GraphType.DATA)
            read_time = time.time() - start
            read_times.append(read_time)
            
            if loaded_graph is None or len(loaded_graph.nodes) != 100:
                print(f"   ⚠️ Iteration {i}: Consistency issue!")
        
        avg_save = statistics.mean(save_times) * 1000  # ms
        avg_read = statistics.mean(read_times) * 1000  # ms
        
        print(f"   ✅ Average save (100 nodes): {avg_save:.2f}ms")
        print(f"   ✅ Average read (100 nodes): {avg_read:.2f}ms")
        print(f"   ✅ Total cycle time: {(avg_save + avg_read):.2f}ms")
        
        # Store results
        self.results['batch_ops'] = {
            'iterations': 1_000,
            'nodes_per_iteration': 100,
            'avg_save_ms': avg_save,
            'avg_read_ms': avg_read,
            'total_cycle_ms': avg_save + avg_read
        }
    
    def print_summary(self) -> None:
        """Print comprehensive summary with recommendations"""
        print("=" * 80)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 80)
        print()
        
        # Write Performance
        write_data = self.results.get('write_10k', {})
        print(f"🔸 Write Performance (10K nodes + 30K edges):")
        print(f"   Total Time: {write_data.get('total_time', 0):.2f}s")
        print(f"   Throughput: {write_data.get('throughput_ops_per_sec', 0):,.0f} ops/sec")
        print()
        
        # Read Performance
        read_data = self.results.get('read_10k', {})
        print(f"🔸 Read Performance (10K nodes + 30K edges):")
        print(f"   Single Read: {read_data.get('single_read_time', 0):.2f}s")
        print(f"   Average Read: {read_data.get('avg_read_time', 0):.2f}s")
        print(f"   Throughput: {read_data.get('throughput_ops_per_sec', 0):,.0f} ops/sec")
        print()
        
        # Query Performance
        query_data = self.results.get('query_10k', {})
        print(f"🔸 Query Performance:")
        print(f"   Node Lookup: {query_data.get('lookup_avg_ms', 0):.3f}ms")
        print(f"   Exists Check: {query_data.get('exists_avg_ms', 0):.3f}ms")
        print()
        
        # Construction Performance
        const_data = self.results.get('construction', {})
        print(f"🔸 In-Memory Construction:")
        print(f"   Node Addition: {const_data.get('node_throughput', 0):,.0f} nodes/sec")
        print(f"   Edge Addition: {const_data.get('edge_throughput', 0):,.0f} edges/sec")
        print()
        
        # Batch Operations
        batch_data = self.results.get('batch_ops', {})
        print(f"🔸 Batch Operations (1K iterations):")
        print(f"   Save (100 nodes): {batch_data.get('avg_save_ms', 0):.2f}ms")
        print(f"   Read (100 nodes): {batch_data.get('avg_read_ms', 0):.2f}ms")
        print()
        
        # Bottleneck Analysis
        print("=" * 80)
        print("🔍 BOTTLENECK ANALYSIS")
        print("=" * 80)
        print()
        
        self.analyze_bottlenecks()
        
        # Recommendations
        print()
        print("=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        print()
        
        self.generate_recommendations()
    
    def analyze_bottlenecks(self) -> None:
        """Identify performance bottlenecks"""
        write_data = self.results.get('write_10k', {})
        read_data = self.results.get('read_10k', {})
        query_data = self.results.get('query_10k', {})
        
        total_write = write_data.get('total_time', 0)
        total_read = read_data.get('single_read_time', 0)
        
        print("📊 Operation Breakdown:")
        print()
        
        # Write operations
        if total_write > 5.0:
            print(f"   ⚠️ SLOW WRITE: {total_write:.2f}s for 40K operations")
            print(f"      Likely cause: Transaction overhead, index updates")
        else:
            print(f"   ✅ FAST WRITE: {total_write:.2f}s for 40K operations")
        
        # Read operations
        if total_read > 2.0:
            print(f"   ⚠️ SLOW READ: {total_read:.2f}s for 40K operations")
            print(f"      Likely cause: Deserialization overhead, JSON parsing")
        else:
            print(f"   ✅ FAST READ: {total_read:.2f}s for 40K operations")
        
        # Query operations
        lookup_ms = query_data.get('lookup_avg_ms', 0)
        if lookup_ms > 0.1:
            print(f"   ⚠️ SLOW LOOKUP: {lookup_ms:.3f}ms per query")
            print(f"      Likely cause: Dict lookup in large collection")
        else:
            print(f"   ✅ FAST LOOKUP: {lookup_ms:.3f}ms per query")
        
        print()
        
        # Check database size
        db_file = Path(self.db_path)
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            print(f"📦 Database Size: {size_mb:.2f} MB")
            
            if size_mb > 100:
                print(f"   ⚠️ LARGE DATABASE: Consider compression or partitioning")
            else:
                print(f"   ✅ Reasonable size for 40K operations")
    
    def generate_recommendations(self) -> None:
        """Generate actionable recommendations"""
        write_data = self.results.get('write_10k', {})
        read_data = self.results.get('read_10k', {})
        query_data = self.results.get('query_10k', {})
        batch_data = self.results.get('batch_ops', {})
        
        recommendations = []
        
        # Recommendation 1: Connection Pooling
        write_throughput = write_data.get('throughput_ops_per_sec', 0)
        if write_throughput < 5000:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Implement Connection Pooling',
                'reason': f'Current throughput: {write_throughput:,.0f} ops/sec',
                'benefit': 'Expected 5-10% improvement for concurrent access',
                'effort': '2-3 hours',
                'task': 'HIGH-13'
            })
        
        # Recommendation 2: Batch Inserts
        batch_save_ms = batch_data.get('avg_save_ms', 0)
        if batch_save_ms > 50:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Use Batch Inserts (executemany)',
                'reason': f'Small graphs take {batch_save_ms:.2f}ms',
                'benefit': 'Expected 50-70% improvement for bulk operations',
                'effort': '1-2 hours',
                'task': 'NEW'
            })
        
        # Recommendation 3: Index Optimization
        lookup_ms = query_data.get('lookup_avg_ms', 0)
        if lookup_ms > 0.05:
            recommendations.append({
                'priority': 'LOW',
                'title': 'Add Composite Indexes',
                'reason': f'Lookups average {lookup_ms:.3f}ms',
                'benefit': 'Expected 20-30% improvement for complex queries',
                'effort': '1 hour',
                'task': 'NEW'
            })
        
        # Recommendation 4: JSON Optimization
        read_time = read_data.get('single_read_time', 0)
        if read_time > 2.0:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Optimize JSON Deserialization',
                'reason': f'Read operations take {read_time:.2f}s',
                'benefit': 'Expected 10-15% improvement',
                'effort': '2-3 hours',
                'task': 'NEW'
            })
        
        # Print recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority']}] {rec['title']}")
                print(f"   Reason: {rec['reason']}")
                print(f"   Benefit: {rec['benefit']}")
                print(f"   Effort: {rec['effort']}")
                print(f"   Task ID: {rec['task']}")
                print()
        else:
            print("✅ No performance issues detected!")
            print("   Knowledge Graph handles 10K+ nodes efficiently.")
            print()
    
    def check_database_health(self) -> None:
        """Check database integrity and performance"""
        print("🔍 Database Health Check:")
        print()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check table sizes
            cursor.execute("SELECT COUNT(*) FROM graph_nodes")
            node_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM graph_edges")
            edge_count = cursor.fetchone()[0]
            
            print(f"   📊 Stored Nodes: {node_count:,}")
            print(f"   📊 Stored Edges: {edge_count:,}")
            print()
            
            # Check index usage
            cursor.execute("PRAGMA index_list('graph_nodes')")
            node_indexes = cursor.fetchall()
            print(f"   🔍 Node Indexes: {len(node_indexes)}")
            
            cursor.execute("PRAGMA index_list('graph_edges')")
            edge_indexes = cursor.fetchall()
            print(f"   🔍 Edge Indexes: {len(edge_indexes)}")
            print()
            
            # Database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            if integrity == 'ok':
                print("   ✅ Database integrity: OK")
            else:
                print(f"   ⚠️ Integrity issue: {integrity}")
            
        finally:
            conn.close()


def main():
    """Run benchmark suite"""
    benchmark = PerformanceBenchmark()
    
    try:
        # Run all benchmarks
        results = benchmark.run_all_benchmarks()
        
        # Health check
        print()
        benchmark.check_database_health()
        
        # Success
        print()
        print("=" * 80)
        print("✅ BENCHMARK COMPLETE")
        print("=" * 80)
        print()
        print(f"📁 Results stored in: {benchmark.db_path}")
        print(f"📊 Benchmark data: {len(results)} test suites")
        print()
        print("Next Steps:")
        print("   1. Review recommendations above")
        print("   2. Implement HIGH-13 (Connection Pooling) for 5-10% improvement")
        print("   3. Consider batch insert optimization for bulk operations")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())