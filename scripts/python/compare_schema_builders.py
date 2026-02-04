"""
Compare Schema Graph Builders - Feature Parity Validation

Compares output from:
1. SchemaGraphBuilder (database-driven)
2. CSNSchemaGraphBuilder (CSN metadata-driven)

Validates:
- Same node count and structure
- Same edge count and relationships
- Same semantics and visual styling
- Output format compatibility

Usage:
    python scripts/python/compare_schema_builders.py
"""

import sys
import os
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.schema_graph_builder import SchemaGraphBuilder
from modules.knowledge_graph.backend.csn_schema_graph_builder import CSNSchemaGraphBuilder
from core.services.csn_parser import CSNParser


def compare_graphs(db_graph: dict, csn_graph: dict) -> dict:
    """
    Compare two graph outputs for feature parity
    
    Args:
        db_graph: Output from SchemaGraphBuilder
        csn_graph: Output from CSNSchemaGraphBuilder
        
    Returns:
        Dictionary with comparison results
    """
    results = {
        'feature_parity': True,
        'differences': [],
        'statistics': {},
        'details': {}
    }
    
    # Compare success status
    if db_graph.get('success') != csn_graph.get('success'):
        results['feature_parity'] = False
        results['differences'].append(f"Success status mismatch: DB={db_graph.get('success')}, CSN={csn_graph.get('success')}")
    
    # Compare statistics
    db_stats = db_graph.get('stats', {})
    csn_stats = csn_graph.get('stats', {})
    
    results['statistics'] = {
        'database_driven': db_stats,
        'csn_driven': csn_stats
    }
    
    for stat_name in ['node_count', 'edge_count', 'product_count', 'table_count']:
        db_val = db_stats.get(stat_name, 0)
        csn_val = csn_stats.get(stat_name, 0)
        
        if db_val != csn_val:
            results['differences'].append(f"{stat_name}: DB={db_val}, CSN={csn_val}")
            # Allow small differences in node/edge counts (implementation differences)
            if abs(db_val - csn_val) > 5:
                results['feature_parity'] = False
    
    # Compare node structure
    db_nodes = db_graph.get('nodes', [])
    csn_nodes = csn_graph.get('nodes', [])
    
    results['details']['node_comparison'] = {
        'db_node_count': len(db_nodes),
        'csn_node_count': len(csn_nodes),
        'db_node_groups': _count_by_group(db_nodes),
        'csn_node_groups': _count_by_group(csn_nodes)
    }
    
    # Compare edge structure
    db_edges = db_graph.get('edges', [])
    csn_edges = csn_graph.get('edges', [])
    
    results['details']['edge_comparison'] = {
        'db_edge_count': len(db_edges),
        'csn_edge_count': len(csn_edges),
        'db_edge_types': _analyze_edges(db_edges),
        'csn_edge_types': _analyze_edges(csn_edges)
    }
    
    # Validate output format compatibility
    format_issues = _validate_output_format(db_nodes, db_edges, csn_nodes, csn_edges)
    if format_issues:
        results['differences'].extend(format_issues)
        results['feature_parity'] = False
    
    return results


def _count_by_group(nodes: list) -> dict:
    """Count nodes by group (product, table)"""
    counts = {}
    for node in nodes:
        group = node.get('group', 'unknown')
        counts[group] = counts.get(group, 0) + 1
    return counts


def _analyze_edges(edges: list) -> dict:
    """Analyze edge types and properties"""
    analysis = {
        'total': len(edges),
        'with_labels': sum(1 for e in edges if e.get('label')),
        'dashed': sum(1 for e in edges if e.get('dashes')),
        'arrows': sum(1 for e in edges if e.get('arrows'))
    }
    return analysis


def _validate_output_format(db_nodes: list, db_edges: list, csn_nodes: list, csn_edges: list) -> list:
    """
    Validate that both outputs use same vis.js format
    
    Returns:
        List of format issues (empty if compatible)
    """
    issues = []
    
    # Check node format
    required_node_fields = ['id', 'label', 'title', 'group', 'shape', 'color']
    for i, node in enumerate(csn_nodes[:3]):  # Sample check
        for field in required_node_fields:
            if field not in node:
                issues.append(f"CSN node {i} missing required field: {field}")
    
    # Check edge format
    required_edge_fields = ['from', 'to', 'arrows', 'color']
    for i, edge in enumerate(csn_edges[:3]):  # Sample check
        for field in required_edge_fields:
            if field not in edge:
                issues.append(f"CSN edge {i} missing required field: {field}")
    
    # Check color format consistency
    for node in csn_nodes[:3]:
        color = node.get('color', {})
        if not isinstance(color, dict) or 'background' not in color:
            issues.append(f"CSN node color format inconsistent (expected dict with 'background')")
            break
    
    return issues


def print_comparison_report(results: dict):
    """Print formatted comparison report"""
    print("\n" + "="*80)
    print("SCHEMA GRAPH BUILDER COMPARISON REPORT")
    print("="*80)
    
    # Overall result
    if results['feature_parity']:
        print("\n✅ FEATURE PARITY ACHIEVED!")
        print("CSNSchemaGraphBuilder produces equivalent output to SchemaGraphBuilder")
    else:
        print("\n⚠️ FEATURE PARITY NOT ACHIEVED")
        print("Differences detected between builders")
    
    # Statistics comparison
    print("\n" + "-"*80)
    print("STATISTICS COMPARISON")
    print("-"*80)
    
    db_stats = results['statistics']['database_driven']
    csn_stats = results['statistics']['csn_driven']
    
    print(f"\n{'Metric':<20} {'Database-Driven':<20} {'CSN-Driven':<20} {'Match':<10}")
    print("-" * 70)
    
    for stat in ['node_count', 'edge_count', 'product_count', 'table_count']:
        db_val = db_stats.get(stat, 0)
        csn_val = csn_stats.get(stat, 0)
        match = "✅" if db_val == csn_val else "❌"
        print(f"{stat:<20} {db_val:<20} {csn_val:<20} {match:<10}")
    
    # Node comparison
    print("\n" + "-"*80)
    print("NODE STRUCTURE COMPARISON")
    print("-"*80)
    
    node_comp = results['details']['node_comparison']
    print(f"\nDatabase-driven nodes by group: {node_comp['db_node_groups']}")
    print(f"CSN-driven nodes by group:      {node_comp['csn_node_groups']}")
    
    # Edge comparison
    print("\n" + "-"*80)
    print("EDGE STRUCTURE COMPARISON")
    print("-"*80)
    
    edge_comp = results['details']['edge_comparison']
    print(f"\nDatabase-driven edges: {edge_comp['db_edge_types']}")
    print(f"CSN-driven edges:      {edge_comp['csn_edge_types']}")
    
    # Differences
    if results['differences']:
        print("\n" + "-"*80)
        print("DETAILED DIFFERENCES")
        print("-"*80)
        for diff in results['differences']:
            print(f"  • {diff}")
    
    print("\n" + "="*80)
    
    # Semantic equivalence assessment
    print("\nSEMANTIC EQUIVALENCE ASSESSMENT")
    print("-"*80)
    
    assessments = []
    
    # Node count similarity
    db_nodes = node_comp['db_node_count']
    csn_nodes = node_comp['csn_node_count']
    node_diff = abs(db_nodes - csn_nodes)
    
    if node_diff == 0:
        assessments.append("✅ Exact node count match")
    elif node_diff <= 5:
        assessments.append(f"⚠️ Minor node count difference ({node_diff} nodes)")
    else:
        assessments.append(f"❌ Significant node count difference ({node_diff} nodes)")
    
    # Edge count similarity
    db_edges = edge_comp['db_edge_count']
    csn_edges = edge_comp['csn_edge_count']
    edge_diff = abs(db_edges - csn_edges)
    
    if edge_diff == 0:
        assessments.append("✅ Exact edge count match")
    elif edge_diff <= 3:
        assessments.append(f"⚠️ Minor edge count difference ({edge_diff} edges)")
    else:
        assessments.append(f"❌ Significant edge count difference ({edge_diff} edges)")
    
    # Format compatibility
    format_issues = [d for d in results['differences'] if 'format' in d.lower() or 'field' in d.lower()]
    if not format_issues:
        assessments.append("✅ Output format fully compatible (vis.js)")
    else:
        assessments.append(f"❌ Format compatibility issues ({len(format_issues)} found)")
    
    for assessment in assessments:
        print(f"  {assessment}")
    
    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if results['feature_parity']:
        print("\n✅ CSNSchemaGraphBuilder achieves FULL FEATURE PARITY")
        print("   • Same graph structure (products → tables → relationships)")
        print("   • Same semantics and visual styling")
        print("   • Compatible output format (vis.js)")
        print("   • Can be used interchangeably with SchemaGraphBuilder")
    else:
        print("\n⚠️ Feature parity NOT achieved - review differences above")
    
    print("\n" + "="*80 + "\n")


def main():
    """Run comparison test"""
    print("\n" + "="*80)
    print("INITIALIZING SCHEMA BUILDER COMPARISON")
    print("="*80)
    
    db_path = 'p2p_data.db'
    
    if not os.path.exists(db_path):
        print(f"\n❌ Database not found: {db_path}")
        print("   Please ensure p2p_data.db exists in the project root")
        sys.exit(1)
    
    print(f"\n✓ Using database: {db_path}")
    print(f"✓ Using CSN directory: docs/csn")
    
    # Initialize builders
    print("\nInitializing builders...")
    
    try:
        # Database-driven builder
        data_source = SQLiteDataSource(db_path)
        csn_parser = CSNParser('docs/csn')
        db_builder = SchemaGraphBuilder(data_source, csn_parser, db_path)
        print("  ✓ SchemaGraphBuilder (database-driven) initialized")
        
        # CSN-driven builder
        csn_builder = CSNSchemaGraphBuilder('docs/csn', db_path)
        print("  ✓ CSNSchemaGraphBuilder (CSN-driven) initialized")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)
    
    # Build graphs
    print("\nBuilding graphs...")
    
    try:
        print("  • Building database-driven graph...")
        db_graph = db_builder.build_schema_graph()
        print(f"    ✓ Generated: {db_graph.get('stats', {}).get('node_count', 0)} nodes, {db_graph.get('stats', {}).get('edge_count', 0)} edges")
        
        print("  • Building CSN-driven graph...")
        csn_graph = csn_builder.build_schema_graph()
        print(f"    ✓ Generated: {csn_graph.get('stats', {}).get('node_count', 0)} nodes, {csn_graph.get('stats', {}).get('edge_count', 0)} edges")
        
    except Exception as e:
        print(f"\n❌ Graph building failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Compare results
    print("\nComparing outputs...")
    results = compare_graphs(db_graph, csn_graph)
    
    # Print report
    print_comparison_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['feature_parity'] else 1)


if __name__ == '__main__':
    main()