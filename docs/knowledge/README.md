# Knowledge Vault

**Purpose**: Project-specific knowledge base with linked documentation  
**Format**: Markdown with [[wikilinks]]  
**Scope**: steel_thread_on_sap project only  
**Version**: 1.0  
**Created**: 2026-01-25

---

## 🎯 What Is This?

The Knowledge Vault is a structured, linked documentation system for the steel_thread_on_sap project. It follows an **Obsidian-like approach** where:

- ✅ **Create new documents** - Don't update old ones
- ✅ **Link documents** - Use [[wikilinks]] to connect concepts
- ✅ **Append-only** - Build knowledge over time
- ✅ **Query-able** - AI can search and consolidate
- ✅ **Single location** - No scattered docs

---

## 📂 Structure

```
docs/knowledge/
├── README.md              # This file - How the system works
├── INDEX.md               # Main navigation hub (auto-updated)
│
├── components/            # Module documentation
│   ├── [module-name].md  # One file per module
│   └── ...
│
├── architecture/          # Architecture decisions and patterns
│   ├── [decision-name].md # Design decisions
│   └── ...
│
├── guidelines/            # Development standards and practices
│   ├── [guideline-name].md # Standards
│   └── ...
│
└── queries/               # Common questions with consolidated answers
    ├── [question].md      # Pre-answered questions
    └── ...
```

---

## 🔗 Linking System

### Wikilinks Format
```markdown
# Related Concepts
- [[Modular Architecture]] - Follows this pattern
- [[API First Approach]] - Uses this principle
- [[HANA Connection]] - Depends on this
```

### Link Categories
- **Components** - Modules and services
- **Architecture** - Design patterns and decisions
- **Guidelines** - Standards and best practices
- **Queries** - Common questions

---

## 🤖 AI Assistant Workflow

**When Creating New Documentation**:

1. **Search for Related Docs**
   ```
   <search_files>
     <path>docs/knowledge</path>
     <regex>(keywords from new doc)</regex>
   </search_files>
   ```

2. **Identify Relationships**
   - Find 3-5 most related documents
   - Determine relationship type (depends on, implements, related to)

3. **Create Document with Links**
   - Use appropriate template
   - Add [[wikilinks]] to related docs
   - Include metadata (type, status, created date)

4. **Update INDEX.md**
   - Add entry under correct category
   - Keep alphabetically sorted

5. **Commit to Git**
   - Single commit for new doc + INDEX update
   - Clear commit message

**This happens AUTOMATICALLY** - No need to remind AI!

---

## 📝 Document Templates

### Component Template
```markdown
# [Component Name]

**Type**: Component
**Status**: [Planning / In Progress / Complete]
**Created**: YYYY-MM-DD
**Module**: modules/[name]/

## Overview
Brief description of the component.

## Related Components
- [[Related Component 1]]
- [[Related Component 2]]

## Related Architecture
- [[Architecture Pattern 1]]
- [[Architecture Pattern 2]]

## Related Guidelines
- [[Guideline 1]]
- [[Guideline 2]]

## Details
Implementation details, capabilities, etc.

## Test Coverage
- Tests: X/X passing
- Coverage: 100%

## Files
- `path/to/file.py` - Description
```

### Architecture Template
```markdown
# [Architecture Decision/Pattern]

**Type**: Architecture
**Decision Date**: YYYY-MM-DD
**Status**: [Proposed / Adopted / Deprecated]

## Context
Why this decision was needed.

## Decision
What was decided.

## Consequences
Impact of this decision.

## Related Components
- [[Component 1]] - Uses this
- [[Component 2]] - Implements this

## Related Architecture
- [[Related Pattern 1]]
- [[Related Pattern 2]]
```

### Guideline Template
```markdown
# [Guideline Name]

**Type**: Guideline
**Category**: [Development / Design / Testing / etc.]
**Created**: YYYY-MM-DD

## Principle
Core principle being documented.

## Requirements
What must be followed.

## Examples
Code examples showing correct usage.

## Related Guidelines
- [[Related Guideline 1]]
- [[Related Guideline 2]]

## Related Components
- [[Component 1]] - Follows this
- [[Component 2]] - Implements this
```

---

## 🚫 What NOT to Document Here

**Do NOT create documents in vault for**:
- ❌ Code itself (lives in modules/)
- ❌ Test files (lives in tests/)
- ❌ Temporary notes (use scratch pad)
- ❌ External resources (link to URL instead)

**DO create documents for**:
- ✅ Component implementations
- ✅ Architecture decisions
- ✅ Guidelines and standards
- ✅ Common questions/FAQs
- ✅ Lessons learned
- ✅ Integration patterns

---

## 🔍 How to Query the Vault

### For AI Assistant
```xml
<!-- Search by topic -->
<search_files>
  <path>docs/knowledge</path>
  <regex>(HANA|connection|module)</regex>
</search_files>

<!-- Read specific document -->
<read_file>
  <path>docs/knowledge/components/hana-connection.md</path>
</read_file>
```

### For Humans
- Browse in VS Code file explorer
- Use VS Code search (Ctrl+Shift+F)
- Open in Obsidian (optional)
- Read INDEX.md for navigation

---

## ✅ Success Criteria

The vault is successful when:
- ✅ All documentation in single location
- ✅ Documents are linked (3+ links each)
- ✅ INDEX.md provides clear navigation
- ✅ AI can query and consolidate
- ✅ No scattered docs outside vault

---

## 📊 Maintenance

**AI Responsibilities**:
- Create new docs in vault (with links)
- Update INDEX.md when adding docs
- Search and link related docs
- Keep structure organized

**User Responsibilities**:
- Review and approve documentation
- Request consolidation when needed
- Suggest new categories if needed

---

**Status**: ✅ **SYSTEM READY** - Start using immediately!