"""
Resolver Registry - Central registry for all Gu Wu resolvers

Manages discovery and dispatch of resolvers based on finding types.
"""

from typing import List, Dict, Type, Optional
import logging
from pathlib import Path

from .base_resolver import BaseResolver, ResolutionResult
from .file_organization_resolver import FileOrganizationResolver


class ResolverRegistry:
    """
    Central registry for managing resolvers
    
    Responsibilities:
    - Register resolvers by category
    - Find appropriate resolver for a finding
    - Dispatch findings to correct resolvers
    """
    
    def __init__(self):
        """Initialize registry and register known resolvers"""
        self._resolvers: Dict[str, BaseResolver] = {}
        self.logger = logging.getLogger("guwu.resolvers.registry")
        
        # Register known resolvers
        self._register_default_resolvers()
    
    def _register_default_resolvers(self):
        """Register all known resolvers"""
        # File Organization Resolver
        file_org_resolver = FileOrganizationResolver()
        for category in file_org_resolver.get_supported_categories():
            self.register(category, file_org_resolver)
        
        self.logger.info(f"Registered {len(set(self._resolvers.values()))} resolver(s) for {len(self._resolvers)} categories")
    
    def register(self, category: str, resolver: BaseResolver):
        """
        Register a resolver for a category
        
        Args:
            category: Finding category (e.g., "Root Directory Clutter", "Misplaced Script")
            resolver: Resolver instance
        """
        self._resolvers[category] = resolver
        self.logger.debug(f"Registered resolver for category: {category}")
    
    def get_resolver(self, category: str) -> Optional[BaseResolver]:
        """
        Get resolver for a category
        
        Args:
            category: Finding category
            
        Returns:
            Resolver instance or None if not found
        """
        return self._resolvers.get(category)
    
    def resolve_findings(self, findings: List, category: str, 
                         dry_run: bool = True, interactive: bool = False) -> ResolutionResult:
        """
        Resolve findings using appropriate resolver
        
        Args:
            findings: List of findings
            category: Finding category
            dry_run: If True, simulate actions only
            interactive: If True, prompt for confirmations
            
        Returns:
            ResolutionResult
        """
        resolver = self.get_resolver(category)
        
        if not resolver:
            self.logger.warning(f"No resolver found for category: {category}")
            result = ResolutionResult(status="skipped")
            result.add_warning(f"No resolver registered for category: {category}")
            return result
        
        self.logger.info(f"Resolving {len(findings)} findings with {resolver.name} (dry_run={dry_run})")
        return resolver.resolve_findings(findings, dry_run=dry_run, interactive=interactive)
    
    def list_resolvers(self) -> List[str]:
        """List all registered resolver categories"""
        return list(self._resolvers.keys())
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered resolvers"""
        capabilities = {}
        for resolver in set(self._resolvers.values()):
            capabilities[resolver.name] = resolver.get_capabilities()
        return capabilities


# Global registry instance
_registry = ResolverRegistry()


def get_registry() -> ResolverRegistry:
    """Get global resolver registry"""
    return _registry