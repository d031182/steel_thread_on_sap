"""
Feature Flags Service - Core business logic for feature management

This service provides:
1. Feature flag storage and retrieval
2. Enable/disable/toggle operations
3. Persistence to JSON file
4. Export/import configuration
5. Reset to defaults

Part of: Feature Manager Module
Version: 1.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Add project root to path for core imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.module_registry import ModuleRegistry


class FeatureFlags:
    """
    Core service for managing feature flags.
    
    Features are stored in a JSON file and can be toggled on/off
    to enable/disable modules dynamically.
    """
    
    def __init__(self, storage_file: str = "feature_flags.json", default_features: Optional[Dict] = None):
        """
        Initialize feature flags service.
        
        Args:
            storage_file: Path to JSON file for persistence
            default_features: Default feature configuration
        """
        self.storage_file = Path(storage_file)
        self.default_features = default_features or self._get_default_features()
        self.features: Dict[str, dict] = {}
        
        # Load existing or initialize with defaults
        self.load()
    
    def _get_default_features(self) -> Dict[str, dict]:
        """
        Get default feature configuration from ModuleRegistry.
        
        Auto-discovers all modules and creates features from their metadata.
        
        Returns:
            Dictionary of feature_name -> feature_config
        """
        try:
            # Get modules path (relative to this file)
            modules_path = project_root / "modules"
            
            # Initialize ModuleRegistry
            registry = ModuleRegistry(str(modules_path))
            
            # Get all modules
            all_modules = registry.get_all_modules()
            
            # Convert modules to features
            features = {}
            for module_name, module_config in all_modules.items():
                features[module_name] = {
                    "enabled": module_config.get('enabled', True),
                    "displayName": module_config.get('displayName', module_name),
                    "description": module_config.get('description', ''),
                    "category": module_config.get('category', 'Uncategorized'),
                    "version": module_config.get('version', '1.0.0'),
                    "requiresHana": module_config.get('requiresHana', False)
                }
            
            print(f"[FeatureFlags] Auto-discovered {len(features)} features from ModuleRegistry")
            return features
            
        except Exception as e:
            print(f"[FeatureFlags] WARNING: ModuleRegistry unavailable, using fallback: {e}")
            # Fallback to minimal defaults if ModuleRegistry fails
            return {
                "feature_manager": {
                    "enabled": True,
                    "displayName": "Feature Manager",
                    "description": "Feature toggle system",
                    "category": "Infrastructure"
                },
                "application_logging": {
                    "enabled": True,
                    "displayName": "Application Logging",
                    "description": "SQLite-based logging system",
                    "category": "Infrastructure"
                }
            }
    
    def load(self) -> bool:
        """
        Load features from storage file.
        
        If file doesn't exist, initializes with defaults.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both formats: direct features dict or nested under "features" key
                    if isinstance(data, dict) and 'features' in data:
                        self.features = data['features']
                    else:
                        self.features = data
                print(f"[FeatureFlags] Loaded {len(self.features)} features from {self.storage_file}")
                return True
            else:
                # Initialize with defaults
                self.features = self.default_features.copy()
                self.save()
                print(f"[FeatureFlags] Initialized with {len(self.features)} default features")
                return True
        except Exception as e:
            print(f"[FeatureFlags] ERROR: Error loading features: {e}")
            # Fall back to defaults
            self.features = self.default_features.copy()
            return False
    
    def save(self) -> bool:
        """
        Save features to storage file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if needed
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            data = {
                "version": "1.0",
                "lastModified": datetime.now().isoformat(),
                "features": self.features
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"[FeatureFlags] Saved {len(self.features)} features to {self.storage_file}")
            return True
        except Exception as e:
            print(f"[FeatureFlags] ERROR: Error saving features: {e}")
            return False
    
    def get_all(self) -> Dict[str, dict]:
        """
        Get all features with their configuration.
        
        Returns:
            Dictionary of feature_name -> feature_config
        """
        return self.features.copy()
    
    def get(self, feature_name: str) -> Optional[dict]:
        """
        Get a specific feature configuration.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            Feature configuration dict or None if not found
        """
        return self.features.get(feature_name)
    
    def is_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            True if enabled, False otherwise
        """
        feature = self.features.get(feature_name)
        if feature:
            return feature.get('enabled', False)
        return False
    
    def enable(self, feature_name: str) -> bool:
        """
        Enable a feature.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            True if enabled successfully, False if feature not found
        """
        if feature_name in self.features:
            self.features[feature_name]['enabled'] = True
            self.save()
            print(f"[FeatureFlags] Enabled feature: {feature_name}")
            return True
        
        print(f"[FeatureFlags] ERROR: Feature not found: {feature_name}")
        return False
    
    def disable(self, feature_name: str) -> bool:
        """
        Disable a feature.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            True if disabled successfully, False if feature not found
        """
        if feature_name in self.features:
            self.features[feature_name]['enabled'] = False
            self.save()
            print(f"[FeatureFlags] Disabled feature: {feature_name}")
            return True
        
        print(f"[FeatureFlags] ERROR: Feature not found: {feature_name}")
        return False
    
    def toggle(self, feature_name: str) -> Optional[bool]:
        """
        Toggle a feature on/off.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            New enabled state (True/False) or None if feature not found
        """
        if feature_name in self.features:
            current_state = self.features[feature_name].get('enabled', False)
            new_state = not current_state
            self.features[feature_name]['enabled'] = new_state
            self.save()
            print(f"[FeatureFlags] Toggled {feature_name}: {current_state} -> {new_state}")
            return new_state
        
        print(f"[FeatureFlags] ERROR: Feature not found: {feature_name}")
        return None
    
    def add_feature(self, feature_name: str, config: dict) -> bool:
        """
        Add a new feature.
        
        Args:
            feature_name: Name of the feature
            config: Feature configuration (displayName, description, etc.)
        
        Returns:
            True if added successfully, False if already exists
        """
        if feature_name not in self.features:
            # Ensure enabled flag exists
            if 'enabled' not in config:
                config['enabled'] = True
            
            self.features[feature_name] = config
            self.save()
            print(f"[FeatureFlags] Added feature: {feature_name}")
            return True
        
        print(f"[FeatureFlags] ERROR: Feature already exists: {feature_name}")
        return False
    
    def remove_feature(self, feature_name: str) -> bool:
        """
        Remove a feature.
        
        Args:
            feature_name: Name of the feature
        
        Returns:
            True if removed successfully, False if not found
        """
        if feature_name in self.features:
            del self.features[feature_name]
            self.save()
            print(f"[FeatureFlags] Removed feature: {feature_name}")
            return True
        
        print(f"[FeatureFlags] ERROR: Feature not found: {feature_name}")
        return False
    
    def get_enabled_features(self) -> List[str]:
        """
        Get list of enabled feature names.
        
        Returns:
            List of feature names that are enabled
        """
        return [
            name for name, config in self.features.items()
            if config.get('enabled', False)
        ]
    
    def get_disabled_features(self) -> List[str]:
        """
        Get list of disabled feature names.
        
        Returns:
            List of feature names that are disabled
        """
        return [
            name for name, config in self.features.items()
            if not config.get('enabled', False)
        ]
    
    def get_features_by_category(self, category: str) -> Dict[str, dict]:
        """
        Get features in a specific category.
        
        Args:
            category: Category name
        
        Returns:
            Dictionary of features in the category
        """
        return {
            name: config
            for name, config in self.features.items()
            if config.get('category') == category
        }
    
    def export_config(self) -> str:
        """
        Export feature configuration as JSON string.
        
        Returns:
            JSON string of feature configuration
        """
        return json.dumps(self.features, indent=2)
    
    def import_config(self, config_json: str) -> bool:
        """
        Import feature configuration from JSON string.
        
        Args:
            config_json: JSON string of feature configuration
        
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            imported_features = json.loads(config_json)
            
            # Validate it's a dictionary
            if not isinstance(imported_features, dict):
                print("[FeatureFlags] ERROR: Invalid configuration format")
                return False
            
            self.features = imported_features
            self.save()
            print(f"[FeatureFlags] Imported {len(self.features)} features")
            return True
        except json.JSONDecodeError as e:
            print(f"[FeatureFlags] ERROR: Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"[FeatureFlags] ERROR: Error importing config: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all features to default configuration.
        
        Returns:
            True if reset successfully
        """
        self.features = self.default_features.copy()
        self.save()
        print(f"[FeatureFlags] Reset to {len(self.features)} default features")
        return True
    
    def get_feature_count(self) -> int:
        """
        Get total number of features.
        
        Returns:
            Count of features
        """
        return len(self.features)
    
    def __repr__(self) -> str:
        """String representation."""
        enabled_count = len(self.get_enabled_features())
        total_count = self.get_feature_count()
        return f"<FeatureFlags: {enabled_count}/{total_count} enabled>"


# Global instance (singleton pattern)
_feature_flags_instance: Optional[FeatureFlags] = None


def get_feature_flags(storage_file: str = "feature_flags.json") -> FeatureFlags:
    """
    Get the global feature flags instance.
    
    Args:
        storage_file: Path to storage file
    
    Returns:
        FeatureFlags instance
    """
    global _feature_flags_instance
    
    if _feature_flags_instance is None:
        _feature_flags_instance = FeatureFlags(storage_file)
    
    return _feature_flags_instance


if __name__ == "__main__":
    # Test feature flags
    print("=== Feature Flags Test ===\n")
    
    # Create instance
    ff = FeatureFlags("test_features.json")
    
    print(f"\nFeature Flags: {ff}")
    print(f"Total features: {ff.get_feature_count()}")
    print(f"Enabled: {ff.get_enabled_features()}")
    print(f"Disabled: {ff.get_disabled_features()}")
    
    print("\n--- Testing Operations ---")
    
    # Test toggle
    print(f"\nToggling 'application-logging'...")
    new_state = ff.toggle("application-logging")
    print(f"New state: {new_state}")
    
    # Test enable/disable
    print(f"\nDisabling 'feature-manager'...")
    ff.disable("feature-manager")
    print(f"Is enabled: {ff.is_enabled('feature-manager')}")
    
    print(f"\nEnabling 'feature-manager'...")
    ff.enable("feature-manager")
    print(f"Is enabled: {ff.is_enabled('feature-manager')}")
    
    # Test export/import
    print("\n--- Testing Export/Import ---")
    exported = ff.export_config()
    print(f"Exported config ({len(exported)} chars)")
    
    # Cleanup test file
    if Path("test_features.json").exists():
        Path("test_features.json").unlink()
        print("\nTest cleanup complete")
