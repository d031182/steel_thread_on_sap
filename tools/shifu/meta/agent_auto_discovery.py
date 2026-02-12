"""
Shi Fu Agent Auto-Discovery

Automatically discovers new Feng Shui agents and updates the registry.

Philosophy:
"The wise teacher stays current with their students' growth."

Auto-Discovery Process:
1. Scan tools/fengshui/agents/ directory
2. Find all *_agent.py files
3. Extract agent class names (e.g., ArchitectAgent)
4. Introspect agent to extract purpose, detectors, etc.
5. Generate registry entry automatically
6. Detect when registry is out of sync
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class DiscoveredAgent:
    """Represents an auto-discovered Feng Shui agent"""
    name: str  # e.g., "ArchitectAgent"
    file_path: str  # e.g., "tools/fengshui/agents/architect_agent.py"
    class_obj: type  # The actual class object
    detectors: List[str]  # List of detector method names
    purpose_hint: str  # Extracted from class docstring


class AgentAutoDiscovery:
    """
    Automatically discovers Feng Shui agents from source code
    
    Key Features:
    - Scans tools/fengshui/agents/ directory
    - Extracts agent class names and detectors
    - Detects out-of-sync registry
    - Suggests registry updates
    """
    
    def __init__(self, agents_dir: Optional[Path] = None):
        """
        Initialize auto-discovery
        
        Args:
            agents_dir: Path to Feng Shui agents directory
                       (default: tools/fengshui/agents/)
        """
        self.agents_dir = agents_dir or Path("tools/fengshui/agents")
    
    def discover_agents(self) -> List[DiscoveredAgent]:
        """
        Discover all Feng Shui agents automatically
        
        Returns:
            List of DiscoveredAgent objects
        """
        discovered = []
        
        if not self.agents_dir.exists():
            return discovered
        
        # Find all agent files
        for agent_file in self.agents_dir.glob("*_agent.py"):
            if agent_file.name.startswith("_"):
                continue  # Skip __init__.py, _base.py, etc.
            
            try:
                agent = self._analyze_agent_file(agent_file)
                if agent:
                    discovered.append(agent)
            except Exception as e:
                print(f"⚠️ Failed to analyze {agent_file.name}: {e}")
        
        return discovered
    
    def _analyze_agent_file(self, file_path: Path) -> Optional[DiscoveredAgent]:
        """
        Analyze a single agent file to extract metadata
        
        Args:
            file_path: Path to agent file
            
        Returns:
            DiscoveredAgent or None if analysis fails
        """
        # Read file content
        content = file_path.read_text(encoding='utf-8')
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        
        # Find agent class (ends with "Agent")
        agent_class_name = None
        agent_class_node = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Skip base classes
                if node.name in ["BaseAgent", "FengShuiAgent"]:
                    continue
                agent_class_name = node.name
                agent_class_node = node
                break
        
        if not agent_class_name:
            return None
        
        # Extract detectors (methods starting with _detect_)
        detectors = []
        for node in ast.walk(agent_class_node):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_detect_"):
                    detectors.append(node.name)
        
        # Extract purpose from class docstring
        purpose_hint = ""
        if ast.get_docstring(agent_class_node):
            docstring = ast.get_docstring(agent_class_node)
            # Take first line of docstring as purpose hint
            purpose_hint = docstring.split('\n')[0].strip()
        
        # Use absolute path, then make relative
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # Fallback: just use the file name
            relative_path = file_path
        
        return DiscoveredAgent(
            name=agent_class_name,
            file_path=str(relative_path).replace('\\', '/'),  # Normalize to forward slashes
            class_obj=None,  # Don't import to avoid dependencies
            detectors=sorted(detectors),
            purpose_hint=purpose_hint
        )
    
    def check_registry_sync(self, registered_agents: List[str]) -> Dict[str, any]:
        """
        Check if registry is in sync with actual agents
        
        Args:
            registered_agents: List of agent names in registry
            
        Returns:
            {
                "in_sync": bool,
                "missing_in_registry": List[str],
                "missing_in_codebase": List[str],
                "discovered": List[DiscoveredAgent]
            }
        """
        discovered = self.discover_agents()
        discovered_names = {agent.name for agent in discovered}
        registered_set = set(registered_agents)
        
        missing_in_registry = discovered_names - registered_set
        missing_in_codebase = registered_set - discovered_names
        
        return {
            "in_sync": len(missing_in_registry) == 0 and len(missing_in_codebase) == 0,
            "missing_in_registry": sorted(missing_in_registry),
            "missing_in_codebase": sorted(missing_in_codebase),
            "discovered": discovered
        }
    
    def generate_registry_entry(self, agent: DiscoveredAgent) -> str:
        """
        Generate Python code for registry entry
        
        Args:
            agent: DiscoveredAgent object
            
        Returns:
            Python code string for AGENT_PURPOSES entry
        """
        # Generate basic template
        template = f'''
AgentPurpose(
    name="{agent.name}",
    purpose="[TODO: Describe {agent.name} purpose]",
    scope=[
        "[TODO: Add scope items]",
    ],
    examples=[
        "[TODO: Add example enhancements]",
    ],
    current_detectors={agent.detectors},
    fits_criteria=[
        "[TODO: Add fit criteria]",
    ],
    does_not_fit=[
        "[TODO: Add exclusion criteria]",
    ]
)
'''
        return template.strip()
    
    def suggest_updates(self) -> str:
        """
        Generate suggestions for registry updates
        
        Returns:
            Human-readable report
        """
        from .agent_registry import list_all_agents
        
        sync_status = self.check_registry_sync(list_all_agents())
        
        report = []
        report.append("=" * 60)
        report.append("Shi Fu Agent Registry Sync Check")
        report.append("=" * 60)
        report.append("")
        
        if sync_status['in_sync']:
            report.append("✅ Registry is in sync with codebase!")
            report.append(f"   {len(sync_status['discovered'])} agents discovered and registered.")
        else:
            report.append("⚠️ Registry is OUT OF SYNC!")
            report.append("")
            
            if sync_status['missing_in_registry']:
                report.append("📝 NEW AGENTS FOUND (not in registry):")
                for agent_name in sync_status['missing_in_registry']:
                    # Find the agent details
                    agent = next(
                        (a for a in sync_status['discovered'] if a.name == agent_name),
                        None
                    )
                    if agent:
                        report.append(f"   • {agent_name}")
                        report.append(f"     File: {agent.file_path}")
                        report.append(f"     Detectors: {len(agent.detectors)}")
                        if agent.purpose_hint:
                            report.append(f"     Hint: {agent.purpose_hint}")
                report.append("")
                report.append("💡 ACTION REQUIRED:")
                report.append("   Add these agents to tools/shifu/meta/agent_registry.py")
                report.append("   Use generate_registry_entry() for templates")
            
            if sync_status['missing_in_codebase']:
                report.append("")
                report.append("⚠️ AGENTS IN REGISTRY BUT NOT IN CODEBASE:")
                for agent_name in sync_status['missing_in_codebase']:
                    report.append(f"   • {agent_name} (possibly deleted or renamed)")
                report.append("")
                report.append("💡 ACTION REQUIRED:")
                report.append("   Remove these agents from agent_registry.py")
        
        report.append("")
        report.append("=" * 60)
        report.append("Discovered Agents:")
        report.append("=" * 60)
        for agent in sync_status['discovered']:
            report.append(f"\n{agent.name}:")
            report.append(f"  File: {agent.file_path}")
            report.append(f"  Detectors: {len(agent.detectors)}")
            if agent.detectors:
                report.append(f"  Methods: {', '.join(agent.detectors[:3])}" + 
                            (f" + {len(agent.detectors)-3} more" if len(agent.detectors) > 3 else ""))
        
        return '\n'.join(report)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI interface for agent auto-discovery"""
    print()
    print("=" * 60)
    print("Shi Fu Agent Auto-Discovery")
    print("=" * 60)
    print()
    
    discovery = AgentAutoDiscovery()
    
    # Check sync status
    print(discovery.suggest_updates())
    
    # Generate templates for new agents (if any)
    from .agent_registry import list_all_agents
    sync_status = discovery.check_registry_sync(list_all_agents())
    
    if sync_status['missing_in_registry']:
        print()
        print("=" * 60)
        print("Registry Entry Templates")
        print("=" * 60)
        
        for agent_name in sync_status['missing_in_registry']:
            agent = next(
                (a for a in sync_status['discovered'] if a.name == agent_name),
                None
            )
            if agent:
                print(f"\n# {agent.name}")
                print(f"# File: {agent.file_path}")
                print(discovery.generate_registry_entry(agent))


if __name__ == "__main__":
    main()