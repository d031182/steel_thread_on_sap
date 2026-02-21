"""
Feng Shui Preview Mode CLI - Validate Module Designs Before Implementation

Provides validation for module designs against Module Federation Standard,
catching violations BEFORE code is written (< 1 second vs 60-300 seconds for browser testing).

Usage Examples:
    python -m tools.fengshui.preview                          # Interactive mode
    python -m tools.fengshui.preview --spec module_spec.json  # JSON spec mode
    python -m tools.fengshui.preview --help                   # Show help

Philosophy: "Test the design, trust the implementation"
Catch architecture violations in planning phase, not implementation phase.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from tools.fengshui.preview.engine import PreviewEngine, Severity
from tools.fengshui.preview.parsers import parse_module_design


def show_banner():
    """Display Preview Mode banner"""
    print()
    print("=" * 70)
    print("  🔮 FENG SHUI PREVIEW MODE - Design Validation")
    print("  'Test the Design, Trust the Implementation'")
    print("=" * 70)
    print()


def format_severity(severity: Severity) -> str:
    """Format severity with color coding"""
    colors = {
        Severity.CRITICAL: "🔴 CRITICAL",
        Severity.HIGH: "🟠 HIGH",
        Severity.MEDIUM: "🟡 MEDIUM",
        Severity.LOW: "🔵 LOW",
        Severity.INFO: "⚪ INFO"
    }
    return colors.get(severity, str(severity))


def display_results(result, output_format: str = "console"):
    """Display validation results"""
    if output_format == "json":
        # JSON output for CI/CD integration (use result.to_dict())
        print(json.dumps(result.to_dict(), indent=2))
        return
    
    # Console output (human-friendly)
    print()
    print("=" * 70)
    print(f"  MODULE: {result.module_name}")
    print("=" * 70)
    print()
    
    # Check if there are blockers
    has_blockers = result.has_blockers
    if not result.findings:
        print("✅ VALIDATION PASSED")
        print(f"   No violations found")
    elif has_blockers:
        print("❌ VALIDATION FAILED - BLOCKERS DETECTED")
        print(f"   Found {len(result.findings)} violation(s)")
    else:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print(f"   Found {len(result.findings)} non-blocking issue(s)")
    
    print()
    print(f"⏱️  Validation Time: {result.validation_time_seconds:.3f}s")
    print(f"✅ Validators Run: {', '.join(result.validators_run)}")
    print()
    
    # Group findings by severity
    findings_by_severity = {}
    for finding in result.findings:
        if finding.severity not in findings_by_severity:
            findings_by_severity[finding.severity] = []
        findings_by_severity[finding.severity].append(finding)
    
    # Display findings (CRITICAL → INFO)
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
        if severity not in findings_by_severity:
            continue
        
        findings = findings_by_severity[severity]
        print(f"{format_severity(severity)} ({len(findings)} finding(s))")
        print("-" * 70)
        
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. [{finding.category}]")
            print(f"   Location: {finding.location}")
            print(f"   Message: {finding.message}")
            if finding.suggestion:
                print(f"   💡 Suggestion: {finding.suggestion}")
        
        print()
    
    print()


def interactive_mode():
    """Interactive mode - guided prompts for module design"""
    show_banner()
    
    print("📝 Interactive Module Design Validation")
    print("   Answer the following questions about your module design:")
    print()
    
    # Collect module information
    module_id = input("Module ID (snake_case, e.g., 'ai_assistant'): ").strip()
    if not module_id:
        print("❌ Error: Module ID is required")
        sys.exit(1)
    
    route = input(f"Route (kebab-case, e.g., '/ai-assistant'): ").strip()
    factory_name = input(f"Factory Name (PascalCase, e.g., 'AIAssistantModule'): ").strip()
    
    print()
    print("Required files (comma-separated, e.g., 'module.json,README.md'):")
    files_input = input("Files: ").strip()
    files = [f.strip() for f in files_input.split(",")] if files_input else []
    
    print()
    print("Required directories (comma-separated, e.g., 'backend,frontend,tests'):")
    dirs_input = input("Directories: ").strip()
    directories = [d.strip() for d in dirs_input.split(",")] if dirs_input else []
    
    print()
    print("Backend API path (e.g., '/api/ai-assistant'):")
    backend_api = input("API Path: ").strip()
    
    print()
    print("Dependencies (comma-separated module IDs, e.g., 'logger,data_products_v2'):")
    deps_input = input("Dependencies: ").strip()
    dependencies = [d.strip() for d in deps_input.split(",")] if deps_input else []
    
    # Build spec
    spec = {
        "module_id": module_id,
        "route": route,
        "factory_name": factory_name,
        "files": files,
        "directories": directories,
        "backend_api": backend_api,
        "dependencies": dependencies
    }
    
    print()
    print("🔍 Validating design...")
    print()
    
    # Run validation
    engine = PreviewEngine()
    result = engine.validate_design(spec)
    
    # Display results
    display_results(result)
    
    # Exit with appropriate code (0 = success, 1 = blockers found)
    sys.exit(1 if result.has_blockers else 0)


def spec_mode(spec_path: Path, output_format: str = "console"):
    """Spec mode - validate from JSON file"""
    show_banner()
    
    print(f"📄 Validating module spec: {spec_path}")
    print()
    
    # Load spec
    try:
        with open(spec_path, 'r') as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Spec file not found: {spec_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in spec file: {e}")
        sys.exit(1)
    
    # Validate required fields
    if "module_id" not in spec:
        print("❌ Error: 'module_id' is required in spec file")
        sys.exit(1)
    
    print(f"🔍 Validating module: {spec['module_id']}")
    print()
    
    # Run validation
    engine = PreviewEngine()
    result = engine.validate_design(spec)
    
    # Display results
    display_results(result, output_format)
    
    # Exit with appropriate code (0 = success, 1 = blockers found)
    sys.exit(1 if result.has_blockers else 0)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Feng Shui Preview Mode - Validate Module Designs Before Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (guided prompts)
  %(prog)s
  
  # Validate from JSON spec file
  %(prog)s --spec examples/module_spec.json
  
  # JSON output (for CI/CD)
  %(prog)s --spec module_spec.json --format json

Philosophy:
  Preview Mode validates module designs BEFORE implementation,
  catching architecture violations in < 1 second (vs 60-300s for browser tests).
  
  "Test the Design, Trust the Implementation"
  
  5 Core Validators:
    1. NamingValidator    - Module Federation naming conventions
    2. StructureValidator - Required files and directories
    3. IsolationValidator - Cross-module import detection (CRITICAL)
    4. DependencyValidator - module.json declarations
    5. PatternValidator   - Repository/Service layer patterns
  
  Benefits:
    - Catch violations BEFORE coding (planning phase)
    - 60-300x faster than browser testing (< 1s vs 60-300s)
    - Actionable feedback with suggestions
    - CI/CD integration ready (JSON output)
        """
    )
    
    parser.add_argument(
        '--spec',
        type=Path,
        help='Path to module specification JSON file'
    )
    
    parser.add_argument(
        '--module',
        type=str,
        help='Auto-parse module from modules/ directory (e.g., --module ai_assistant)'
    )
    
    parser.add_argument(
        '--format',
        choices=['console', 'json'],
        default='console',
        help='Output format (default: console)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.module:
            # Auto-parse mode
            module_path = Path('modules') / args.module
            if not module_path.exists():
                print(f"❌ Error: Module directory not found: {module_path}")
                sys.exit(1)
            
            show_banner()
            print(f"📖 Parsing design documents from: {module_path}")
            print()
            
            spec = parse_module_design(str(module_path))
            if not spec:
                print(f"❌ Failed to parse module design (module.json required)")
                sys.exit(1)
            
            print(f"✅ Extracted specification from {len(spec.get('_extracted_from', []))} files")
            print(f"   Confidence: {spec.get('_confidence', 0):.1%}")
            print()
            print(f"🔍 Validating module: {spec['module_id']}")
            print()
            
            # Run validation
            engine = PreviewEngine()
            result = engine.validate_design(spec)
            
            # Display results
            display_results(result, args.format)
            
            # Exit with appropriate code
            sys.exit(1 if result.has_blockers else 0)
            
        elif args.spec:
            # Spec mode
            spec_mode(args.spec, args.format)
        else:
            # Interactive mode
            interactive_mode()
    
    except KeyboardInterrupt:
        print()
        print("⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()