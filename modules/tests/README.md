 # Module Root API Contract Tests

This directory contains API contract tests for the P2P Data Products modular architecture.

## Purpose

Test the root module's integration and configuration capabilities according to Module Federation Standard v1.0.

## Test Coverage

- Module registry validation
- Module loading and lifecycle
- Inter-module communication
- Configuration validation

## Running Tests

```bash
pytest modules/tests/ -v
```

## Future Tests

- Root module.json schema validation
- Module discovery and registration
- Module dependency resolution
- Module lifecycle hooks

## Related Documentation

- Module Federation Standard: `docs/knowledge/module-federation-standard.md`
- Architecture Proposal: `docs/knowledge/module-federation-architecture-proposal.md`
- Migration Guide: `app_v2/MODULE_MIGRATION_GUIDE.md`