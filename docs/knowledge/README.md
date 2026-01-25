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

**⚠️ CRITICAL: READ THIS FIRST EVERY SESSION**

When the user asks you to document something, you MUST:

### Step 1: Search for Related Documents (MANDATORY)
```xml
<search_files>
  <path>docs/knowledge</path>
  <regex>(keywords from topic)</regex>
</search_files>
```

### Step 2: Analyze Search Results
- Read through ALL results
- Identify 3-5 most related documents
- Note their categories (components/architecture/guidelines/queries)
- Understand the relationships (depends on, implements, related to)

### Step 3: Create Document with [[Wikilinks]]
- Choose appropriate template (see below)
- Add metadata (type, status, created date)
- **MUST include** "## Related Components" section with [[links]]
- **MUST include** "## Related Architecture" section with [[links]]
- **MUST include** "## Related Guidelines" section with [[links]]
- Minimum 3 [[wikilinks]], target 5-8

### Step 4: Update INDEX.md (MANDATORY)
- Add new entry under correct category
- Keep alphabetically sorted
- Update statistics count

### Step 5: Commit Together (MANDATORY)
- Commit new doc + INDEX.md update in ONE commit
- Clear commit message explaining what was documented

### ⚠️ ENFORCEMENT

**This workflow is MANDATORY and AUTOMATIC**:
- ✅ .clinerules enforces this (Section 7)
- ✅ You MUST search before creating
- ✅ You MUST add [[wikilinks]]
- ✅ You MUST update INDEX.md
- ✅ User should NEVER need to remind you

**If you forget**:
1. Stop immediately
2. Re-read this README.md
3. Follow the 5 steps above
4. Never skip steps

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

## 📥 Integrating User-Created Documents

**When user creates a document and asks to integrate it**:

The AI will automatically:

1. **Read the document** to understand content
2. **Determine category** (components/architecture/guidelines/queries)
3. **Search for related docs** in vault
4. **Move to correct folder** with proper naming
5. **Add metadata** (Type, Status, Created date)
6. **Add [[wikilinks]]** (3-5 related documents)
7. **Update INDEX.md** with new entry
8. **Commit changes** (moved doc + INDEX update)

**User command**:
- "Integrate [filename] into the knowledge vault"
- "Add [filename] to the vault with proper links"
- "Move [filename] to knowledge vault and link it"

**Example workflow**:
```
User: "I created my-feature.md. Please integrate it into the vault."

AI Actions:
1. Reads my-feature.md
2. Determines it's a component
3. Searches vault for related docs (HANA, modules, etc.)
4. Moves to docs/knowledge/components/my-feature.md
5. Adds metadata section at top
6. Adds [[Related Component]], [[Architecture Pattern]], etc.
7. Updates INDEX.md under Components section
8. Commits: "[Docs] Integrate My Feature into knowledge vault"
```

**Result**: User-created doc is now fully integrated with proper structure and links! ✅

---

## 📊 Maintenance

**AI Responsibilities**:
- Create new docs in vault (with links)
- Update INDEX.md when adding docs
- Search and link related docs
- Keep structure organized
- **Integrate user-created docs** with proper categorization and linking
- **Run maintenance routines** when requested

**User Responsibilities**:
- Review and approve documentation
- Request consolidation when needed
- Suggest new categories if needed
- Can create docs anywhere, then ask AI to integrate them
- Run maintenance routine periodically

---

## 🔧 Vault Maintenance Routine

**User Command**: "Run vault maintenance" or "Clean up knowledge vault"

### Phase 1: Find Orphaned Documents (AUTO)

AI scans project for .md files outside vault:
```xml
<search_files>
  <path>.</path>
  <regex>\.md$</regex>
</search_files>
```

**Excludes**:
- docs/knowledge/ (already in vault)
- .clinerules (workspace rules)
- PROJECT_TRACKER.md (historical log)
- README.md (project root)
- modules/*/README.md (module entry points)

**Reports**: List of files found that need integration

### Phase 2: User Confirmation (REQUIRED)

AI presents list to user:
```
Found 5 documents to integrate:
1. docs/planning/features/NEW_FEATURE.md
2. csn-investigation-archive/DOCUMENT.md
3. docs/hana-cloud/NEW_GUIDE.md

Options:
- Integrate all
- Integrate selected (specify numbers)
- Skip all
```

**User must approve** before proceeding.

### Phase 3: Integrate Approved Documents (AUTO)

For each approved document:
1. Read content
2. Search vault for related docs
3. Determine category
4. Move to vault with proper naming
5. Add metadata and [[wikilinks]]
6. Update INDEX.md
7. Delete original file

**One commit** for all integrations.

### Phase 4: Identify Obsolete Knowledge (AUTO)

AI scans vault for:

**Obsolete Indicators**:
- Status: "Deprecated"
- "DO NOT USE" in content
- References to deleted code/modules
- Superseded by newer documents
- Implementation plans for completed features
- Old temporary/scratch documents

**Analysis**:
```xml
<read_file path="docs/knowledge/[doc]"/>
<!-- Check for obsolete markers -->
<!-- Check if referenced files/modules exist -->
<!-- Check if superseded by newer docs -->
```

**Reports**: List of potentially obsolete docs with reasons

### Phase 5: User Confirmation for Deletion (REQUIRED)

AI presents analysis:
```
Found 3 potentially obsolete documents:

1. docs/knowledge/architecture/old-pattern.md
   Reason: Status = "Deprecated", superseded by [[New Pattern]]
   
2. docs/knowledge/components/removed-module.md
   Reason: Module folder modules/removed/ no longer exists
   
3. docs/knowledge/queries/outdated-question.md
   Reason: Contains "OBSOLETE" marker

Options:
- Delete all
- Delete selected (specify numbers)
- Archive instead of delete
- Keep all
```

**User must approve** deletions.

### Phase 6: Delete/Archive Obsolete Docs (AUTO)

For each approved deletion:
- Option A: Delete file + remove from INDEX.md
- Option B: Move to docs/knowledge/archive/ folder
- Update INDEX.md statistics
- Update any broken [[links]] in other docs

**One commit** for all deletions.

### Phase 7: Identify Consolidation Opportunities (AUTO)

AI scans for:

**Consolidation Signals**:
- Multiple docs about same component
- Similar topics split across files
- Docs with < 50 lines (too small)
- Heavy cross-linking (3+ docs all link to each other)
- Duplicate information
- Series of related docs (part1, part2, etc.)

**Analysis**:
```
Group A: Feature X (3 documents)
- feature-x-plan.md (50 lines)
- feature-x-implementation.md (40 lines)
- feature-x-summary.md (30 lines)
Suggestion: Merge into single feature-x.md

Group B: HANA Guides (5 documents)
- All heavily cross-linked
- Total: 400 lines
- Could consolidate to 2 documents
```

### Phase 8: User Confirmation for Consolidation (REQUIRED)

AI presents proposals:
```
Found 2 consolidation opportunities:

1. Consolidate Feature X documents
   Current: 3 files (120 lines total)
   Proposed: 1 file (feature-x.md)
   Benefit: Easier to find, less duplication
   
2. Consolidate HANA Guides
   Current: 5 files (400 lines)
   Proposed: 2 files (hana-setup.md, hana-advanced.md)
   Benefit: Better organization, less fragmentation

Options:
- Consolidate all
- Consolidate selected (specify numbers)
- Skip all
```

**User must approve** consolidation.

### Phase 9: Execute Consolidation (AUTO)

For each approved consolidation:
1. Read all source documents
2. Merge content intelligently
3. Combine [[wikilinks]] (remove duplicates)
4. Update metadata (created = oldest, updated = now)
5. Create consolidated document
6. Update all incoming [[links]] to point to new doc
7. Delete old documents
8. Update INDEX.md

**One commit** for all consolidations.

### Phase 10: Final Report (AUTO)

AI provides summary:
```
Vault Maintenance Complete!

Phase 1 - Integration:
✅ Integrated 5 documents with proper linking

Phase 2 - Obsolete Cleanup:
✅ Deleted 3 obsolete documents
✅ Archived 1 document to archive/

Phase 3 - Consolidation:
✅ Consolidated 8 documents into 3
✅ Updated 15 incoming links

Results:
- Before: 25 documents, scattered files
- After: 20 documents, organized vault
- Reduction: 5 files (-20%)
- All links updated ✅
- INDEX.md refreshed ✅

Commit: "[Docs] Vault maintenance - integrate, cleanup, consolidate"
```

---

## 🎯 Maintenance Command Examples

**Full Maintenance**:
```
User: "Run full vault maintenance"
AI: Executes all 10 phases with confirmations
```

**Specific Phases**:
```
User: "Find orphaned documents"
AI: Runs Phase 1 only

User: "Clean up obsolete docs"
AI: Runs Phase 4-6 only

User: "Consolidate vault"
AI: Runs Phase 7-9 only
```

**Scheduled Maintenance**:
```
Recommended: Run full maintenance every 2 weeks
- Prevents vault bloat
- Keeps knowledge current
- Improves search performance
- Maintains single source of truth
```

---

## ✅ Maintenance Benefits

1. **Automatic Discovery** - Finds docs created outside vault
2. **User Control** - Approval required at each phase
3. **Obsolete Removal** - Deletes outdated knowledge
4. **Smart Consolidation** - Reduces fragmentation
5. **Link Maintenance** - Updates all [[links]] automatically
6. **Performance** - Smaller vault = faster search
7. **Quality** - Latest truth easy to find
8. **No Confusion** - Old docs don't mislead

---

**Status**: ✅ **SYSTEM READY** - Start using immediately!
