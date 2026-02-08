"""
Feng Shui + Gu Wu Integration Script

Complete pipeline:
1. Run Feng Shui multi-agent orchestrator on module
2. Get comprehensive JSON report (7 agents)
3. Generate pytest tests via Gu Wu
4. Run tests
5. Report results
"""

import sys
import json
from pathlib import Path
import subprocess


def integrate_feng_shui_guwu(module_name: str, run_tests: bool = True):
    """
    Complete Feng Shui → Gu Wu → pytest pipeline
    
    Args:
        module_name: Name of module to analyze
        run_tests: Whether to run generated tests (default True)
    """
    print("=" * 70)
    print("🔬 Feng Shui + Gu Wu Integration Pipeline")
    print("=" * 70)
    
    # Step 1: Run Feng Shui multi-agent orchestrator
    print("\n📊 Step 1: Running Feng Shui multi-agent orchestrator...")
    
    # Import orchestrator
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.fengshui.agents.orchestrator import AgentOrchestrator
    from tools.guwu.generators.app_v2_test_generator import AppV2TestGenerator
    
    module_path = Path(f"modules/{module_name}")
    
    # Run only App V2 agent (for targeted App V2 validation)
    orchestrator = AgentOrchestrator()
    comprehensive_report = orchestrator.analyze_module_comprehensive(
        module_path,
        parallel=False,  # Single agent, no need for parallelism
        selected_agents=['app_v2']
    )
    
    # Extract App V2 agent report
    app_v2_report = next(
        (r for r in comprehensive_report.agent_reports if r.agent_name == 'app_v2'),
        None
    )
    
    if not app_v2_report:
        print("   ❌ App V2 agent failed to run")
        return False
    
    print(f"   ✅ Feng Shui analysis complete: {len(app_v2_report.findings)} findings")
    
    # Convert to Gu Wu-compatible format
    report_dict = app_v2_report.to_dict()
    
    # Save report (for debugging)
    report_file = Path(f"feng_shui_report_{module_name}.json")
    report_file.write_text(json.dumps(report_dict, indent=2))
    print(f"   📄 Report saved: {report_file}")
    
    # Step 2: Generate tests via Gu Wu
    print("\n🧪 Step 2: Generating pytest tests via Gu Wu...")
    generator = AppV2TestGenerator()
    test_file = generator.generate_from_report(app_v2_report)
    
    print(f"   ✅ Tests generated: {test_file}")
    
    # Step 3: Run tests (optional)
    if run_tests:
        print("\n🏃 Step 3: Running generated tests...")
        result = subprocess.run(
            ['pytest', str(test_file), '-v'],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed (see output above)")
            return False
    
    print("\n" + "=" * 70)
    print("✅ Pipeline complete!")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m tools.guwu.feng_shui_integration <module_name>")
        print("\nExample:")
        print("  python -m tools.guwu.feng_shui_integration knowledge_graph_v2")
        sys.exit(1)
    
    module_name = sys.argv[1]
    success = integrate_feng_shui_guwu(module_name)
    
    sys.exit(0 if success else 1)