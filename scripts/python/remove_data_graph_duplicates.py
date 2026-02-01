"""
Remove duplicate methods from DataGraphService that are inherited from GraphBuilderBase

Phase 3 of WP-KG-002: Final DRY cleanup
"""

def remove_duplicates():
    filepath = 'modules/knowledge_graph/backend/data_graph_service.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove _discover_fk_mappings method (starts around line 303)
    start_marker = '    def _discover_fk_mappings(self, tables: List[Dict[str, str]]) -> Dict[str, List[Tuple[str, str]]]:'
    end_marker = '    def _find_fk_relationships('
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx + 1)
    
    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find _discover_fk_mappings method boundaries")
        return False
    
    # Extract the method (for logging)
    method1 = content[start_idx:end_idx]
    lines_removed_1 = method1.count('\n')
    
    # Remove the method, add comment
    comment = '    # NOTE: _discover_fk_mappings() inherited from GraphBuilderBase\n    \n'
    content = content[:start_idx] + comment + content[end_idx:]
    
    print(f"[OK] Removed _discover_fk_mappings (~{lines_removed_1} lines)")
    
    # Find and remove _infer_fk_target_table method
    start_marker2 = '    def _infer_fk_target_table(self, column_name: str, source_table: str) -> str:'
    end_marker2 = '    def build_data_graph('
    
    start_idx2 = content.find(start_marker2)
    end_idx2 = content.find(end_marker2, start_idx2 + 1)
    
    if start_idx2 == -1 or end_idx2 == -1:
        print("ERROR: Could not find _infer_fk_target_table method boundaries")
        return False
    
    # Extract the method (for logging)
    method2 = content[start_idx2:end_idx2]
    lines_removed_2 = method2.count('\n')
    
    # Remove the method, add comment
    comment2 = '    # NOTE: _infer_fk_target_table() inherited from GraphBuilderBase\n    \n'
    content = content[:start_idx2] + comment2 + content[end_idx2:]
    
    print(f"[OK] Removed _infer_fk_target_table (~{lines_removed_2} lines)")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    total_removed = lines_removed_1 + lines_removed_2
    print(f"\n[COMPLETE] Phase 3 Done!")
    print(f"   Removed {total_removed} duplicate lines from DataGraphService")
    print(f"   Both methods now inherited from GraphBuilderBase")
    
    return True

if __name__ == '__main__':
    success = remove_duplicates()
    exit(0 if success else 1)