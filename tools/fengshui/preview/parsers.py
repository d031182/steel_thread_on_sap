"""
Design Document Parsers for Feng Shui Preview Mode

Extracts module specifications from documentation files:
- module.json: Module metadata, dependencies, routes
- README.md: Structure, API endpoints, architecture
- API specs: Endpoint contracts, parameters

Philosophy: "Extract the plan before validating it"
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class ExtractedModuleSpec:
    """
    Module specification extracted from documentation files.
    
    Maps to PreviewEngine input format.
    """
    module_id: str
    routes: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    factory_name: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    required_files: List[str] = field(default_factory=list)
    required_directories: List[str] = field(default_factory=list)
    backend_api_path: Optional[str] = None
    
    # Metadata from extraction
    source_files: List[str] = field(default_factory=list)
    extraction_warnings: List[str] = field(default_factory=list)
    confidence_score: float = 1.0  # 0.0-1.0, how confident extraction was


class ModuleJsonParser:
    """
    Parse module.json for module metadata.
    
    Extracts:
    - module_id (from "id" field)
    - routes (from "routes" array)
    - factory_name (from "factory" field)
    - dependencies (from "dependencies" array)
    - backend_api_path (from "backend.api" field)
    """
    
    @staticmethod
    def parse(file_path: Path) -> Optional[ExtractedModuleSpec]:
        """
        Parse module.json file.
        
        Args:
            file_path: Path to module.json
            
        Returns:
            ExtractedModuleSpec or None if parsing fails
        """
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            spec = ExtractedModuleSpec(
                module_id=data.get('id', ''),
                source_files=[str(file_path)]
            )
            
            # Extract routes
            if 'routes' in data:
                spec.routes = data['routes']
            
            # Extract factory name
            if 'factory' in data:
                spec.factory_name = data['factory']
            
            # Extract dependencies
            if 'dependencies' in data:
                spec.dependencies = data['dependencies']
            
            # Extract backend API path
            if 'backend' in data and 'api' in data['backend']:
                spec.backend_api_path = data['backend']['api']
            
            # Confidence: 1.0 if all critical fields present
            critical_fields = ['id', 'routes', 'factory']
            present_fields = sum(1 for field in critical_fields if data.get(field))
            spec.confidence_score = present_fields / len(critical_fields)
            
            if spec.confidence_score < 1.0:
                spec.extraction_warnings.append(
                    f"Missing critical fields: {[f for f in critical_fields if not data.get(f)]}"
                )
            
            return spec
            
        except json.JSONDecodeError as e:
            return None
        except Exception as e:
            return None


class ReadmeParser:
    """
    Parse README.md for structure and API information.
    
    Extracts:
    - required_files (from "Structure" section)
    - required_directories (from "Structure" section)
    - api_endpoints (from "API Endpoints" section)
    """
    
    @staticmethod
    def parse(file_path: Path) -> Optional[ExtractedModuleSpec]:
        """
        Parse README.md file.
        
        Args:
            file_path: Path to README.md
            
        Returns:
            ExtractedModuleSpec or None if parsing fails
        """
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            spec = ExtractedModuleSpec(
                module_id='',  # Must be filled from module.json
                source_files=[str(file_path)]
            )
            
            # Extract module ID from title (e.g., "# AI Assistant Module" or "# Test Module")
            # Match "# Some Title Module" or "# Some Title" (with optional Module at end)
            title_match = re.search(r'^#\s+(.+?)\s*$', content, re.MULTILINE)
            if title_match:
                module_name = title_match.group(1).strip()
                # Remove trailing "Module" if present (case-insensitive)
                module_name = re.sub(r'\s+Module$', '', module_name, flags=re.IGNORECASE)
                # Convert to snake_case
                spec.module_id = re.sub(r'[^a-z0-9]+', '_', module_name.lower()).strip('_')
            
            # Extract structure (files and directories)
            spec.required_files, spec.required_directories = ReadmeParser._extract_structure(content)
            
            # Extract API endpoints
            spec.api_endpoints = ReadmeParser._extract_api_endpoints(content)
            
            # Confidence based on extraction success
            extraction_count = sum([
                1 if spec.module_id else 0,
                1 if spec.required_files else 0,
                1 if spec.required_directories else 0,
                1 if spec.api_endpoints else 0
            ])
            spec.confidence_score = extraction_count / 4
            
            if extraction_count < 2:
                spec.extraction_warnings.append(
                    "Low information density in README.md"
                )
            
            return spec
            
        except Exception as e:
            return None
    
    @staticmethod
    def _extract_structure(content: str) -> tuple[List[str], List[str]]:
        """
        Extract file and directory structure from README.
        
        Looks for sections like:
        ## Structure
        ```
        module/
        ├── backend/
        │   ├── api.py
        ```
        
        Returns:
            (files, directories) tuple
        """
        files = []
        directories = []
        
        # Find structure section
        structure_match = re.search(
            r'##\s+Structure\s*\n\s*```[^\n]*\n(.*?)```',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if structure_match:
            structure_text = structure_match.group(1)
            
            # Parse tree structure
            for line in structure_text.split('\n'):
                # Remove tree characters
                cleaned = re.sub(r'^[│├└─\s]+', '', line).strip()
                
                if not cleaned:
                    continue
                
                if cleaned.endswith('/'):
                    # Directory
                    directories.append(cleaned.rstrip('/'))
                elif '.' in cleaned:
                    # File (has extension)
                    files.append(cleaned)
        
        return files, directories
    
    @staticmethod
    def _extract_api_endpoints(content: str) -> List[str]:
        """
        Extract API endpoints from README.
        
        Looks for patterns like:
        - POST /api/module/endpoint
        - GET /api/module/endpoint
        
        Returns:
            List of endpoint paths
        """
        endpoints = []
        
        # Find API section
        api_section_match = re.search(
            r'##\s+API\s+Endpoints?\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if api_section_match:
            api_text = api_section_match.group(1)
            
            # Extract endpoints (e.g., "POST /api/ai-assistant/chat")
            endpoint_pattern = r'(?:GET|POST|PUT|DELETE|PATCH)\s+(/api/[^\s\)]+)'
            endpoints = re.findall(endpoint_pattern, api_text, re.IGNORECASE)
        
        # Also look for code blocks with route definitions
        code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            # Look for @blueprint.route decorators
            routes = re.findall(r'@\w+\.route\([\'"]([^\'"]+)[\'"]', block)
            endpoints.extend(routes)
        
        return list(set(endpoints))  # Remove duplicates


class DesignDocumentParser:
    """
    Main parser coordinating extraction from multiple sources.
    
    Combines data from:
    1. module.json (highest priority)
    2. README.md (supplementary)
    3. API spec files (if provided)
    
    Philosophy: "Trust the code, verify the docs"
    """
    
    def __init__(self, module_path: Path):
        """
        Initialize parser for a module directory.
        
        Args:
            module_path: Path to module root directory
        """
        self.module_path = Path(module_path)
        self.module_json_path = self.module_path / 'module.json'
        self.readme_path = self.module_path / 'README.md'
    
    def parse(self) -> Optional[ExtractedModuleSpec]:
        """
        Parse all available documentation and combine results.
        
        Returns:
            Combined ExtractedModuleSpec or None if critical files missing
        """
        # Parse module.json (required)
        module_json_spec = ModuleJsonParser.parse(self.module_json_path)
        if not module_json_spec:
            return None
        
        # Parse README.md (optional but recommended)
        readme_spec = ReadmeParser.parse(self.readme_path)
        
        # Combine specifications
        combined_spec = self._merge_specs(module_json_spec, readme_spec)
        
        return combined_spec
    
    def _merge_specs(
        self,
        primary: ExtractedModuleSpec,
        secondary: Optional[ExtractedModuleSpec]
    ) -> ExtractedModuleSpec:
        """
        Merge specifications with priority to primary source.
        
        Args:
            primary: Primary specification (module.json)
            secondary: Secondary specification (README.md)
            
        Returns:
            Merged specification
        """
        if not secondary:
            return primary
        
        # Start with primary
        merged = ExtractedModuleSpec(
            module_id=primary.module_id,
            routes=primary.routes.copy(),
            api_endpoints=primary.api_endpoints.copy(),
            factory_name=primary.factory_name,
            dependencies=primary.dependencies.copy(),
            required_files=primary.required_files.copy(),
            required_directories=primary.required_directories.copy(),
            backend_api_path=primary.backend_api_path,
            source_files=primary.source_files.copy(),
            extraction_warnings=primary.extraction_warnings.copy(),
            confidence_score=primary.confidence_score
        )
        
        # Merge from secondary (no duplicates)
        merged.api_endpoints.extend(
            ep for ep in secondary.api_endpoints 
            if ep not in merged.api_endpoints
        )
        
        merged.required_files.extend(
            f for f in secondary.required_files 
            if f not in merged.required_files
        )
        
        merged.required_directories.extend(
            d for d in secondary.required_directories 
            if d not in merged.required_directories
        )
        
        # Combine source files and warnings
        merged.source_files.extend(secondary.source_files)
        merged.extraction_warnings.extend(secondary.extraction_warnings)
        
        # Adjust confidence score (average if both have data)
        if secondary.confidence_score > 0:
            merged.confidence_score = (
                primary.confidence_score + secondary.confidence_score
            ) / 2
        
        return merged
    
    def to_preview_spec(self, spec: ExtractedModuleSpec) -> Dict:
        """
        Convert ExtractedModuleSpec to PreviewEngine input format.
        
        Args:
            spec: Extracted specification
            
        Returns:
            Dictionary suitable for PreviewEngine.preview()
        """
        return {
            'module_id': spec.module_id,
            'routes': spec.routes,
            'factory_name': spec.factory_name,
            'files': spec.required_files,
            'directories': spec.required_directories,
            'backend_api': spec.backend_api_path,
            'dependencies': spec.dependencies,
            
            # Metadata
            '_extracted_from': spec.source_files,
            '_confidence': spec.confidence_score,
            '_warnings': spec.extraction_warnings
        }


def parse_module_design(module_path: str) -> Optional[Dict]:
    """
    Convenience function to parse module design from documentation.
    
    Args:
        module_path: Path to module root directory
        
    Returns:
        Preview specification dictionary or None
        
    Example:
        >>> spec = parse_module_design('modules/ai_assistant')
        >>> if spec:
        ...     print(f"Module: {spec['module_id']}")
        ...     print(f"Routes: {spec['routes']}")
    """
    parser = DesignDocumentParser(Path(module_path))
    extracted = parser.parse()
    
    if not extracted:
        return None
    
    return parser.to_preview_spec(extracted)