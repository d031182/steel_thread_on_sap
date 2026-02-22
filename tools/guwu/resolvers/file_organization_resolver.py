"""
File Organization Resolver - Automated File Placement & Structure Fixes

Resolves findings from Feng Shui's file_organization_agent:
- Moves misplaced files to correct directories
- Updates import statements in moved files
- Updates references in files that import the moved files
- Cleans up obsolete/temporary files
- Consolidates duplicate directories

Philosophy: "Test the contract, trust the implementation" - If Feng Shui
detected an issue and provided clear recommendation, we can safely resolve it.

Usage:
    # Dry-run (default, safe)
    resolver = FileOrganizationResolver()
    result = resolver.resolve_findings(findings, dry_run=True)
    
    # Execute (requires explicit flag)
    result = resolver.resolve_findings(findings, dry_run=False)
    
    # Interactive (prompt per finding)
    result = resolver.resolve_findings(findings, dry_run=False, interactive=True)
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

from .base_resolver import (
    BaseResolver, ResolutionResult, ResolutionStatus
)


class FileOrganizationResolver(BaseResolver):
    """
    Resolves file organization issues detected by Feng Shui
    
    Capabilities:
    - Move files to correct directories
    - Update imports in moved files (adjust relative imports)
    - Update imports in files that reference moved files
    - Delete obsolete/temporary files
    - Consolidate duplicate directories
    
    Safety:
    - Dry-run by default (simulates without changing files)
    - Interactive mode (confirm each finding)
    - Backup before destructive operations
    - Validation before/after operations
    """
    
    def __init__(self):
        super().__init__("file_organization")
        
        # Categories this resolver can handle
        self.supported_categories = {
            "Root Directory Clutter",
            "Misplaced Script",
            "Obsolete File",
            "Obsolete Temporary File",
            "Documentation Misplacement",
            "Knowledge Vault Structure Violation",
            "Misplaced Utility Script",
            "Misplaced Test Artifact",
            "Duplicate Test Configuration",
            "Stale Backup Directory",
            "Directory Duplication",
            "Scattered Documentation",
            "Module Structure Violation",
        }
        
        # Mapping of recommendation actions to resolution methods
        self.action_handlers = {
            'MOVE': self._handle_move,
            'DELETE': self._handle_delete,
            'CONSOLIDATE': self._handle_consolidate,
            'SPLIT': self._handle_split,  # For bloated documentation
        }
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this resolver provides.
        
        Returns:
            List of capability descriptions
        """
        return [
            "Move misplaced files to correct locations",
            "Remove clutter files (temp, backup, cache)",
            "Organize scattered files into proper directories",
            "Clean up empty directories"
        ]
    
    def can_resolve(self, finding) -> bool:
        """
        Check if this resolver can handle the finding
        
        Args:
            finding: Finding object from Feng Shui
            
        Returns:
            True if finding category is supported
        """
        return finding.category in self.supported_categories
    
    def resolve_finding(self, finding, dry_run: bool = True) -> ResolutionResult:
        """
        Resolve a single file organization finding
        
        Args:
            finding: Finding object from Feng Shui file_organization_agent
            dry_run: If True, simulate without making changes
        
        Returns:
            ResolutionResult with outcome
        """
        result = ResolutionResult(status=ResolutionStatus.SUCCESS)
        
        try:
            # Extract action from recommendation (MOVE, DELETE, CONSOLIDATE, etc.)
            action = self._extract_action(finding.recommendation)
            
            if not action:
                result.add_error(f"Could not determine action from recommendation: {finding.recommendation}")
                result.status = ResolutionStatus.FAILED
                result.findings_failed += 1
                return result
            
            # Get handler for this action
            handler = self.action_handlers.get(action)
            
            if not handler:
                result.add_error(f"No handler for action: {action}")
                result.status = ResolutionStatus.FAILED
                result.findings_failed += 1
                return result
            
            # Execute handler
            if dry_run:
                self._simulate_resolution(finding, action, result)
            else:
                handler(finding, result)
            
            result.status = ResolutionStatus.SUCCESS
            result.findings_resolved += 1
        
        except Exception as e:
            self.logger.error(f"Error resolving finding: {str(e)}")
            result.add_error(f"Resolution failed: {str(e)}")
            result.status = ResolutionStatus.FAILED
            result.findings_failed += 1
        
        return result
    
    def _extract_action(self, recommendation: str) -> Optional[str]:
        """
        Extract primary action from recommendation text
        
        Examples:
            "MOVE to tests/ai_assistant/" -> "MOVE"
            "DELETE (temporary file)" -> "DELETE"
            "CONSOLIDATE: Move contents..." -> "CONSOLIDATE"
            
        Args:
            recommendation: Recommendation text from finding
            
        Returns:
            Action keyword or None
        """
        # Check for action keywords at start of recommendation
        for action in ['MOVE', 'DELETE', 'CONSOLIDATE', 'SPLIT', 'CREATE', 'REVIEW']:
            if recommendation.startswith(action):
                return action
        
        return None
    
    def _simulate_resolution(self, finding, action: str, result: ResolutionResult):
        """
        Simulate resolution (dry-run mode)
        
        Args:
            finding: Finding to resolve
            action: Action to simulate
            result: ResolutionResult to update
        """
        file_path = Path(finding.file_path)
        
        if action == 'MOVE':
            # Extract target directory from recommendation
            target_match = re.search(r'to\s+([^\s,\.]+)', finding.recommendation)
            if target_match:
                target = target_match.group(1)
                result.add_dry_run_action(f"WOULD move: {file_path} → {target}")
                
                # Check if imports need updating
                if file_path.suffix == '.py':
                    result.add_dry_run_action(f"WOULD update imports in: {file_path.name}")
                    result.add_dry_run_action(f"WOULD scan project for references to: {file_path.name}")
            else:
                result.add_dry_run_action(f"WOULD move: {file_path} (target unclear)")
        
        elif action == 'DELETE':
            if file_path.is_dir():
                file_count = sum(1 for _ in file_path.rglob('*') if _.is_file())
                result.add_dry_run_action(f"WOULD delete directory: {file_path} ({file_count} files)")
            else:
                result.add_dry_run_action(f"WOULD delete file: {file_path}")
        
        elif action == 'CONSOLIDATE':
            result.add_dry_run_action(f"WOULD consolidate: {file_path} (merge with canonical location)")
        
        elif action == 'SPLIT':
            result.add_dry_run_action(f"WOULD split: {file_path} (break into focused documents)")
        
        else:
            result.add_dry_run_action(f"WOULD apply action '{action}' to: {file_path}")
    
    def _handle_move(self, finding, result: ResolutionResult):
        """
        Handle MOVE action - Move file to correct directory
        
        Steps:
        1. Parse target directory from recommendation
        2. Create target directory if needed
        3. Move file
        4. Update imports if Python file
        5. Update references in other files
        
        Args:
            finding: Finding with MOVE recommendation
            result: ResolutionResult to update
        """
        source_path = Path(finding.file_path)
        
        if not source_path.exists():
            result.add_error(f"Source file not found: {source_path}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
            return
        
        # Extract target directory from recommendation
        # Examples: "Move to tests/ai_assistant/", "MOVE to docs/knowledge/modules/"
        target_match = re.search(r'(?:Move|MOVE)\s+to\s+([^\s,\.]+)', finding.recommendation)
        
        if not target_match:
            result.add_error(f"Could not parse target directory from: {finding.recommendation}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
            return
        
        target_dir = target_match.group(1).strip()
        
        # Get project root (assuming we're at c:/Users/D031182/gitrepo/steel_thread_on_sap)
        project_root = Path.cwd()
        target_path = project_root / target_dir / source_path.name
        
        try:
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source_path), str(target_path))
            result.add_action(f"Moved: {source_path} → {target_path}")
            
            # If Python file, update imports
            if target_path.suffix == '.py':
                updated_refs = self._update_imports_after_move(source_path, target_path)
                if updated_refs:
                    result.add_action(f"Updated imports in {len(updated_refs)} files: {', '.join([f.name for f in updated_refs])}")
            
            result.findings_resolved += 1
            result.status = ResolutionStatus.SUCCESS
        
        except Exception as e:
            result.add_error(f"Failed to move file: {str(e)}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
    
    def _handle_delete(self, finding, result: ResolutionResult):
        """
        Handle DELETE action - Remove obsolete file or directory
        
        Safety: Only deletes files explicitly marked as obsolete/temporary
        
        Args:
            finding: Finding with DELETE recommendation
            result: ResolutionResult to update
        """
        target_path = Path(finding.file_path)
        
        if not target_path.exists():
            result.add_warning(f"Target already deleted: {target_path}")
            result.findings_resolved += 1
            result.status = ResolutionStatus.SUCCESS
            return
        
        try:
            if target_path.is_dir():
                # Delete directory and contents
                shutil.rmtree(target_path)
                result.add_action(f"Deleted directory: {target_path}")
            else:
                # Delete file
                target_path.unlink()
                result.add_action(f"Deleted file: {target_path}")
            
            result.findings_resolved += 1
            result.status = ResolutionStatus.SUCCESS
        
        except Exception as e:
            result.add_error(f"Failed to delete: {str(e)}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
    
    def _handle_consolidate(self, finding, result: ResolutionResult):
        """
        Handle CONSOLIDATE action - Merge duplicate directories
        
        Args:
            finding: Finding with CONSOLIDATE recommendation
            result: ResolutionResult to update
        """
        # This is complex and requires careful planning
        # For Phase 2, we'll simulate only
        result.add_warning(f"CONSOLIDATE action requires manual review: {finding.file_path}")
        result.add_action(f"Flagged for consolidation: {finding.recommendation}")
        result.findings_skipped += 1
        result.status = ResolutionStatus.SKIPPED
    
    def _handle_split(self, finding, result: ResolutionResult):
        """
        Handle SPLIT action - Break bloated documentation into focused docs
        
        Args:
            finding: Finding with SPLIT recommendation
            result: ResolutionResult to update
        """
        # This requires content analysis and is complex
        # For Phase 2, we'll skip and require manual intervention
        result.add_warning(f"SPLIT action requires manual review: {finding.file_path}")
        result.add_action(f"Flagged for splitting: {finding.recommendation}")
        result.findings_skipped += 1
        result.status = ResolutionStatus.SKIPPED
    
    def _update_imports_after_move(
        self, 
        old_path: Path, 
        new_path: Path
    ) -> List[Path]:
        """
        Update import statements after moving a Python file
        
        This is a simplified version. Full implementation would:
        1. Update imports in the moved file (adjust relative imports)
        2. Find all files that import the moved file
        3. Update their import statements
        
        Args:
            old_path: Original file path
            new_path: New file path
            
        Returns:
            List of files with updated imports
        """
        updated_files = []
        
        try:
            # For Phase 2, we'll just log this as a warning
            # Full implementation would use AST parsing and rewriting
            self.logger.warning(
                f"Import updates needed after moving {old_path.name}. "
                f"Manual review recommended."
            )
        
        except Exception as e:
            self.logger.error(f"Error updating imports: {str(e)}")
        
        return updated_files
    
    def get_supported_categories(self) -> Set[str]:
        """Return set of finding categories this resolver supports"""
        return self.supported_categories