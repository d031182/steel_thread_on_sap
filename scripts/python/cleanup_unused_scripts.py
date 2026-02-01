#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Cleanup Utility

Analyzes scripts/ directory and helps identify/remove unused scripts.
Focus on cleaning up scripts/tmp/ (one-shot scripts) and identifying
unused scripts in other directories.

Usage:
    python scripts/python/cleanup_unused_scripts.py [options]

Options:
    --dry-run    : Show what would be deleted without actually deleting
    --auto-tmp   : Automatically delete all scripts in tmp/ older than 7 days
    --threshold  : Days threshold for considering files old (default: 30)
    --interactive: Ask before deleting each file
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Directories to analyze
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
TMP_DIR = SCRIPTS_DIR / 'tmp'
PYTHON_DIR = SCRIPTS_DIR / 'python'
TEST_DIR = SCRIPTS_DIR / 'test'

# Script patterns that are likely referenced
COMMON_PATTERNS = [
    'create_', 'populate_', 'migrate_', 'rebuild_', 'generate_',
    'sync_', 'import_', 'init_'
]

class ScriptAnalyzer:
    """Analyzes scripts for usage and determines cleanup candidates"""
    
    def __init__(self, threshold_days=30):
        self.threshold_days = threshold_days
        self.threshold_date = datetime.now() - timedelta(days=threshold_days)
        
    def analyze_scripts(self):
        """Main analysis function"""
        print("="*80)
        print("SCRIPT CLEANUP UTILITY")
        print("="*80)
        print(f"\nAnalyzing scripts directory: {SCRIPTS_DIR}")
        print(f"Threshold for 'old' files: {self.threshold_days} days\n")
        
        results = {
            'tmp': self.analyze_tmp_dir(),
            'python': self.analyze_python_dir(),
            'test': self.analyze_test_dir(),
            'summary': {}
        }
        
        # Generate summary
        results['summary'] = self.generate_summary(results)
        
        return results
    
    def analyze_tmp_dir(self):
        """Analyze scripts/tmp/ - all files here are candidates for deletion"""
        print("\n" + "="*80)
        print("ANALYZING: scripts/tmp/ (One-shot scripts)")
        print("="*80)
        
        if not TMP_DIR.exists():
            print("⚠️  scripts/tmp/ does not exist")
            return {'files': [], 'total': 0}
        
        files = list(TMP_DIR.glob('*.py'))
        
        if not files:
            print("✅ scripts/tmp/ is empty (no cleanup needed)")
            return {'files': [], 'total': 0}
        
        results = {'files': [], 'total': len(files)}
        
        print(f"\nFound {len(files)} file(s) in scripts/tmp/:\n")
        
        for file in files:
            age_days = self.get_file_age_days(file)
            last_modified = datetime.fromtimestamp(file.stat().st_mtime)
            size_kb = file.stat().st_size / 1024
            
            status = "🔴 OLD" if age_days > self.threshold_days else "🟡 RECENT"
            
            print(f"{status} {file.name}")
            print(f"     Age: {age_days} days | Modified: {last_modified.strftime('%Y-%m-%d')} | Size: {size_kb:.1f} KB")
            
            results['files'].append({
                'path': file,
                'name': file.name,
                'age_days': age_days,
                'last_modified': last_modified,
                'size_kb': size_kb,
                'recommend_delete': True  # All tmp files are candidates
            })
        
        return results
    
    def analyze_python_dir(self):
        """Analyze scripts/python/ - look for unused utility scripts"""
        print("\n" + "="*80)
        print("ANALYZING: scripts/python/ (Utility scripts)")
        print("="*80)
        
        if not PYTHON_DIR.exists():
            print("⚠️  scripts/python/ does not exist")
            return {'files': [], 'total': 0}
        
        files = list(PYTHON_DIR.glob('*.py'))
        results = {'files': [], 'total': len(files)}
        
        print(f"\nFound {len(files)} file(s) in scripts/python/\n")
        
        for file in files:
            age_days = self.get_file_age_days(file)
            last_modified = datetime.fromtimestamp(file.stat().st_mtime)
            size_kb = file.stat().st_size / 1024
            is_old = age_days > self.threshold_days
            
            # Check if likely unused
            is_referenced = self.check_if_referenced(file.name)
            recommend_delete = is_old and not is_referenced
            
            if recommend_delete:
                status = "🔴 POTENTIALLY UNUSED"
            elif is_old:
                status = "🟡 OLD BUT REFERENCED"
            else:
                status = "🟢 RECENT"
            
            if recommend_delete or is_old:
                print(f"{status} {file.name}")
                print(f"     Age: {age_days} days | Modified: {last_modified.strftime('%Y-%m-%d')} | Size: {size_kb:.1f} KB")
                if is_referenced:
                    print(f"     ℹ️  Appears to be referenced in project")
            
            results['files'].append({
                'path': file,
                'name': file.name,
                'age_days': age_days,
                'last_modified': last_modified,
                'size_kb': size_kb,
                'is_referenced': is_referenced,
                'recommend_delete': recommend_delete
            })
        
        return results
    
    def analyze_test_dir(self):
        """Analyze scripts/test/ - identify old test scripts"""
        print("\n" + "="*80)
        print("ANALYZING: scripts/test/ (Test scripts)")
        print("="*80)
        
        if not TEST_DIR.exists():
            print("⚠️  scripts/test/ does not exist")
            return {'files': [], 'total': 0}
        
        files = list(TEST_DIR.glob('*.py'))
        results = {'files': [], 'total': len(files)}
        
        print(f"\nFound {len(files)} file(s) in scripts/test/\n")
        
        old_tests = [f for f in files if self.get_file_age_days(f) > self.threshold_days]
        
        if old_tests:
            print(f"Found {len(old_tests)} old test script(s):\n")
            for file in old_tests:
                age_days = self.get_file_age_days(file)
                last_modified = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"🟡 {file.name}")
                print(f"     Age: {age_days} days | Modified: {last_modified.strftime('%Y-%m-%d')}")
        else:
            print("✅ No old test scripts found")
        
        for file in files:
            results['files'].append({
                'path': file,
                'name': file.name,
                'age_days': self.get_file_age_days(file),
                'recommend_delete': False  # Tests are kept unless explicitly unused
            })
        
        return results
    
    def get_file_age_days(self, file_path):
        """Calculate file age in days"""
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - last_modified
        return age.days
    
    def check_if_referenced(self, filename):
        """Check if script name appears in PROJECT_TRACKER or other key files"""
        # Simple heuristic: check common patterns
        stem = Path(filename).stem
        
        # Scripts with common patterns are likely in use
        for pattern in COMMON_PATTERNS:
            if stem.startswith(pattern):
                return True
        
        # Check if mentioned in PROJECT_TRACKER.md
        tracker_file = PROJECT_ROOT / 'PROJECT_TRACKER.md'
        if tracker_file.exists():
            content = tracker_file.read_text(encoding='utf-8')
            if stem in content or filename in content:
                return True
        
        return False
    
    def generate_summary(self, results):
        """Generate summary statistics"""
        summary = {
            'tmp_total': results['tmp']['total'],
            'tmp_candidates': len([f for f in results['tmp']['files'] if f['recommend_delete']]),
            'python_total': results['python']['total'],
            'python_candidates': len([f for f in results['python']['files'] if f['recommend_delete']]),
            'test_total': results['test']['total'],
        }
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"\nscripts/tmp/:")
        print(f"  Total: {summary['tmp_total']} files")
        print(f"  Deletion candidates: {summary['tmp_candidates']} files")
        
        print(f"\nscripts/python/:")
        print(f"  Total: {summary['python_total']} files")
        print(f"  Potentially unused: {summary['python_candidates']} files")
        
        print(f"\nscripts/test/:")
        print(f"  Total: {summary['test_total']} files")
        
        total_candidates = summary['tmp_candidates'] + summary['python_candidates']
        print(f"\n💡 Total cleanup candidates: {total_candidates} files")
        
        return summary

    def cleanup(self, results, dry_run=True, auto_tmp=False, interactive=False):
        """Execute cleanup based on analysis results"""
        print("\n" + "="*80)
        print("CLEANUP EXECUTION")
        print("="*80)
        
        if dry_run:
            print("\n🔵 DRY RUN MODE - No files will be deleted\n")
        else:
            print("\n🔴 LIVE MODE - Files will be PERMANENTLY deleted\n")
        
        deleted_count = 0
        
        # Clean up tmp/ directory
        if auto_tmp or not interactive:
            for file_info in results['tmp']['files']:
                if self.should_delete_file(file_info, dry_run, interactive, "tmp"):
                    if not dry_run:
                        file_info['path'].unlink()
                    deleted_count += 1
                    print(f"{'[DRY RUN] Would delete' if dry_run else '✅ Deleted'}: {file_info['name']}")
        
        # Clean up python/ directory (only with confirmation)
        if interactive:
            for file_info in results['python']['files']:
                if file_info['recommend_delete']:
                    if self.should_delete_file(file_info, dry_run, True, "python"):
                        if not dry_run:
                            file_info['path'].unlink()
                        deleted_count += 1
                        print(f"{'[DRY RUN] Would delete' if dry_run else '✅ Deleted'}: {file_info['name']}")
        
        print(f"\n{'[DRY RUN] Would delete' if dry_run else 'Deleted'}: {deleted_count} file(s)")
        
        return deleted_count
    
    def should_delete_file(self, file_info, dry_run, interactive, category):
        """Determine if file should be deleted"""
        if not file_info['recommend_delete']:
            return False
        
        if not interactive:
            return True
        
        print(f"\n📋 {file_info['name']} ({category}/)")
        print(f"   Age: {file_info['age_days']} days")
        print(f"   Last modified: {file_info['last_modified'].strftime('%Y-%m-%d %H:%M')}")
        
        response = input("   Delete this file? [y/N]: ").strip().lower()
        return response == 'y'


def main():
    parser = argparse.ArgumentParser(description='Cleanup unused scripts')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be deleted without deleting')
    parser.add_argument('--auto-tmp', action='store_true',
                        help='Automatically delete scripts in tmp/ older than threshold')
    parser.add_argument('--threshold', type=int, default=30,
                        help='Days threshold for considering files old (default: 30)')
    parser.add_argument('--interactive', action='store_true',
                        help='Ask before deleting each file')
    parser.add_argument('--execute', action='store_true',
                        help='Execute cleanup (not dry-run)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ScriptAnalyzer(threshold_days=args.threshold)
    
    # Run analysis
    results = analyzer.analyze_scripts()
    
    # Execute cleanup if requested
    if args.execute or args.interactive:
        if args.interactive or input("\n\nProceed with cleanup? [y/N]: ").strip().lower() == 'y':
            analyzer.cleanup(
                results,
                dry_run=not args.execute,
                auto_tmp=args.auto_tmp,
                interactive=args.interactive
            )
    else:
        print("\n💡 Tip: Run with --execute to perform cleanup, or --interactive for manual review")
    
    print("\n" + "="*80)
    print("DONE")
    print("="*80)


if __name__ == '__main__':
    main()