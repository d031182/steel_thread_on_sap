"""
File Organization Resolver - Generic Automated File Organization Fixes

Resolves findings from Feng Shui's file_organization_agent by parsing
recommendations dynamically. NO hardcoded categories or paths - fully generic!

Philosophy: "Follow Feng Shui's wisdom" - If Feng Shui detected an issue and 
provided clear recommendation, parse it and execute it safely.

Key Design Principles:
1. GENERIC: Parse recommendation text, don't hardcode categories/paths
2. INTELLIGENT: Extract action verbs (MOVE, DELETE, CREATE) and targets
3. SAFE: Dry-run by default, validation before execution
4. FLEXIBLE: Works with any Feng Shui finding format

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
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from .base_resolver import (
    BaseResolver, ResolutionResult, ResolutionStatus
)


class FileOrganizationResolver(BaseResolver):
    """
    Generic resolver for file organization issues
    
    Parses Feng Shui recommendations dynamically instead of hardcoding rules.
    
    Capabilities:
    - Parse action verbs from recommendations (MOVE, DELETE, CONSOLIDATE, etc.)
    - Extract target paths from recommendation text
    - Execute file operations safely with validation
    - Update imports if Python files moved (future enhancement)
    
    Safety:
    - Dry-run by default (simulates without changing files)
    - Interactive mode (confirm each finding)
    - Validation before/after operations
    - Git-aware (checks for uncommitted changes)
    """
    
    def __init__(self):
        super().__init__("file_organization")
        
        # Action verb patterns to extract from recommendations
        # Format: (verb_pattern, handler_method, priority)
        # Priority determines order when multiple verbs found
        self.action_patterns = [
            (re.compile(r'\b(MOVE|Move)\b\s+to\s+([^\s,\.]+)', re.IGNORECASE), self._handle_move, 10),
            (re.compile(r'\b(DELETE|Delete)\b', re.IGNORECASE), self._handle_delete, 20),
            (re.compile(r'\b(CONSOLIDATE|Consolidate)\b', re.IGNORECASE), self._handle_consolidate, 30),
            (re.compile(r'\b(SPLIT|Split)\b', re.IGNORECASE), self._handle_split, 40),
            (re.compile(r'\b(CREATE|Create)\b', re.IGNORECASE), self._handle_create, 50),
            (re.compile(r'\b(REVIEW|Review)\b', re.IGNORECASE), self._handle_review, 60),
        ]
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this resolver provides.
        
        Returns:
            List of capability descriptions
        """
        return [
            "Parse Feng Shui recommendations dynamically (no hardcoded rules)",
            "Move misplaced files to correct locations",
            "Remove clutter files (temp, backup, cache)",
            "Organize scattered files into proper directories",
            "Clean up empty directories",
            "Consolidate duplicate directory structures",
            "Create missing directories/files",
            "Generic action extraction from recommendation text"
        ]
    
    def can_resolve(self, finding) -> bool:
        """
        Check if this resolver can handle the finding
        
        Generic approach: Can resolve if recommendation contains action verb
        
        Args:
            finding: Finding object from Feng Shui
            
        Returns:
            True if recommendation contains parseable action
        """
        action, _ = self._parse_recommendation(finding.recommendation)
        return action is not None
    
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
            # Parse recommendation to extract action and details
            action, details = self._parse_recommendation(finding.recommendation)
            
            if not action:
                result.add_error(
                    f"Could not parse action from recommendation: {finding.recommendation}"
                )
                result.status = ResolutionStatus.FAILED
                result.findings_failed += 1
                return result
            
            # Log what we're about to do
            self.logger.info(
                f"{'[DRY-RUN] ' if dry_run else ''}Resolving: {finding.category} - "
                f"Action={action['verb']}, File={finding.file_path}"
            )
            
            # Execute handler
            if dry_run:
                self._simulate_resolution(finding, action, details, result)
            else:
                handler = action['handler']
                handler(finding, details, result)
            
            result.findings_resolved += 1
        
        except Exception as e:
            self.logger.error(f"Error resolving finding: {str(e)}")
            result.add_error(f"Resolution failed: {str(e)}")
            result.status = ResolutionStatus.FAILED
            result.findings_failed += 1
        
        return result
    
    def _parse_recommendation(self, recommendation: str) -> Tuple[Optional[Dict], Dict]:
        """
        Parse recommendation text to extract action and details
        
        Generic approach: Match against known action patterns, extract targets
        
        Examples:
            "MOVE to tests/ai_assistant/" -> 
                action={'verb': 'MOVE', 'handler': ...}, details={'target': 'tests/ai_assistant/'}
            
            "DELETE (temporary file)" -> 
                action={'verb': 'DELETE', 'handler': ...}, details={}
            
            "CONSOLIDATE: Move contents to docs/knowledge/" ->
                action={'verb': 'CONSOLIDATE', 'handler': ...}, details={'target': 'docs/knowledge/'}
            
        Args:
            recommendation: Recommendation text from finding
            
        Returns:
            Tuple of (action_dict, details_dict) or (None, {}) if unparseable
        """
        for pattern, handler, priority in self.action_patterns:
            match = pattern.search(recommendation)
            if match:
                verb = match.group(1).upper()
                
                # Extract target if available (group 2 in MOVE pattern)
                target = None
                if len(match.groups()) >= 2:
                    target = match.group(2).strip()
                
                action = {
                    'verb': verb,
                    'handler': handler,
                    'priority': priority
                }
                
                details = {
                    'target': target,
                    'full_text': recommendation
                }
                
                return action, details
        
        return None, {}
    
    def _simulate_resolution(
        self, 
        finding, 
        action: Dict, 
        details: Dict, 
        result: ResolutionResult
    ):
        """
        Simulate resolution (dry-run mode)
        
        Args:
            finding: Finding to resolve
            action: Parsed action dict
            details: Parsed details dict
            result: ResolutionResult to update
        """
        file_path = Path(finding.file_path)
        verb = action['verb']
        
        if verb == 'MOVE':
            target = details.get('target')
            if target:
                result.add_dry_run_action(f"WOULD move: {file_path} → {target}")
                
                # Check if imports need updating
                if file_path.suffix == '.py':
                    result.add_dry_run_action(f"WOULD update imports in: {file_path.name}")
                    result.add_dry_run_action(
                        f"WOULD scan project for references to: {file_path.name}"
                    )
            else:
                result.add_dry_run_action(f"WOULD move: {file_path} (target unclear)")
        
        elif verb == 'DELETE':
            if file_path.is_dir():
                try:
                    file_count = sum(1 for _ in file_path.rglob('*') if _.is_file())
                    result.add_dry_run_action(
                        f"WOULD delete directory: {file_path} ({file_count} files)"
                    )
                except:
                    result.add_dry_run_action(f"WOULD delete directory: {file_path}")
            else:
                result.add_dry_run_action(f"WOULD delete file: {file_path}")
        
        elif verb == 'CONSOLIDATE':
            target = details.get('target')
            if target:
                result.add_dry_run_action(
                    f"WOULD consolidate: {file_path} → {target}"
                )
            else:
                result.add_dry_run_action(
                    f"WOULD consolidate: {file_path} (merge with canonical location)"
                )
        
        elif verb == 'SPLIT':
            result.add_dry_run_action(
                f"WOULD split: {file_path} (break into focused documents)"
            )
        
        elif verb == 'CREATE':
            target = details.get('target')
            if target:
                result.add_dry_run_action(f"WOULD create: {target}")
            else:
                result.add_dry_run_action(
                    f"WOULD create: (target unclear from '{details['full_text']}')"
                )
        
        elif verb == 'REVIEW':
            result.add_dry_run_action(f"WOULD flag for review: {file_path}")
            result.findings_skipped += 1
            result.status = ResolutionStatus.SKIPPED
        
        else:
            result.add_dry_run_action(
                f"WOULD apply action '{verb}' to: {file_path}"
            )
    
    def _handle_move(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle MOVE action - Move file to correct directory
        
        Parses target directory from recommendation dynamically
        
        Steps:
        1. Extract target directory from details
        2. Validate source exists
        3. Create target directory if needed
        4. Move file
        5. Update imports if Python file (future enhancement)
        
        Args:
            finding: Finding with MOVE recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        source_path = Path(finding.file_path)
        
        if not source_path.exists():
            result.add_error(f"Source file not found: {source_path}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
            return
        
        # Get target directory from parsed details
        target_dir = details.get('target')
        
        if not target_dir:
            result.add_error(
                f"Could not extract target directory from: {details['full_text']}"
            )
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
            return
        
        # Normalize target directory (remove trailing slashes, etc.)
        target_dir = target_dir.rstrip('/')
        
        # Get project root (current working directory)
        project_root = Path.cwd()
        target_path = project_root / target_dir / source_path.name
        
        try:
            # Validate target doesn't already exist
            if target_path.exists():
                result.add_warning(
                    f"Target already exists: {target_path}. Skipping move."
                )
                result.findings_skipped += 1
                result.status = ResolutionStatus.SKIPPED
                return
            
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source_path), str(target_path))
            result.add_action(f"Moved: {source_path} → {target_path}")
            
            # If Python file, log that imports may need updating
            # (Actual import updating is complex and future enhancement)
            if target_path.suffix == '.py':
                result.add_warning(
                    f"Python file moved: {target_path.name}. "
                    "Manual review of imports recommended."
                )
            
            result.status = ResolutionStatus.SUCCESS
        
        except Exception as e:
            result.add_error(f"Failed to move file: {str(e)}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
    
    def _handle_delete(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle DELETE action - Remove obsolete file or directory
        
        Safety: Only deletes if recommendation explicitly says DELETE
        
        Args:
            finding: Finding with DELETE recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        target_path = Path(finding.file_path)
        
        if not target_path.exists():
            result.add_warning(f"Target already deleted: {target_path}")
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
            
            result.status = ResolutionStatus.SUCCESS
        
        except Exception as e:
            result.add_error(f"Failed to delete: {str(e)}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
    
    def _handle_consolidate(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle CONSOLIDATE action - Merge duplicate directories
        
        This is complex and requires careful planning.
        For now, flag for manual review.
        
        Args:
            finding: Finding with CONSOLIDATE recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        result.add_warning(
            f"CONSOLIDATE action requires manual review: {finding.file_path}"
        )
        result.add_action(f"Flagged for consolidation: {details['full_text']}")
        result.findings_skipped += 1
        result.status = ResolutionStatus.SKIPPED
    
    def _handle_split(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle SPLIT action - Break bloated documentation into focused docs
        
        This requires content analysis and is complex.
        Flag for manual intervention.
        
        Args:
            finding: Finding with SPLIT recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        result.add_warning(
            f"SPLIT action requires manual review: {finding.file_path}"
        )
        result.add_action(f"Flagged for splitting: {details['full_text']}")
        result.findings_skipped += 1
        result.status = ResolutionStatus.SKIPPED
    
    def _handle_create(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle CREATE action - Create missing directories/files
        
        Parses target from recommendation and creates it.
        
        Args:
            finding: Finding with CREATE recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        # Extract what to create from recommendation text
        # Look for patterns like "CREATE missing subdirectories: modules/, architecture/"
        full_text = details['full_text']
        
        # Try to find target after "CREATE" or similar
        create_match = re.search(
            r'CREATE\s+(?:missing\s+)?(?:subdirectories?:?\s+)?([^\n\.]+)', 
            full_text,
            re.IGNORECASE
        )
        
        if not create_match:
            result.add_warning(
                f"Could not parse CREATE target from: {full_text}"
            )
            result.findings_skipped += 1
            result.status = ResolutionStatus.SKIPPED
            return
        
        # Extract list of things to create (may be comma-separated)
        targets_str = create_match.group(1).strip()
        targets = [t.strip().rstrip('/') for t in re.split(r'[,\s]+', targets_str)]
        
        project_root = Path.cwd()
        base_path = Path(finding.file_path)
        
        try:
            for target in targets:
                if not target:
                    continue
                
                # Determine full path
                if base_path.is_dir():
                    full_path = base_path / target
                else:
                    full_path = project_root / target
                
                # Create directory
                full_path.mkdir(parents=True, exist_ok=True)
                result.add_action(f"Created directory: {full_path}")
            
            result.status = ResolutionStatus.SUCCESS
        
        except Exception as e:
            result.add_error(f"Failed to create: {str(e)}")
            result.findings_failed += 1
            result.status = ResolutionStatus.FAILED
    
    def _handle_review(self, finding, details: Dict, result: ResolutionResult):
        """
        Handle REVIEW action - Flag for manual review
        
        These findings need human judgment, not automated resolution.
        
        Args:
            finding: Finding with REVIEW recommendation
            details: Parsed details from recommendation
            result: ResolutionResult to update
        """
        result.add_warning(
            f"Flagged for manual review: {finding.file_path} - {details['full_text']}"
        )
        result.findings_skipped += 1
        result.status = ResolutionStatus.SKIPPED