# Effective AI Collaboration Guide

**Created**: 2026-02-01  
**Purpose**: Prevent "back to square one" miscommunications  
**Context**: After cache implementation confusion

---

## The Problem We're Solving

**What Happened**:
- User: "I expected full graph cache (nodes + edges instantly loaded)"
- AI: "I only implemented FK relationship cache (partial solution)"
- Result: 90 minutes of confusion until user asked directly

**Root Cause**: **Assumption Mismatch**
- AI assumed user understood partial implementation
- User assumed AI completed full implementation
- Neither verified assumptions explicitly

---

## Communication Patterns That Work

### 1. Explicit Acceptance Criteria (User → AI)

**❌ DON'T SAY**:
> "Optimize the cache"

**✅ DO SAY**:
> "Optimize the cache so that:
> - Clicking 'Refresh Graph' loads in <1 second
> - Both nodes AND edges are cached
> - No database queries during cache hits"

**Why It Works**: Specific, measurable outcomes prevent assumption gaps

---

### 2. Implementation Scope Confirmation (AI → User)

**❌ AI Should NOT Assume**:
> "I'll implement caching" (ambiguous scope)

**✅ AI Should Confirm**:
> "I'll implement FK relationship caching (4ms speedup for discovery).
> Note: This caches relationships only, not full graph nodes.
> Should I also cache complete graph for instant loading?"

**Why It Works**: Makes scope explicit, invites correction

---

### 3. "What Does Success Look Like?" Question

**Before starting ANY feature, ask**:

**User Template**:
```
What success looks like:
- User experience: [describe what user sees/feels]
- Performance: [specific numbers]
- Scope: [what IS included, what is NOT]
```

**Example (Cache Feature)**:
```
What success looks like:
- User experience: Click "Refresh Graph" → instant load (<1s)
- Performance: First load 27s (builds cache), subsequent <100ms
- Scope: 
  ✅ Cache nodes (products, tables, records)
  ✅ Cache edges (all relationships)
  ✅ Cache invalidation API
  ❌ NOT auto-refresh on data changes (manual button)
```

---

### 4. Phase Clarification (For Multi-Step Work)

**When work has phases, be explicit**:

**AI Template**:
```
This has 3 phases:
Phase 1: [scope] - [time] ← YOU ARE HERE
Phase 2: [scope] - [time] ← PLANNED
Phase 3: [scope] - [time] ← FUTURE

Implementing Phase 1 now. Phase 2 requires [X]. Proceed?
```

**Example (Our Cache Case)**:
```
Ontology caching has 2 phases:
Phase 1: FK relationship cache (4ms) - 30 min ← IMPLEMENTING
Phase 2: Full graph cache (<100ms) - 2 hours ← NOT INCLUDED

Phase 1 gives 103x speedup for discovery.
Phase 2 gives 270x speedup for complete graph loading.

Should I include Phase 2, or Phase 1 only?
```

---

### 5. Use Behavioral Tests (Not Technical Terms)

**❌ Technical (Ambiguous)**:
> "Is the cache working?"

**✅ Behavioral (Specific)**:
> "After I click 'Refresh Graph' twice:
> - First click: Should take 27 seconds (builds cache)
> - Second click: Should take <1 second (uses cache)
> Does this happen?"

**Why It Works**: Describes observable behavior, not implementation

---

## Explicit Commands You Can Use

### Command Pattern 1: "Verify My Understanding"

**When unsure, ask AI**:
```
Verify my understanding:
- I expect [behavior X]
- Because you said [statement Y]
- Is this correct?
```

**Example**:
```
Verify my understanding:
- I expect clicking "Refresh Graph" loads instantly
- Because you said "cache is implemented"
- Is this correct?
```

**AI Response Should Be**:
```
No, partially correct:
- Current: FK relationships cached (4ms), nodes queried fresh (25s)
- Your expectation: Full graph cached (nodes + edges <100ms)
- Gap: Phase 2 (full graph cache) not implemented yet
```

---

### Command Pattern 2: "Show Me What's Cached"

**When verifying implementation**:
```
Show me what's currently cached:
- What data is stored?
- What data is still queried fresh?
- What's the actual performance impact?
```

**Forces AI to be concrete about scope**

---

### Command Pattern 3: "Define Success Metrics"

**Before starting work**:
```
Define success metrics for [feature]:
- Performance: [specific numbers]
- User experience: [specific behavior]
- Scope: [what's included/excluded]
```

**AI must provide measurable criteria**

---

### Command Pattern 4: "Implementation vs Planning Mode"

**Choose mode explicitly**:

**Planning Mode**:
```
PLAN MODE: Create architecture for full graph cache
- Don't implement yet
- Document phases, time, trade-offs
- Get approval before coding
```

**Implementation Mode**:
```
ACT MODE: Implement Phase 1 only
- FK relationship cache
- Do NOT implement full graph cache yet
- Commit when Phase 1 complete
```

---

## AI Self-Check Questions

**Before saying "done", AI must verify**:

1. ✅ Does implementation match user's stated expectations?
2. ✅ Did I communicate scope limitations clearly?
3. ✅ Would user be surprised by what IS NOT included?
4. ✅ Did I verify behavioral outcomes, not just technical completion?

**If ANY answer is uncertain**: Ask user to clarify expectations

---

## Red Flags (Communication Smells)

**🚩 Danger Signs**:

1. **Vague Success Criteria**
   - "Make it faster" (how fast?)
   - "Optimize the cache" (what specifically?)
   - "Fix the performance" (to what target?)

2. **Assumption Language**
   - "Obviously..." (nothing is obvious)
   - "Of course..." (verify instead)
   - "Naturally..." (state explicitly)

3. **Technical Jargon Without Behavior**
   - "Cache is implemented" (what's cached? what's the impact?)
   - "Graph optimization done" (what changed for user?)
   - "Fixed the bug" (how do I verify?)

4. **Incomplete Phase Communication**
   - "Phase 1 complete" (but user expected Phases 1+2)
   - "Started implementation" (of what scope?)
   - "Making progress" (toward what specific goal?)

---

## Case Study: Our Cache Confusion

### What Went Wrong

**User Expectation** (Implicit):
- Full graph cache (nodes + edges)
- Instant "Refresh Graph" loading

**AI Implementation** (Implicit):
- Only FK relationship cache
- Partial speedup (4ms for discovery, 25s for graph)

**Communication Gap**:
- AI didn't state "Phase 1 only, Phase 2 not included"
- User didn't verify "cache = complete graph cache"
- 90 minutes wasted on misalignment

### What Would Have Prevented It

**Option 1 - AI Upfront**:
```
Implementing FK relationship cache (Phase 1):
- Caches: Relationship discovery only
- Performance: 4ms (was 410ms)
- Does NOT cache: Complete graph nodes/edges
- "Refresh Graph" still takes 27s (queries nodes fresh)

For instant loading, need Phase 2 (full graph cache - 2 hours).
Proceed with Phase 1 only, or include Phase 2?
```

**Option 2 - User Verification**:
```
Verify: After cache implementation:
- "Refresh Graph" should load in <1 second
- Both schema and data modes instant
- No database queries on refresh
Is this correct?
```

**Either would have caught the mismatch immediately**

---

## Recommended Workflow

### For Users

**Starting New Feature**:
1. Describe desired behavior (not technical terms)
2. Provide success metrics (numbers, not adjectives)
3. Clarify scope (what's included/excluded)

**During Implementation**:
4. Ask "Verify my understanding" if uncertain
5. Request behavioral tests, not technical status

**At Completion**:
6. Verify behavioral outcomes match expectations
7. If surprised, investigate assumption gap

### For AI

**Starting New Feature**:
1. Restate user request in behavioral terms
2. Propose phases if multi-step (get approval for scope)
3. State success metrics explicitly

**During Implementation**:
4. Communicate limitations/trade-offs proactively
5. Don't assume user understands technical scope

**At Completion**:
6. Verify implementation matches stated expectations
7. If uncertain, ask user to verify behavior

---

## Quick Templates

### User: "Define Success" Template
```
For [feature], success means:
1. User sees: [observable behavior]
2. Performance: [specific numbers]
3. Includes: [list what IS in scope]
4. Excludes: [list what is NOT in scope]
```

### AI: "Scope Confirmation" Template
```
Implementing [feature] with scope:
- Phase 1: [specific items] - [time] ← THIS SESSION
- Phase 2: [specific items] - [time] ← NOT INCLUDED
- Impact: [specific numbers]
Proceed with Phase 1 only?
```

### User: "Verify Understanding" Template
```
Verify: After this work:
- I should see: [specific behavior]
- Performance should be: [specific numbers]
- Is this correct?
```

---

## Summary

**Root Cause of Confusion**: Implicit assumptions about scope/expectations

**Prevention**:
1. **Users**: State behavioral expectations explicitly
2. **AI**: Confirm scope/phases before implementing
3. **Both**: Verify assumptions, don't assume alignment

**Simple Rule**: 
> "If it takes 90 minutes to clarify, 
> it should have taken 3 minutes to verify upfront."

**One Question That Prevents This**:
> "What specific behavior should I see after this is complete?"

---

**Key Insight**: The 90-minute cache discussion happened because neither party explicitly verified the scope. This guide ensures future work starts with aligned expectations.