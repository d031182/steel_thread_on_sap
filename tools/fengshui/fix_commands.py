#!/usr/bin/env python3
"""
Feng Shui Fix Commands - Command Pattern
=========================================

Encapsulates architecture fixes as executable commands.

GoF Pattern: Command
- Encapsulates fix operations as objects
- Supports undo/redo
- Enables automated fixes (like Gu Wu for tests!)
- Queued execution with validation
"""
import sys
import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class CommandResult:
    """Result of executing a command"""
    success: bool
    message: str
    changes_made: List[str]
    backup_path: Optional[Path] = None


class ArchitectureCommand(ABC):
    """
    Abstract command for architecture fixes (Command pattern)
    
    Each command:
    - Encapsulates a specific fix operation
    - Can be executed, undone, validated
    - Tracks changes for rollback
    """
    
    def __init__(self, target: Path):
        self.target = target
        self.executed = False
        self.backup_path: Optional[Path] = None
        self.timestamp = datetime.now()
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """
        Execute the fix command
        
        Returns:
            CommandResult with success status and details
        """
        pass
    
    @abstractmethod
    def undo(self) -> CommandResult:
        """
        Undo the fix command
        
        Returns:
            CommandResult with success status
        """
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """
        Check if command can be executed safely
        
        Returns:
            True if prerequisites are met
        """
        pass
    
    def _create_backup(self) -> Optional[Path]:
        """
        Create backup before making changes
        
        Returns:
            Path to backup, or None if backup failed
        """
        if not self.target.exists():
            return None
        
        backup_dir = Path('backups/fengshui')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.timestamp.strftime('%Y%m%d_%H%M%S')
        backup_name = f"{self.target.name}.{timestamp}.bak"
        backup_path = backup_dir / backup_name
        
        try:
            if self.target.is_file():
                shutil.copy2(self.target, backup_path)
            else:
                shutil.copytree(self.target, backup_path)
            return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return None


class CreateModuleJsonCommand(ArchitectureCommand):
    """
    Command to create missing module.json file
    
    Fixes: CRITICAL - module.json not found
    """
    
    def __init__(self, module_path: Path):
        super().__init__(module_path)
        self.module_name = module_path.name
    
    def can_execute(self) -> bool:
        """Check if module directory exists and module.json is missing"""
        return (
            self.target.is_dir() and
            not (self.target / 'module.json').exists()
        )
    
    def execute(self) -> CommandResult:
        """Create module.json with default configuration"""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="Cannot create module.json - prerequisites not met",
                changes_made=[]
            )
        
        module_json_path = self.target / 'module.json'
        
        # Create default configuration
        config = {
            "name": self.module_name,
            "version": "1.0.0",
            "description": f"{self.module_name.replace('_', ' ').title()} module",
            "enabled": True,
            "backend": {
                "blueprint": f"modules.{self.module_name}.backend:bp"
            }
        }
        
        try:
            with open(module_json_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.executed = True
            return CommandResult(
                success=True,
                message=f"Created module.json for {self.module_name}",
                changes_made=[str(module_json_path)]
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to create module.json: {str(e)}",
                changes_made=[]
            )
    
    def undo(self) -> CommandResult:
        """Remove created module.json"""
        if not self.executed:
            return CommandResult(
                success=False,
                message="Command was not executed, nothing to undo",
                changes_made=[]
            )
        
        module_json_path = self.target / 'module.json'
        
        try:
            if module_json_path.exists():
                module_json_path.unlink()
            
            return CommandResult(
                success=True,
                message=f"Removed module.json from {self.module_name}",
                changes_made=[str(module_json_path)]
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to undo: {str(e)}",
                changes_made=[]
            )


class CreateModuleReadmeCommand(ArchitectureCommand):
    """
    Command to create missing README.md file
    
    Fixes: MEDIUM - README.md not found
    """
    
    def __init__(self, module_path: Path):
        super().__init__(module_path)
        self.module_name = module_path.name
    
    def can_execute(self) -> bool:
        """Check if module directory exists and README is missing"""
        return (
            self.target.is_dir() and
            not (self.target / 'README.md').exists()
        )
    
    def execute(self) -> CommandResult:
        """Create README.md with template"""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="Cannot create README.md - prerequisites not met",
                changes_made=[]
            )
        
        readme_path = self.target / 'README.md'
        
        # Create template README
        content = f"""# {self.module_name.replace('_', ' ').title()} Module

## Purpose
[Describe the module's purpose and responsibilities]

## Features
- Feature 1
- Feature 2
- Feature 3

## API Endpoints
### GET /api/{self.module_name}/...
[Describe endpoint]

## Integration
```python
from modules.{self.module_name}.backend import service

# Example usage
result = service.do_something()
```

## Configuration
See `module.json` for configuration options.

## Testing
```bash
pytest tests/unit/modules/{self.module_name}/
```

## Dependencies
- Core: [list core dependencies]
- External: [list external packages]
"""
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.executed = True
            return CommandResult(
                success=True,
                message=f"Created README.md for {self.module_name}",
                changes_made=[str(readme_path)]
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to create README.md: {str(e)}",
                changes_made=[]
            )
    
    def undo(self) -> CommandResult:
        """Remove created README.md"""
        if not self.executed:
            return CommandResult(
                success=False,
                message="Command was not executed, nothing to undo",
                changes_made=[]
            )
        
        readme_path = self.target / 'README.md'
        
        try:
            if readme_path.exists():
                readme_path.unlink()
            
            return CommandResult(
                success=True,
                message=f"Removed README.md from {self.module_name}",
                changes_made=[str(readme_path)]
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to undo: {str(e)}",
                changes_made=[]
            )


class AddBlueprintConfigCommand(ArchitectureCommand):
    """
    Command to add missing backend.blueprint to module.json
    
    Fixes: HIGH - Blueprint Config failed
    """
    
    def __init__(self, module_path: Path):
        super().__init__(module_path)
        self.module_name = module_path.name
        self.config_path = module_path / 'module.json'
    
    def can_execute(self) -> bool:
        """Check if module.json exists and is missing blueprint config"""
        if not self.config_path.exists():
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Missing backend section or backend.blueprint
            return (
                'backend' not in config or
                'blueprint' not in config.get('backend', {})
            )
        except:
            return False
    
    def execute(self) -> CommandResult:
        """Add backend.blueprint to module.json"""
        if not self.can_execute():
            return CommandResult(
                success=False,
                message="Cannot add blueprint config - prerequisites not met",
                changes_made=[]
            )
        
        # Create backup
        self.backup_path = self._create_backup()
        
        try:
            # Load config
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Add backend.blueprint
            if 'backend' not in config:
                config['backend'] = {}
            
            config['backend']['blueprint'] = f"modules.{self.module_name}.backend:bp"
            
            # Save
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.executed = True
            return CommandResult(
                success=True,
                message=f"Added backend.blueprint to {self.module_name}",
                changes_made=[str(self.config_path)],
                backup_path=self.backup_path
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to add blueprint config: {str(e)}",
                changes_made=[]
            )
    
    def undo(self) -> CommandResult:
        """Restore from backup"""
        if not self.executed or not self.backup_path:
            return CommandResult(
                success=False,
                message="Nothing to undo",
                changes_made=[]
            )
        
        try:
            shutil.copy2(self.backup_path, self.config_path)
            return CommandResult(
                success=True,
                message=f"Restored {self.module_name}/module.json from backup",
                changes_made=[str(self.config_path)]
            )
        
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to undo: {str(e)}",
                changes_made=[]
            )


class CommandInvoker:
    """
    Invoker for executing commands with history tracking
    
    Features:
    - Execute commands in order
    - Track execution history
    - Support batch undo
    - Validation before execution
    """
    
    def __init__(self):
        self.history: List[ArchitectureCommand] = []
        self.failed_commands: List[tuple[ArchitectureCommand, str]] = []
    
    def execute_command(self, command: ArchitectureCommand) -> CommandResult:
        """
        Execute a single command
        
        Args:
            command: Command to execute
            
        Returns:
            CommandResult with execution details
        """
        # Check prerequisites
        if not command.can_execute():
            result = CommandResult(
                success=False,
                message=f"Prerequisites not met for {command.__class__.__name__}",
                changes_made=[]
            )
            self.failed_commands.append((command, result.message))
            return result
        
        # Execute
        result = command.execute()
        
        # Track in history if successful
        if result.success:
            self.history.append(command)
        else:
            self.failed_commands.append((command, result.message))
        
        return result
    
    def execute_batch(self, commands: List[ArchitectureCommand]) -> Dict[str, Any]:
        """
        Execute multiple commands
        
        Args:
            commands: List of commands to execute
            
        Returns:
            Summary of batch execution
        """
        results = []
        success_count = 0
        
        for command in commands:
            result = self.execute_command(command)
            results.append(result)
            if result.success:
                success_count += 1
        
        return {
            'total': len(commands),
            'succeeded': success_count,
            'failed': len(commands) - success_count,
            'results': results
        }
    
    def undo_last(self) -> CommandResult:
        """Undo the last executed command"""
        if not self.history:
            return CommandResult(
                success=False,
                message="No commands to undo",
                changes_made=[]
            )
        
        command = self.history.pop()
        return command.undo()
    
    def undo_all(self) -> List[CommandResult]:
        """Undo all executed commands (in reverse order)"""
        results = []
        while self.history:
            result = self.undo_last()
            results.append(result)
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            'executed': len(self.history),
            'failed': len(self.failed_commands),
            'can_undo': len(self.history) > 0
        }


# ============================================================================
# COMMAND FACTORY
# ============================================================================

class CommandFactory:
    """
    Factory for creating fix commands based on findings
    
    Maps finding types to appropriate command implementations
    """
    
    @staticmethod
    def create_commands_for_module(module_path: Path, findings: List[str]) -> List[ArchitectureCommand]:
        """
        Create commands to fix findings in a module
        
        Args:
            module_path: Path to module directory
            findings: List of finding descriptions
            
        Returns:
            List of commands to fix the findings
        """
        commands = []
        
        for finding in findings:
            # Missing module.json
            if 'module.json not found' in finding:
                commands.append(CreateModuleJsonCommand(module_path))
            
            # Missing README
            elif 'README.md not found' in finding:
                commands.append(CreateModuleReadmeCommand(module_path))
            
            # Missing blueprint config
            elif 'Blueprint Config failed' in finding:
                commands.append(AddBlueprintConfigCommand(module_path))
        
        return commands


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_command_pattern():
    """
    Demonstrate Command pattern with automated fixes
    """
    print("\n" + "="*80)
    print("FENG SHUI COMMAND PATTERN DEMONSTRATION")
    print("="*80 + "\n")
    
    # Example: Fix ai_assistant module (missing module.json)
    ai_assistant_path = Path('modules/ai_assistant')
    
    if ai_assistant_path.exists():
        print("Creating fix commands for ai_assistant module...")
        
        # Create commands
        commands = [
            CreateModuleJsonCommand(ai_assistant_path),
            CreateModuleReadmeCommand(ai_assistant_path)
        ]
        
        # Create invoker
        invoker = CommandInvoker()
        
        # Execute commands
        print("\nExecuting commands:")
        print("-" * 80)
        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] {cmd.__class__.__name__}...")
            
            if cmd.can_execute():
                result = invoker.execute_command(cmd)
                if result.success:
                    print(f"  ✓ {result.message}")
                    for change in result.changes_made:
                        print(f"    - Created: {change}")
                else:
                    print(f"  ✗ {result.message}")
            else:
                print(f"  ⊘ Skipped (prerequisites not met)")
        
        # Summary
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        summary = invoker.get_summary()
        print(f"  Executed: {summary['executed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Can Undo: {'Yes' if summary['can_undo'] else 'No'}")
        
        # Demonstrate undo
        if summary['can_undo']:
            print("\n" + "="*80)
            print("UNDO DEMONSTRATION (commented out - uncomment to test)")
            print("="*80)
            print("  # Uncomment to undo all changes:")
            print("  # undo_results = invoker.undo_all()")
            print("  # for result in undo_results:")
            print("  #     print(f'  {result.message}')")
    
    else:
        print(f"Module not found: {ai_assistant_path}")
        print("Demonstration skipped.")


if __name__ == '__main__':
    demonstrate_command_pattern()