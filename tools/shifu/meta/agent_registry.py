"""
Feng Shui Agent Purpose Registry

Documents the purpose, scope, and capabilities of all 6 Feng Shui agents.
Used by Shi Fu Phase 6 to route enhancement requests to the correct agent.

Philosophy:
"Each agent has a defined purpose. New capabilities must fit that purpose."
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentPurpose:
    """Defines an agent's purpose and scope"""
    name: str
    purpose: str
    scope: List[str]
    examples: List[str]
    current_detectors: List[str]
    fits_criteria: List[str]
    does_not_fit: List[str]


# ============================================================================
# THE 6 FENG SHUI AGENTS - COMPLETE PURPOSE DOCUMENTATION
# ============================================================================

AGENT_PURPOSES: Dict[str, AgentPurpose] = {
    
    # ========================================================================
    # 1. ARCHITECT AGENT - Architecture Patterns & Design Principles
    # ========================================================================
    "ArchitectAgent": AgentPurpose(
        name="ArchitectAgent",
        purpose="Architecture patterns & design principles",
        scope=[
            "SOLID principles (SRP, OCP, LSP, ISP, DIP)",
            "Dependency Injection violations",
            "GoF design pattern violations",
            "DDD pattern compliance (Repository, UoW, Service Layer, Facade)",
            "Backend structure validation",
            "Anti-pattern detection (Service Locator, Stale Reference)",
        ],
        examples=[
            "DI violations (.connection, .service, .db_path access)",
            "Service Locator anti-pattern (Flask config access)",
            "Stale Reference anti-pattern (cached container.get())",
            "Repository Pattern violations (direct DB access)",
            "Unit of Work violations (manual commit/rollback)",
            "Service Layer violations (business logic in routes)",
            "Facade Pattern violations (API → Repository directly)",
            "Large classes (>500 LOC, SRP violation)",
        ],
        current_detectors=[
            "_detect_di_violations (static)",
            "_detect_di_violations_runtime (from logs)",
            "_detect_solid_violations",
            "_detect_large_classes",
            "_detect_repository_violations",
            "_detect_unit_of_work_violations",
            "_detect_service_layer_violations",
            "_detect_facade_pattern_violations",
            "_detect_backend_structure_violations",
            "_detect_service_locator_violations",
            "_detect_stale_references",
        ],
        fits_criteria=[
            "Related to code design patterns (GoF, DDD)",
            "Violates SOLID principles",
            "Architecture anti-pattern",
            "Dependency management issue",
            "Module structure problem (backend/, facade/, repositories/)",
            "Coupling/cohesion concern",
        ],
        does_not_fit=[
            "Security vulnerability → SecurityAgent",
            "Performance issue → PerformanceAgent",
            "UX/UI concern → UXArchitectAgent",
            "File organization → FileOrganizationAgent",
            "Documentation → DocumentationAgent",
        ]
    ),
    
    # ========================================================================
    # 2. SECURITY AGENT - Security Vulnerabilities & Compliance
    # ========================================================================
    "SecurityAgent": AgentPurpose(
        name="SecurityAgent",
        purpose="Security vulnerabilities & compliance",
        scope=[
            "SQL injection vulnerabilities",
            "Hardcoded secrets/credentials",
            "Authentication/authorization issues",
            "XSS vulnerabilities",
            "CSRF protection",
            "Input validation",
            "Insecure connections (HTTP vs HTTPS)",
            "Weak cryptography",
        ],
        examples=[
            "SQL injection (string concatenation in queries)",
            "Hardcoded passwords/API keys",
            "Missing authentication decorators",
            "XSS via unescaped user input",
            "Missing CSRF tokens",
            "Weak password hashing (MD5, SHA1)",
            "Insecure HTTP endpoints",
            "Exposed sensitive data in logs",
        ],
        current_detectors=[
            "_detect_sql_injection",
            "_detect_hardcoded_secrets",
            "_detect_auth_issues",
            "_detect_xss_vulnerabilities",
            # Future: _detect_weak_crypto, _detect_insecure_connections
        ],
        fits_criteria=[
            "Security vulnerability",
            "Authentication/authorization concern",
            "Data exposure risk",
            "Injection attack vector",
            "Cryptographic weakness",
            "Compliance violation (OWASP, GDPR)",
        ],
        does_not_fit=[
            "Architecture pattern → ArchitectAgent",
            "Performance issue → PerformanceAgent",
            "UX concern → UXArchitectAgent",
            "File placement → FileOrganizationAgent",
            "Missing docs → DocumentationAgent",
        ]
    ),
    
    # ========================================================================
    # 3. UX ARCHITECT AGENT - SAP Fiori/SAPUI5 Compliance & UX Patterns
    # ========================================================================
    "UXArchitectAgent": AgentPurpose(
        name="UXArchitectAgent",
        purpose="SAP Fiori/SAPUI5 compliance & UX patterns",
        scope=[
            "SAP Fiori design guidelines",
            "SAPUI5 control usage (standard vs custom)",
            "Responsive design compliance",
            "Accessibility (a11y) standards",
            "UX consistency patterns",
            "CSS layout standards (use built-in properties)",
            "Navigation patterns",
        ],
        examples=[
            "CSS !important for layout (use built-in properties)",
            "CustomListItem vs InputListItem (prefer standard)",
            "Missing responsive design attributes",
            "Accessibility labels missing (a11y)",
            "Inconsistent button styles",
            "Direct CSS for sizing (use width='100%' instead)",
            "Non-standard control patterns",
        ],
        current_detectors=[
            "_detect_css_layout_hacks",
            "_detect_custom_controls",
            "_detect_non_responsive",
            # Future: _detect_a11y_violations, _detect_ux_inconsistencies
        ],
        fits_criteria=[
            "SAP Fiori/SAPUI5 concern",
            "Frontend UX pattern",
            "Accessibility issue",
            "Responsive design",
            "UI consistency",
            "CSS/styling standards",
        ],
        does_not_fit=[
            "Backend architecture → ArchitectAgent",
            "Security issue → SecurityAgent",
            "Backend performance → PerformanceAgent",
            "File organization → FileOrganizationAgent",
            "API documentation → DocumentationAgent",
        ]
    ),
    
    # ========================================================================
    # 4. PERFORMANCE AGENT - Performance Optimization & Efficiency
    # ========================================================================
    "PerformanceAgent": AgentPurpose(
        name="PerformanceAgent",
        purpose="Performance optimization & efficiency",
        scope=[
            "N+1 query problems",
            "Nested loop inefficiencies",
            "Missing database indices",
            "Memory leaks",
            "Caching opportunities",
            "Unbuffered I/O",
            "Missing pagination",
            "Slow algorithms",
        ],
        examples=[
            "N+1 queries (loop with DB query inside)",
            "Nested loops with O(n²) complexity",
            "Missing database indices on foreign keys",
            "Large file I/O without buffering",
            "Missing pagination for large datasets",
            "Inefficient sorting/searching algorithms",
            "Missing caching for expensive operations",
        ],
        current_detectors=[
            "_detect_n_plus_one_queries",
            "_detect_nested_loops",
            "_detect_missing_indices",
            # Future: _detect_unbuffered_io, _detect_missing_pagination
        ],
        fits_criteria=[
            "Performance bottleneck",
            "Scalability concern",
            "Resource inefficiency",
            "Algorithm complexity issue",
            "Database query optimization",
            "Memory/CPU intensive operation",
        ],
        does_not_fit=[
            "Architecture pattern → ArchitectAgent",
            "Security issue → SecurityAgent",
            "UX concern → UXArchitectAgent",
            "File placement → FileOrganizationAgent",
            "Missing docs → DocumentationAgent",
        ]
    ),
    
    # ========================================================================
    # 5. FILE ORGANIZATION AGENT - File Structure & Organization Standards
    # ========================================================================
    "FileOrganizationAgent": AgentPurpose(
        name="FileOrganizationAgent",
        purpose="File structure & organization standards",
        scope=[
            "Module directory structure",
            "File naming conventions",
            "Obsolete/unused files",
            "Misplaced files (wrong directory)",
            "Empty/obsolete directories",  # ⭐ YOUR CASE
            "Orphaned configuration files",
            "Stale migration scripts",
            "Duplicate files",
        ],
        examples=[
            "Tests in wrong directory (should be in tests/unit/modules/[name]/)",
            "Orphaned configuration files (no references)",
            "Empty directories (only __pycache__, .DS_Store, Thumbs.db)",  # ⭐
            "Stale migration scripts (not used)",
            "Duplicate files (same content, different locations)",
            "Missing __init__.py in Python packages",
            "Misnamed files (violate conventions)",
        ],
        current_detectors=[
            "_detect_misplaced_tests",
            "_detect_obsolete_files",
            "_detect_naming_violations",
            # Future: _detect_empty_directories ⭐, _detect_duplicate_files
        ],
        fits_criteria=[
            "File/directory organization",
            "Naming convention violation",
            "Obsolete/unused content",
            "File placement issue",
            "Directory structure concern",
            "Project organization standard",
        ],
        does_not_fit=[
            "Code architecture → ArchitectAgent",
            "Security issue → SecurityAgent",
            "UX concern → UXArchitectAgent",
            "Performance issue → PerformanceAgent",
            "Code documentation → DocumentationAgent (file org is about placement, not content)",
        ]
    ),
    
    # ========================================================================
    # 6. DOCUMENTATION AGENT - Documentation Quality & Completeness
    # ========================================================================
    "DocumentationAgent": AgentPurpose(
        name="DocumentationAgent",
        purpose="Documentation quality & completeness",
        scope=[
            "README.md presence/quality",
            "Docstring coverage",
            "API documentation",
            "Inline comments",
            "Knowledge vault links",
            "Outdated documentation",
            "Broken wikilinks",
            "Missing examples",
        ],
        examples=[
            "Missing README.md in modules",
            "Functions without docstrings",
            "Missing API documentation",
            "Complex code without comments",
            "Outdated README (references removed features)",
            "Broken wikilinks ([[Document Name]] not found)",
            "Missing usage examples",
        ],
        current_detectors=[
            "_detect_missing_readmes",
            "_detect_missing_docstrings",
            "_detect_poor_comments",
            # Future: _detect_stale_docs, _detect_broken_links
        ],
        fits_criteria=[
            "Documentation quality",
            "Missing documentation",
            "Outdated documentation",
            "Broken references",
            "Comment quality",
            "Example completeness",
        ],
        does_not_fit=[
            "Code architecture → ArchitectAgent",
            "Security issue → SecurityAgent",
            "UX concern → UXArchitectAgent",
            "Performance issue → PerformanceAgent",
            "File organization → FileOrganizationAgent (unless doc in wrong place)",
        ]
    ),
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_agent_for_issue(issue_description: str) -> Optional[str]:
    """
    Analyze issue description and determine which agent should handle it
    
    Uses keyword matching and scope analysis to route issues to correct agent.
    
    Args:
        issue_description: Description of the issue (e.g., "Empty /app folder")
        
    Returns:
        Agent name (e.g., "FileOrganizationAgent") or None if no match
        
    Example:
        >>> get_agent_for_issue("Empty /app folder with only __pycache__")
        "FileOrganizationAgent"
        
        >>> get_agent_for_issue("SQL injection in query")
        "SecurityAgent"
    """
    issue_lower = issue_description.lower()
    
    # Keyword mapping (order matters - check specific before general)
    keyword_map = {
        # Security keywords (check first - highest priority)
        "SecurityAgent": [
            "sql injection", "hardcoded password", "hardcoded secret",
            "authentication", "authorization", "xss", "csrf",
            "security vulnerability", "exposed credential"
        ],
        
        # FileOrganization keywords
        "FileOrganizationAgent": [
            "empty directory", "empty folder", "__pycache__", "obsolete directory",
            "misplaced file", "wrong directory", "file organization",
            "orphaned file", "duplicate file", "naming convention"
        ],
        
        # UXArchitect keywords
        "UXArchitectAgent": [
            "sap fiori", "sapui5", "css layout", "!important",
            "custom control", "responsive design", "accessibility",
            "ux pattern", "ui consistency", "frontend ux"
        ],
        
        # Performance keywords
        "PerformanceAgent": [
            "n+1 query", "nested loop", "performance bottleneck",
            "slow query", "missing index", "caching opportunity",
            "memory leak", "unbuffered io", "pagination"
        ],
        
        # Documentation keywords
        "DocumentationAgent": [
            "missing readme", "missing docstring", "outdated documentation",
            "broken link", "wikilink", "missing example",
            "poor comment", "api documentation"
        ],
        
        # Architecture keywords (most general - check last)
        "ArchitectAgent": [
            "di violation", "dependency injection", "solid principle",
            "design pattern", "repository pattern", "unit of work",
            "service layer", "facade pattern", "service locator",
            "stale reference", "architecture", "coupling", "cohesion"
        ],
    }
    
    # Check each agent's keywords
    for agent_name, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in issue_lower:
                return agent_name
    
    # No match found
    return None


def get_agent_purpose(agent_name: str) -> Optional[AgentPurpose]:
    """
    Get complete purpose documentation for an agent
    
    Args:
        agent_name: Name of the agent (e.g., "ArchitectAgent")
        
    Returns:
        AgentPurpose object or None if agent not found
    """
    return AGENT_PURPOSES.get(agent_name)


def list_all_agents() -> List[str]:
    """Get list of all agent names"""
    return list(AGENT_PURPOSES.keys())


def validate_enhancement(agent_name: str, enhancement_description: str) -> Dict[str, any]:
    """
    Validate if an enhancement fits an agent's purpose
    
    Args:
        agent_name: Target agent (e.g., "FileOrganizationAgent")
        enhancement_description: What to enhance (e.g., "Detect empty directories")
        
    Returns:
        {
            "fits": bool,
            "confidence": float (0.0-1.0),
            "reasoning": str,
            "recommendations": List[str]
        }
    """
    agent = AGENT_PURPOSES.get(agent_name)
    if not agent:
        return {
            "fits": False,
            "confidence": 0.0,
            "reasoning": f"Agent '{agent_name}' not found",
            "recommendations": []
        }
    
    desc_lower = enhancement_description.lower()
    
    # Check if description matches agent's scope (weighted higher)
    scope_matches = sum(1 for scope_item in agent.scope 
                       if any(word in desc_lower for word in scope_item.lower().split()))
    
    # Check if description matches agent's examples (weighted higher)
    example_matches = sum(1 for example in agent.examples
                         if any(word in desc_lower for word in example.lower().split()))
    
    # Check if description matches fits_criteria
    criteria_matches = sum(1 for criterion in agent.fits_criteria
                          if any(word in desc_lower for word in criterion.lower().split()))
    
    # Calculate confidence with proper weighting
    # Examples are most specific (weight 3x), then scope (2x), then criteria (1x)
    weighted_score = (example_matches * 3) + (scope_matches * 2) + criteria_matches
    max_weighted = (len(agent.examples) * 3) + (len(agent.scope) * 2) + len(agent.fits_criteria)
    
    confidence = min(weighted_score / max(max_weighted * 0.15, 1), 1.0)  # 15% threshold
    
    fits = confidence >= 0.15  # Lower threshold due to weighting
    
    # Total matches for reasoning
    total_matches = scope_matches + example_matches + criteria_matches
    
    # Generate reasoning
    if fits:
        reasoning = (
            f"Enhancement fits {agent_name}'s purpose: '{agent.purpose}'. "
            f"Matches {total_matches} scope/example/criteria items "
            f"(weighted confidence: {confidence:.2f})."
        )
    else:
        reasoning = (
            f"Enhancement does NOT fit {agent_name}'s purpose. "
            f"Only {total_matches} matches found "
            f"(weighted confidence: {confidence:.2f} < 0.15 threshold). "
            f"Consider: {', '.join(agent.does_not_fit)}"
        )
    
    # Generate recommendations
    recommendations = []
    if fits:
        recommendations.append(f"Add detector to {agent_name}")
        recommendations.append(f"Check if similar detectors already exist: {', '.join(agent.current_detectors[:3])}")
        recommendations.append(f"Ensure fits scope: {agent.scope[0]}")
    else:
        # Suggest alternative agents
        for alt_agent_name, alt_agent in AGENT_PURPOSES.items():
            if alt_agent_name != agent_name:
                alt_match = sum(1 for scope_item in alt_agent.scope
                              if any(word in desc_lower for word in scope_item.lower().split()))
                if alt_match > 0:
                    recommendations.append(f"Consider {alt_agent_name} instead (better fit)")
    
    return {
        "fits": fits,
        "confidence": confidence,
        "reasoning": reasoning,
        "recommendations": recommendations
    }


# ============================================================================
# AGENT CAPABILITY MATRIX (For Quick Reference)
# ============================================================================

AGENT_CAPABILITY_MATRIX = {
    "DI violations": "ArchitectAgent",
    "SQL injection": "SecurityAgent",
    "CSS !important": "UXArchitectAgent",
    "N+1 queries": "PerformanceAgent",
    "Empty directories": "FileOrganizationAgent",
    "Missing docstrings": "DocumentationAgent",
    
    "SOLID violations": "ArchitectAgent",
    "Hardcoded secrets": "SecurityAgent",
    "Non-responsive UI": "UXArchitectAgent",
    "Nested loops": "PerformanceAgent",
    "Misplaced tests": "FileOrganizationAgent",
    "Outdated README": "DocumentationAgent",
    
    "Service Locator": "ArchitectAgent",
    "XSS vulnerability": "SecurityAgent",
    "Accessibility": "UXArchitectAgent",
    "Missing cache": "PerformanceAgent",
    "Duplicate files": "FileOrganizationAgent",
    "Broken wikilinks": "DocumentationAgent",
}


def get_quick_routing(issue_type: str) -> Optional[str]:
    """
    Quick routing based on issue type
    
    Args:
        issue_type: Type of issue (e.g., "DI violations", "Empty directories")
        
    Returns:
        Agent name or None
    """
    return AGENT_CAPABILITY_MATRIX.get(issue_type)


# ============================================================================
# DEMO/USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Your case (empty /app folder)
    print("=" * 60)
    print("Example 1: Empty /app folder")
    print("=" * 60)
    
    agent = get_agent_for_issue("Empty /app folder with only __pycache__")
    print(f"Routed to: {agent}")
    
    validation = validate_enhancement(agent, "Detect empty directories")
    print(f"Fits: {validation['fits']} (confidence: {validation['confidence']:.2f})")
    print(f"Reasoning: {validation['reasoning']}")
    print()
    
    # Example 2: SQL injection
    print("=" * 60)
    print("Example 2: SQL injection vulnerability")
    print("=" * 60)
    
    agent = get_agent_for_issue("SQL injection in data products query")
    print(f"Routed to: {agent}")
    
    validation = validate_enhancement(agent, "Detect parameterized query violations")
    print(f"Fits: {validation['fits']} (confidence: {validation['confidence']:.2f})")
    print()
    
    # Example 3: List all agents
    print("=" * 60)
    print("All Feng Shui Agents")
    print("=" * 60)
    for agent_name in list_all_agents():
        purpose = get_agent_purpose(agent_name)
        print(f"{agent_name}: {purpose.purpose}")
        print(f"  Detectors: {len(purpose.current_detectors)}")
        print()