# Feng Shui Routine Requirements

**Purpose**: Mandatory steps for feng shui cleanup execution  
**Created**: February 1, 2026  
**Updated**: February 7, 2026 (Phase 2: Log Intelligence Integration) ⭐  
**Philosophy**: Introspection is worthless without actionable follow-up

---

## ⚠️ MANDATORY WORKFLOW

When AI performs feng shui cleanup, these steps are REQUIRED:

### 1. Execute 5-Phase Analysis ✅
- Phase 1: Scripts cleanup
- Phase 2: Vault maintenance  
- Phase 3: Quality validation
- Phase 4: Architecture review (including GoF patterns)
- Phase 5: File organization (ALL directories)

### 2. Create Audit Report ✅
- Generate comprehensive findings report
- Save to `docs/FENG_SHUI_AUDIT_YYYY-MM-DD.md`
- Include all statistics, patterns, proposals

### 3. Add Work Packages to PROJECT_TRACKER.md ⚠️ MANDATORY

**CRITICAL REQUIREMENT**: Any findings that cannot be immediately resolved MUST be added to PROJECT_TRACKER.md as work packages.

**Why This Matters**:
- Prevents findings from being lost/forgotten
- Creates actionable backlog (not just analysis)
- Enables prioritization and planning
- Completes the feedback loop: Introspection → Action

**Format for Work Packages**:
```markdown
#### Technical Debt from Feng Shui Audit (YYYY-MM-DD)

**Source**: docs/FENG_SHUI_AUDIT_YYYY-MM-DD.md
**Finding**: [Summary of issue]
**Root Cause**: [Why it happened]
**Impact**: [Business/technical impact]

##### High Priority

**WP-XXX: [Title]** 🔴 CRITICAL
- **Issue**: [Detailed problem description]
- **Solution**: [Specific approach]
- **Benefit**: [Value delivered]
- **Effort**: [Time estimate]
- **Priority**: 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW
- **Depends On**: [Other WPs if applicable]
- **Blocks**: [What this blocks if applicable]
```

**Work Package Prioritization**:
- 🔴 **HIGH**: Critical infrastructure, blocks other work, systematic violations
- 🟡 **MEDIUM**: Important but not blocking, quality improvements
- 🟢 **LOW**: Documentation, nice-to-have, preventive measures

**Summary Section** (Always include):
```markdown
##### Summary

**Total Work Packages**: [N]
**Total Effort**: [X-Y hours]
**ROI**: [Expected benefits]
**Quick Wins**: [Highest impact/lowest effort items]
**Template/Reference**: [Successful examples to follow]

**Decision Point**: 
- **Option A**: Implement critical now (X hours) → Y% fixed
- **Option B**: Defer to next sprint → Continue feature work
- **Option C**: Implement all now (Z hours) → 100% resolved

**Recommendation from Audit**: [AI's prioritized recommendation]
```

### 4. Log Intelligence (NEW - Phase 2) ⭐

**Optional Enhancement**: Feng Shui can now use runtime logs to enhance analysis

**How It Works**:
- Orchestrator auto-detects if logs available
- If available: ArchitectAgent detects runtime DI violations from error logs
- If unavailable: Static analysis only (graceful degradation)

**What It Detects** (Runtime):
- AttributeError: 'connection' in production logs
- AttributeError: 'service' in production logs  
- AttributeError: 'db_path' in production logs
- Severity: CRITICAL (runtime failures are high priority)

**Feature Flag**: `log-intelligence` in feature_flags.json (disabled by default)

**Benefits**:
- Detect DI violations that only fail at runtime
- Prioritize fixes by error frequency (15 occurrences > 2 occurrences)
- Correlation with static findings (complete picture)

**Usage**:
```python
# Orchestrator auto-detects logs
orchestrator = AgentOrchestrator()  # Auto-detects log availability
report = orchestrator.analyze_module_comprehensive(module_path)

# ArchitectAgent includes runtime DI findings if logs available
# Otherwise: Static analysis only (backward compatible)
```

### 5. Update FENG_SHUI_AUDIT_YYYY-MM-DD.md ✅
Reference that work packages were added to PROJECT_TRACKER.md (create complete audit trail)

### 6. Commit Everything Together ✅
```bash
git add docs/FENG_SHUI_AUDIT_*.md PROJECT_TRACKER.md [other files]
git commit -m "[Feng Shui] Complete audit + work packages added to backlog"
```

---

## ❌ WHAT NOT TO DO

**Don't**:
- ❌ Create audit report without adding work packages
- ❌ Add work packages without linking to audit report
- ❌ Leave critical findings undocumented in PROJECT_TRACKER.md
- ❌ Skip prioritization (all work packages need priority)
- ❌ Forget effort estimates (needed for planning)
- ❌ Skip dependency tracking (shows implementation order)

**Remember**: 
> "Introspection without action is just naval-gazing"
> "Findings in audit report → Work packages in tracker → Implementation → Value delivered"

---

## 📋 Complete Feng Shui Checklist

When user requests "feng shui cleanup", AI must:

- [ ] Execute Phase 1: Scripts cleanup
- [ ] Execute Phase 2: Vault maintenance
- [ ] Execute Phase 3: Quality validation
- [ ] Execute Phase 4: Architecture review
  - [ ] Modular architecture compliance
  - [ ] DI violations check
  - [ ] Interface usage validation
  - [ ] **GoF Design Pattern compliance** (NEW)
- [ ] Execute Phase 5: File organization (all directories)
- [ ] Create audit report (`docs/FENG_SHUI_AUDIT_YYYY-MM-DD.md`)
- [ ] ⚠️ **Add work packages to PROJECT_TRACKER.md** (MANDATORY)
- [ ] Update audit report with tracker reference
- [ ] Commit all changes together
- [ ] Present findings + work packages to user
- [ ] Get user decision on implementation priority

**Time Estimate**: 30-60 minutes (including work package creation)

---

## 🎯 Integration with Project Workflow

**Feng Shui Output Flow**:
```
Audit Report → Work Packages → PROJECT_TRACKER.md → Implementation → Value
     ↓              ↓                  ↓                    ↓            ↓
  Analysis     Prioritized       Backlog Item          Scheduled      Done
```

**Without This Flow**:
```
Audit Report → [Lost/Forgotten] → Never Implemented → Zero Value ❌
```

**With This Flow**:
```
Audit Report → Work Packages → Prioritized → Implemented → 100% ROI ✅
```

---

## 📊 Example Work Package Set

**From First Feng Shui Audit (2026-02-01)**:

- **Finding**: 10/12 modules failing quality gate
- **Root Cause**: Systematic DI violations
- **Work Packages Created**: 14 (WP-001 through WP-014)
- **Total Effort**: 12-15 hours
- **Priority Breakdown**:
  - 🔴 HIGH: 3 packages (5 hours) → Unblocks 83% of issues
  - 🟡 MEDIUM: 10 packages (8 hours) → Complete cleanup
  - 🟢 LOW: 1 package (2 hours) → Documentation

**Result**: Clear backlog, prioritized roadmap, measurable progress

---

## 💡 Why This Requirement Exists

**User Philosophy**:
> "Critical findings which cannot be easily resolved immediately should be added to the project tracker as work package proposal and planning"

**Reasoning**:
1. **Actionable**: Findings become trackable work items
2. **Prioritized**: Can decide when to implement
3. **Measurable**: Effort estimates enable planning
4. **Traceable**: Audit → Work Package → Implementation chain
5. **Valuable**: Introspection leads to actual improvement

**Without This**:
- Feng shui audit = interesting analysis, no action
- Critical issues documented but never addressed
- Technical debt grows despite awareness
- Wasted effort on introspection

**With This**:
- Feng shui audit = analysis + actionable roadmap
- Critical issues tracked and prioritized
- Technical debt actively managed
- ROI on introspection effort

---

## 🌱 Living Document Evolution

**This requirement emerged from**:
- User question: "Why not add findings to tracker?"
- AI recognition: Valid process improvement
- System evolution: Mandatory step added
- Future benefit: All feng shui cleanups now complete the loop

**Like feng shui itself**: The system learns and improves through feedback! 🧘💤✨

---

**Status**: ✅ Active requirement for all feng shui cleanups  
**Scope**: Phases 3 & 4 findings → PROJECT_TRACKER.md work packages  
**Frequency**: Every feng shui cleanup (monthly recommended)  
**Enhancement**: Phase 2 log intelligence integration (2026-02-07) ⭐  
**Related**: 
- `docs/FENG_SHUI_AUDIT_2026-02-01.md` - Example audit
- `PROJECT_TRACKER.md` - Work packages location
- `scripts/CLEANUP_GUIDE.md` - Complete feng shui guide
- `core/interfaces/log_intelligence.py` - Log intelligence interface (NEW)
- `docs/knowledge/log-integration-proposal.md` - Complete proposal (NEW)
