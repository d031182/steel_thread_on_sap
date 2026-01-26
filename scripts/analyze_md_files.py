"""
Markdown Documentation Analyzer
================================
Analyzes .md files in the project and suggests cleanup/consolidation actions.

Features:
- Identifies obsolete files (old, deprecated, empty)
- Finds duplicate/similar content
- Suggests consolidation opportunities
- Generates cleanup recommendations

Usage:
    python scripts/analyze_md_files.py
    python scripts/analyze_md_files.py --auto-archive  # Move obsolete to archive/
    python scripts/analyze_md_files.py --report-only   # Just generate report
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
EXCLUDE_DIRS = {'node_modules', '.pytest_cache', '.git', '__pycache__', 'venv'}
ARCHIVE_DIR = PROJECT_ROOT / 'docs' / 'archive'

class MarkdownAnalyzer:
    def __init__(self):
        self.files = []
        self.issues = defaultdict(list)
        self.stats = {
            'total': 0,
            'empty': 0,
            'small': 0,
            'large': 0,
            'old': 0,
            'recent': 0
        }
    
    def scan_files(self):
        """Scan all .md files in project"""
        print("🔍 Scanning for .md files...")
        
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith('.md'):
                    filepath = Path(root) / file
                    self.analyze_file(filepath)
        
        self.stats['total'] = len(self.files)
        print(f"   Found {self.stats['total']} .md files\n")
    
    def analyze_file(self, filepath: Path):
        """Analyze single markdown file"""
        try:
            stat = filepath.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - modified).days
            
            # Read content
            try:
                content = filepath.read_text(encoding='utf-8')
            except:
                content = filepath.read_text(encoding='latin-1')
            
            lines = content.strip().split('\n')
            line_count = len(lines)
            
            file_info = {
                'path': filepath.relative_to(PROJECT_ROOT),
                'size': size,
                'lines': line_count,
                'modified': modified,
                'age_days': age_days,
                'content': content
            }
            
            self.files.append(file_info)
            
            # Categorize
            if size < 100:
                self.stats['empty'] += 1
                self.issues['empty'].append(file_info)
            elif size < 1000:
                self.stats['small'] += 1
            elif size > 50000:
                self.stats['large'] += 1
                self.issues['large'].append(file_info)
            
            if age_days > 30:
                self.stats['old'] += 1
                if age_days > 60:
                    self.issues['very_old'].append(file_info)
            else:
                self.stats['recent'] += 1
            
            # Check for deprecation markers
            if self._is_deprecated(content):
                self.issues['deprecated'].append(file_info)
            
            # Check for planning/session docs (often obsolete)
            if 'planning' in str(filepath) or 'session' in str(filepath).lower():
                if age_days > 14:  # 2 weeks old planning docs
                    self.issues['old_planning'].append(file_info)
            
        except Exception as e:
            print(f"   ⚠️  Error analyzing {filepath}: {e}")
    
    def _is_deprecated(self, content: str) -> bool:
        """Check if file contains deprecation markers"""
        markers = [
            'DEPRECATED',
            'OBSOLETE',
            'DO NOT USE',
            '⚠️ This document is outdated',
            'This document has been superseded'
        ]
        return any(marker.lower() in content.lower() for marker in markers)
    
    def find_duplicates(self):
        """Find potential duplicate files by name similarity"""
        print("🔍 Finding potential duplicates...\n")
        
        name_groups = defaultdict(list)
        for file_info in self.files:
            # Group by similar names (ignoring extensions and common prefixes)
            base_name = file_info['path'].stem.lower()
            base_name = re.sub(r'^(the|a|an)_', '', base_name)
            name_groups[base_name].append(file_info)
        
        # Find groups with multiple files
        for base_name, files in name_groups.items():
            if len(files) > 1:
                self.issues['potential_duplicates'].append({
                    'group': base_name,
                    'files': files
                })
    
    def find_consolidation_opportunities(self):
        """Find files that could be consolidated"""
        print("🔍 Finding consolidation opportunities...\n")
        
        # Group by directory
        dir_groups = defaultdict(list)
        for file_info in self.files:
            parent = file_info['path'].parent
            if parent != Path('.'):  # Skip root
                dir_groups[parent].append(file_info)
        
        # Find directories with many small files
        for directory, files in dir_groups.items():
            small_files = [f for f in files if f['size'] < 5000]  # < 5KB
            if len(small_files) >= 3:
                self.issues['consolidation'].append({
                    'directory': directory,
                    'file_count': len(files),
                    'small_file_count': len(small_files),
                    'files': small_files
                })
    
    def generate_report(self):
        """Generate analysis report"""
        print("\n" + "="*70)
        print("📊 MARKDOWN DOCUMENTATION ANALYSIS REPORT")
        print("="*70 + "\n")
        
        # Statistics
        print("📈 Statistics")
        print("-" * 70)
        print(f"Total files:        {self.stats['total']}")
        print(f"Empty/tiny (<100B): {self.stats['empty']}")
        print(f"Small (<1KB):       {self.stats['small']}")
        print(f"Large (>50KB):      {self.stats['large']}")
        print(f"Old (>30 days):     {self.stats['old']}")
        print(f"Recent (≤30 days):  {self.stats['recent']}")
        print()
        
        # Issues
        total_issues = sum(len(v) if isinstance(v, list) else len(v) 
                          for v in self.issues.values())
        print(f"🚨 Issues Found: {total_issues}")
        print("-" * 70)
        
        # Empty files
        if self.issues['empty']:
            print(f"\n❌ Empty/Tiny Files ({len(self.issues['empty'])})")
            print("   Recommendation: DELETE (no useful content)\n")
            for file in self.issues['empty'][:10]:  # Show first 10
                print(f"   • {file['path']} ({file['size']} bytes)")
            if len(self.issues['empty']) > 10:
                print(f"   ... and {len(self.issues['empty']) - 10} more")
        
        # Deprecated files
        if self.issues['deprecated']:
            print(f"\n⚠️  Deprecated Files ({len(self.issues['deprecated'])})")
            print("   Recommendation: ARCHIVE or DELETE\n")
            for file in self.issues['deprecated']:
                print(f"   • {file['path']}")
        
        # Old planning docs
        if self.issues['old_planning']:
            print(f"\n📅 Old Planning/Session Docs ({len(self.issues['old_planning'])})")
            print("   Recommendation: ARCHIVE (completed plans/sessions)\n")
            for file in self.issues['old_planning'][:10]:
                days = file['age_days']
                print(f"   • {file['path']} ({days} days old)")
            if len(self.issues['old_planning']) > 10:
                print(f"   ... and {len(self.issues['old_planning']) - 10} more")
        
        # Very old files
        if self.issues['very_old']:
            print(f"\n🕰️  Very Old Files (>60 days) ({len(self.issues['very_old'])})")
            print("   Recommendation: REVIEW - May be outdated\n")
            for file in self.issues['very_old'][:10]:
                days = file['age_days']
                print(f"   • {file['path']} ({days} days old)")
            if len(self.issues['very_old']) > 10:
                print(f"   ... and {len(self.issues['very_old']) - 10} more")
        
        # Potential duplicates
        if self.issues['potential_duplicates']:
            print(f"\n🔄 Potential Duplicate Groups ({len(self.issues['potential_duplicates'])})")
            print("   Recommendation: MERGE or DELETE duplicates\n")
            for group in self.issues['potential_duplicates'][:5]:
                print(f"   📁 {group['group']}:")
                for file in group['files']:
                    print(f"      • {file['path']} ({file['size']} bytes)")
                print()
        
        # Consolidation opportunities
        if self.issues['consolidation']:
            print(f"\n📦 Consolidation Opportunities ({len(self.issues['consolidation'])})")
            print("   Recommendation: MERGE small related files\n")
            for opp in self.issues['consolidation'][:5]:
                print(f"   📁 {opp['directory']} ({opp['small_file_count']} small files)")
                for file in opp['files'][:3]:
                    print(f"      • {file['path'].name} ({file['size']} bytes)")
                if len(opp['files']) > 3:
                    print(f"      ... and {len(opp['files']) - 3} more")
                print()
        
        # Large files
        if self.issues['large']:
            print(f"\n📚 Large Files (>50KB) ({len(self.issues['large'])})")
            print("   Recommendation: Consider splitting if too complex\n")
            for file in self.issues['large']:
                kb = file['size'] / 1024
                print(f"   • {file['path']} ({kb:.1f} KB)")
        
        print("\n" + "="*70)
        print("💡 RECOMMENDED ACTIONS")
        print("="*70 + "\n")
        
        action_count = 0
        
        if self.issues['empty']:
            action_count += len(self.issues['empty'])
            print(f"1. DELETE {len(self.issues['empty'])} empty/tiny files")
        
        if self.issues['deprecated']:
            action_count += len(self.issues['deprecated'])
            print(f"2. ARCHIVE {len(self.issues['deprecated'])} deprecated files")
        
        if self.issues['old_planning']:
            action_count += len(self.issues['old_planning'])
            print(f"3. ARCHIVE {len(self.issues['old_planning'])} old planning/session docs")
        
        if self.issues['potential_duplicates']:
            dup_count = sum(len(g['files'])-1 for g in self.issues['potential_duplicates'])
            action_count += dup_count
            print(f"4. REVIEW & MERGE {len(self.issues['potential_duplicates'])} duplicate groups")
        
        if self.issues['consolidation']:
            print(f"5. CONSOLIDATE {len(self.issues['consolidation'])} directories with many small files")
        
        print(f"\n🎯 Potential cleanup: ~{action_count} files could be deleted/archived")
        print(f"💾 Space savings: ~{self._calculate_savings()} KB\n")
    
    def _calculate_savings(self):
        """Calculate potential space savings"""
        savings = 0
        for file in self.issues['empty']:
            savings += file['size']
        for file in self.issues['deprecated']:
            savings += file['size']
        for file in self.issues['old_planning']:
            savings += file['size']
        return savings / 1024  # Convert to KB
    
    def generate_cleanup_script(self):
        """Generate PowerShell script for cleanup"""
        script_path = PROJECT_ROOT / 'scripts' / 'cleanup_md_files.ps1'
        
        with open(script_path, 'w') as f:
            f.write("# Markdown Files Cleanup Script\n")
            f.write("# Generated: " + datetime.now().isoformat() + "\n\n")
            f.write("# Review each section before executing!\n\n")
            
            if self.issues['empty']:
                f.write("# DELETE Empty/Tiny Files\n")
                for file in self.issues['empty']:
                    f.write(f"# Remove-Item '{file['path']}'\n")
                f.write("\n")
            
            if self.issues['deprecated'] or self.issues['old_planning']:
                f.write("# ARCHIVE Old/Deprecated Files\n")
                f.write(f"# New-Item -Path 'docs/archive' -ItemType Directory -Force\n")
                
                for file in self.issues['deprecated']:
                    f.write(f"# Move-Item '{file['path']}' 'docs/archive/'\n")
                
                for file in self.issues['old_planning']:
                    f.write(f"# Move-Item '{file['path']}' 'docs/archive/'\n")
                f.write("\n")
        
        print(f"📝 Cleanup script generated: {script_path}")
        print("   Review and uncomment lines to execute\n")


def main():
    import sys
    # Fix Windows console encoding for emojis
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    analyzer = MarkdownAnalyzer()
    
    print("="*70)
    print("🔧 MARKDOWN DOCUMENTATION ANALYZER")
    print("="*70 + "\n")
    
    # Scan files
    analyzer.scan_files()
    
    # Analyze
    analyzer.find_duplicates()
    analyzer.find_consolidation_opportunities()
    
    # Report
    analyzer.generate_report()
    
    # Generate cleanup script
    analyzer.generate_cleanup_script()
    
    print("✅ Analysis complete!")
    print("\nNext steps:")
    print("1. Review the report above")
    print("2. Check scripts/cleanup_md_files.ps1 for suggested actions")
    print("3. Manually review files before deleting")
    print("4. Consider consolidating related documentation\n")


if __name__ == '__main__':
    main()