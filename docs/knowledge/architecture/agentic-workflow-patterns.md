# Agentic Workflow Patterns

**Purpose**: Understanding AI agent workflow patterns for autonomous task execution  
**Source**: Industry best practices (Google, AWS, Weaviate/Elysia, Machine Learning Mastery)  
**Date**: 2026-02-06  
**Context**: Enhancing AI assistant capabilities with proven workflow patterns  
**Research**: Perplexity AI search of Weaviate blog + Machine Learning Mastery + Context Engineering patterns

---

## Overview

**What Are Agentic Workflows?**

Agentic workflows are design patterns that enable AI systems to break down complex tasks into manageable steps, make decisions autonomously, and execute multi-step processes with minimal human intervention.

**Why They Matter:**
- Transform single-shot AI responses → autonomous problem-solving
- Enable complex task completion (not just Q&A)
- Allow self-correction and iteration
- Scale AI capabilities beyond prompt-response

**The Thought-Action-Observation Cycle** (Core Framework):

Modern agentic systems operate in a continuous cycle:
```
THOUGHT (Planning) → ACTION (Tool Use) → OBSERVATION (Reflection) → THOUGHT (Next Step)
```

This cycle, popularized by Weaviate's Elysia framework, forms the foundation of all agentic patterns. The agent:
1. **THINKS**: Evaluates environment, tools, past actions, and available options
2. **ACTS**: Executes selected tool or takes decision
3. **OBSERVES**: Reviews output to assess success/failure
4. **REFLECTS**: Decides whether to iterate, switch strategies, or complete task

**Source**: Weaviate Context Engineering (Dec 2025)

---

## Core Agentic Workflow Patterns

### 1. ReAct Pattern (Reason and Act) ⭐ NEW

**HOW IT WORKS:**
```
Reason (Analyze) → Act (Use Tool) → Observe (Review Result) → Reason (Next Step) → ...
```

The agent alternates between reasoning about what to do next, acting via tool calls, and observing results in explicit loops until the task completes.

**WHY IT WORKS:**
- Externalizes reasoning for audit trails (you can see agent's thought process)
- Reduces hallucinations (grounded in observations)
- Clear loop structure (easier to debug)
- Self-correcting (bad actions trigger re-reasoning)

**USE CASES:**
- **Research Tasks**: Search → Analyze results → Identify gaps → Search again
- **Debugging**: Check logs → Hypothesize cause → Test fix → Verify result
- **Data Analysis**: Query data → Examine → Form hypothesis → Query deeper
- **Our Project**: Our current <thinking> tags + tool use pattern IS ReAct!

**EXAMPLE FROM OUR PROJECT:**
```
<thinking>
REASON: User wants to fix a bug. Need to read the file first to understand the issue.
</thinking>

<read_file>  <!-- ACT -->
<path>module.py</path>
</read_file>

[User provides file contents]  <!-- OBSERVE -->

<thinking>
REASON: Found the bug on line 42. Need to use replace_in_file to fix it.
</thinking>

<replace_in_file>  <!-- ACT -->
...
</replace_in_file>
```

**TRADE-OFFS:**
- ✅ Pros: Transparent, self-correcting, reduces hallucinations
- ❌ Cons: Can be costly (repeated LLM calls), slower than single-shot

**WHEN TO USE:**
- Tasks requiring multiple steps with uncertainty
- When you need audit trails of reasoning
- Situations where self-correction is valuable

**Source**: Machine Learning Mastery (Oct 2025) - Production pattern from Google/AWS deployments

---

### 2. Reflection Pattern (Reflexion)

**HOW IT WORKS:**
```
Execute → Self-Critique → Refine → Execute Again
```

The agent completes a task, then critiques its own output, identifies improvements, and iterates until quality thresholds are met.

**WHY IT WORKS:**
- Mimics human self-review process
- Catches errors before user sees them
- Improves output quality through iteration
- No human intervention needed for refinement

**USE CASES:**
- **Code Generation**: Write code → review for bugs → fix → re-review
- **Content Creation**: Draft document → critique clarity → revise → polish
- **Architecture Design**: Propose solution → identify weaknesses → redesign
- **Our Project**: Feng Shui system self-reflects on architecture quality

**EXAMPLE FROM OUR PROJECT:**
- **Gu Wu Reflection Engine** (`tools/guwu/reflection.py`)
  - Validates own predictions
  - Analyzes prediction accuracy
  - Tracks fix success rates
  - Auto-adjusts confidence thresholds
  - Meta-learning: System improves itself over time

**BENEFITS:**
- Higher quality outputs (iterative refinement)
- Reduced human review time
- Self-correcting systems
- Continuous improvement

---

### 3. Tool Use Pattern (Function Calling)

**HOW IT WORKS:**
```
Task → Identify Tools Needed → Execute Tools → Synthesize Results
```

The agent has access to external tools (APIs, databases, file systems) and decides which tools to use and when.

**WHY IT WORKS:**
- Extends capabilities beyond language model
- Access to real-time data and systems
- Can perform actions (not just generate text)
- Deterministic operations where needed

**USE CASES:**
- **Data Analysis**: Query database → process results → generate insights
- **System Operations**: Read files → analyze → modify → verify
- **API Integration**: Call external APIs → parse responses → take action
- **Our Project**: All Cline tool use (read_file, write_to_file, execute_command, etc.)

**EXAMPLE FROM OUR PROJECT:**
- **Knowledge Graph Builder**:
  - Uses `read_file` to load CSN metadata
  - Uses `execute_command` to run SQL queries
  - Uses `write_to_file` to save cache
  - Synthesizes results into graph visualization

**BENEFITS:**
- Real-world action capability
- Integration with existing systems
- Deterministic operations (databases, files)
- Verifiable results

---

### 4. Planning Pattern (Plan-and-Execute)

**HOW IT WORKS:**
```
Complex Task → Break Into Subtasks → Execute Step-by-Step → Track Progress
```

The agent decomposes complex problems into manageable subtasks, creates an execution plan, and tracks completion.

**WHY IT WORKS:**
- Prevents overwhelming complexity
- Enables checkpointing and recovery
- Clear progress tracking
- Allows parallelization where possible

**USE CASES:**
- **Software Development**: Feature request → design → implement → test → deploy
- **Project Management**: Goal → milestones → tasks → execution
- **Research**: Topic → questions → sources → synthesis → report
- **Our Project**: Work package breakdown in PROJECT_TRACKER.md

**EXAMPLE FROM OUR PROJECT:**
- **Feng Shui Work Packages**:
  - WP-001: IDataSource enhancement (2-3 hours)
  - WP-002: Data Products refactoring (1 hour)
  - WP-003: Knowledge Graph DI (1.5 hours)
  - Each broken into concrete steps
  - Dependencies tracked
  - Progress measurable

**BENEFITS:**
- Complex tasks become manageable
- Clear progress indicators
- Failure recovery (restart from checkpoint)
- Parallel execution opportunities

---

### 5. Multi-Agent Collaboration Pattern

**HOW IT WORKS:**
```
Task → Assign Specialists → Agents Collaborate → Synthesize Results
```

Multiple specialized agents work together, each handling their domain of expertise.

**WHY IT WORKS:**
- Division of labor (specialization)
- Parallel processing
- Expert knowledge in each domain
- Redundancy and validation

**USE CASES:**
- **Software Development**: Architect + Coder + Reviewer + Tester
- **Research**: Researcher + Writer + Editor + Fact-Checker
- **Business Analysis**: Data Analyst + Domain Expert + Report Writer
- **Our Project**: Could split Feng Shui + Gu Wu + Implementation agents

**POTENTIAL FOR OUR PROJECT:**
- **ArchitectAgent**: Validates design patterns
- **CodeAgent**: Implements features
- **TestAgent**: Writes/runs tests (Gu Wu)
- **ReviewAgent**: Quality gate enforcement (Feng Shui)
- **DocAgent**: Documentation maintenance

**BENEFITS:**
- Higher quality (multiple perspectives)
- Faster execution (parallel work)
- Specialization (expert agents)
- Validation (peer review)

---

### 6. Retrieval-Augmented Generation (RAG) Pattern

**HOW IT WORKS:**
```
Query → Retrieve Relevant Context → Generate Response with Context
```

The agent searches knowledge bases/documents before generating responses, ensuring accuracy and current information.

**WHY IT WORKS:**
- Overcomes training data cutoff
- Access to proprietary/recent information
- Grounds responses in facts
- Reduces hallucinations

**USE CASES:**
- **Documentation Q&A**: Search docs → find relevant sections → answer
- **Customer Support**: Search knowledge base → provide accurate answer
- **Code Assistance**: Search codebase → understand context → suggest
- **Our Project**: Knowledge vault + MCP memory integration

**EXAMPLE FROM OUR PROJECT:**
- **Knowledge Vault System** (`docs/knowledge/`):
  - 23 documents with [[wikilinks]]
  - INDEX.md for navigation
  - Search before answering questions
  - Prevents re-inventing solutions
  
- **MCP Memory Integration**:
  - Stores observations in knowledge graph
  - Retrieves past decisions and WHY
  - Prevents repeating mistakes
  - Cumulative learning over sessions

**BENEFITS:**
- Accurate responses (grounded in facts)
- No hallucinations (verifiable sources)
- Up-to-date information
- Institutional memory

---

### 7. Chain-of-Thought (Reasoning) Pattern

**HOW IT WORKS:**
```
Problem → Think Step-by-Step → Show Reasoning → Arrive at Answer
```

The agent explicitly shows its reasoning process, breaking down complex problems into logical steps.

**WHY IT WORKS:**
- Reduces reasoning errors
- Makes logic transparent
- Enables verification
- Improves complex problem-solving

**USE CASES:**
- **Math/Logic Problems**: Break down complex calculations
- **Debugging**: Step-through root cause analysis
- **Decision Making**: Evaluate options systematically
- **Our Project**: <thinking> tags before tool use

**EXAMPLE FROM OUR PROJECT:**
- **Mandatory <thinking> Tags**:
  ```
  <thinking>
  1. What information do I have?
  2. What tool is most appropriate?
  3. Do I have all required parameters?
  4. If not, should I ask user or infer?
  </thinking>
  ```

**BENEFITS:**
- Better reasoning quality
- Transparent logic (user can verify)
- Easier debugging
- Reduced errors

---

### 8. Iterative Refinement Pattern

**HOW IT WORKS:**
```
Initial Attempt → Get Feedback → Improve → Repeat Until Satisfactory
```

The agent makes multiple attempts, incorporating feedback to improve each iteration.

**WHY IT WORKS:**
- Perfection in first try is rare
- Feedback guides improvement
- Incremental progress towards goal
- Natural learning process

**USE CASES:**
- **Code Optimization**: Write → Profile → Optimize → Re-profile
- **UI Design**: Mockup → User feedback → Revise → Re-test
- **Architecture**: Propose → Review → Refine → Validate
- **Our Project**: User feedback loops throughout development

**EXAMPLE FROM OUR PROJECT:**
- **Knowledge Graph Visual Polish** (v3.17):
  - Iteration 1: Reduced spacing
  - Iteration 2: CSN default mode
  - Iteration 3: Expanded legend
  - Iteration 4: Fixed text readability (CRITICAL)
  - Iteration 5: Edge colors corrected
  - Iteration 6: Edge widths matched backend
  - Result: Perfect UX after 6 iterations

**BENEFITS:**
- High quality final output
- User satisfaction (their feedback incorporated)
- Learning from mistakes
- Progressive improvement

---

### 9. Sequential Workflows Pattern ⭐ NEW

**HOW IT WORKS:**
```
Step 1 → Step 2 → Step 3 → ... → Complete (predefined sequence)
```

The agent follows a fixed, predefined sequence of steps without dynamic adaptation.

**WHY IT WORKS:**
- Highly predictable (same input = same path)
- Cost-effective (no reasoning overhead)
- Fast execution (no decision-making delays)
- Easy to test and validate

**USE CASES:**
- **ETL Pipelines**: Extract → Transform → Load
- **Deployment Workflows**: Build → Test → Deploy
- **Data Processing**: Read → Validate → Process → Write
- **Our Project**: Feng Shui automated work package execution

**EXAMPLE FROM OUR PROJECT:**
- **Feng Shui Work Package Execution**:
  1. Run quality gate check
  2. Identify violations
  3. Generate work packages
  4. Execute fixes in sequence
  5. Re-run quality gate
  6. Report results

**TRADE-OFFS:**
- ✅ Pros: Fast, cheap, predictable, easy to debug
- ❌ Cons: No adaptation to context, can't handle exceptions dynamically

**WHEN TO USE:**
- Workflows are highly predictable
- Cost and speed are priorities over flexibility
- Tasks don't require dynamic decision-making

**Source**: Machine Learning Mastery (Oct 2025)

---

### 10. Human-in-the-Loop Pattern ⭐ NEW

**HOW IT WORKS:**
```
Agent Attempts → Escalate to Human (if uncertain/risky) → Human Decides → Agent Executes
```

The agent adds human oversight for high-stakes decisions, escalating from full automation for routine tasks.

**WHY IT WORKS:**
- Risk mitigation (humans review critical decisions)
- Trust building (users see and approve actions)
- Learning opportunity (feedback improves agent)
- Compliance (required for regulated industries)

**USE CASES:**
- **Financial Transactions**: Agent proposes → User approves
- **Code Deployment**: Agent builds → User reviews → Agent deploys
- **Customer Support**: Agent drafts response → Human reviews → Send
- **Our Project**: User approval for risky commands (requires_approval parameter)

**EXAMPLE FROM OUR PROJECT:**
```python
<execute_command>
<command>npm uninstall critical-package</command>
<requires_approval>true</requires_approval>  <!-- HUMAN-IN-THE-LOOP -->
</execute_command>
```

**ESCALATION LEVELS**:
1. **Full Automation**: Safe, routine operations (file reads, searches)
2. **Notify Human**: Execute but alert user (file writes, commits)
3. **Human Approval**: Wait for explicit permission (deletions, deployments)
4. **Human-Only**: Never automate (production database changes)

**TRADE-OFFS:**
- ✅ Pros: Risk mitigation, trust, compliance, learning
- ❌ Cons: Slower, requires human availability, can't fully automate

**WHEN TO USE:**
- High-stakes decisions (financial, security, compliance)
- Building user trust in new agent capabilities
- Legal/regulatory requirements
- Learning phase (gather human feedback)

**Source**: Machine Learning Mastery (Oct 2025)

---

## Pattern Combinations (Advanced)

Real-world systems often combine multiple patterns:

### Example 1: Our Feng Shui System
```
Planning (Work Packages)
    ↓
Tool Use (File analysis, git operations)
    ↓
Reflection (Self-critique architecture quality)
    ↓
Iterative Refinement (Fix issues until score > threshold)
```

**Result**: Autonomous architecture improvement engine

---

### Example 2: Our Gu Wu Testing Framework
```
Planning (Test pyramid strategy)
    ↓
Tool Use (pytest execution, coverage analysis)
    ↓
RAG (Learn from past test failures)
    ↓
Reflection (Validate own predictions)
    ↓
Iterative Refinement (Auto-adjust thresholds)
```

**Result**: Self-optimizing testing system

---

### Example 3: Potential Multi-Agent Enhancement
```
Planning Agent (Create work packages)
    ↓
Code Agent (Implement features)
    ↓
Test Agent (Gu Wu validation)
    ↓
Review Agent (Feng Shui quality gate)
    ↓
Doc Agent (Update knowledge vault)
```

**Result**: Complete autonomous development pipeline

---

## Implementation Guidelines

### Decision Framework (Machine Learning Mastery)

**Choose patterns based on three key questions:**

1. **Workflow Predictability**: Is the task sequence known in advance?
   - ✅ YES → Sequential Workflows (fast, cheap, predictable)
   - ❌ NO → ReAct or Planning (dynamic adaptation)

2. **Quality vs Speed Priority**: What matters more?
   - ✅ Quality → Add Reflection + Human-in-the-Loop
   - ✅ Speed → Sequential Workflows + minimal reasoning

3. **Task Complexity**: How complex is the problem?
   - 🔴 HIGH → Multi-Agent + Planning (specialized handling)
   - 🟡 MEDIUM → ReAct + Tool Use (iterative problem-solving)
   - 🟢 LOW → Sequential Workflows (straight execution)

**Cost Optimization Strategy**:
- Use capable model (GPT-4) for planning
- Use cheaper models (GPT-3.5) for execution steps
- Result: Up to 90% cost reduction while maintaining quality

**Start Simple, Add Complexity**:
1. Start with ReAct + Tool Use
2. Add Planning if tasks are complex
3. Add Reflection if quality is critical
4. Add Multi-Agent if specialization needed
5. Monitor: cost, latency, reliability, observability

**Source**: Machine Learning Mastery (Oct 2025) - Production patterns from Google/AWS

---

### When to Use Each Pattern

| Pattern | Best For | Avoid When | Cost | Speed |
|---------|----------|------------|------|-------|
| **ReAct** | Multi-step tasks with uncertainty | Simple lookups | Medium | Medium |
| **Reflection** | Quality-critical tasks | Time-sensitive ops | High | Slow |
| **Tool Use** | System interactions | Pure reasoning | Low | Fast |
| **Planning** | Complex multi-step tasks | Simple single-step | Medium | Medium |
| **Multi-Agent** | Specialized domains | Simple tasks | High | Fast (parallel) |
| **RAG** | Knowledge-intensive tasks | Creative generation | Low | Fast |
| **Chain-of-Thought** | Complex reasoning | Simple lookups | Medium | Medium |
| **Iterative Refinement** | Perfectionist tasks | One-shot requirements | High | Slow |
| **Sequential** | Predictable workflows | Dynamic tasks | Very Low | Very Fast |
| **Human-in-Loop** | High-stakes decisions | Fully automated ops | Low | Slow |

---

### Success Criteria

**Good Agentic System:**
- ✅ Autonomous decision-making
- ✅ Self-correction capability
- ✅ Transparent reasoning
- ✅ Measurable progress
- ✅ Graceful degradation

**Bad Agentic System:**
- ❌ Requires constant human intervention
- ❌ No error recovery
- ❌ Opaque decision-making
- ❌ No progress tracking
- ❌ Fragile (breaks easily)

---

## Our Project's Agentic Capabilities

**Current Implementation:**

| Pattern | Implementation | Maturity |
|---------|---------------|----------|
| **ReAct** | <thinking> tags + tool use loops | ✅ Production |
| **Reflection** | Gu Wu Reflection Engine | ✅ Production |
| **Tool Use** | Complete Cline toolset (10+ tools) | ✅ Production |
| **Planning** | PROJECT_TRACKER.md work packages | ✅ Production |
| **Multi-Agent** | Not implemented | ⏳ Future |
| **RAG** | Knowledge Vault + MCP memory | ✅ Production |
| **Chain-of-Thought** | Mandatory <thinking> tags | ✅ Production |
| **Iterative Refinement** | User feedback loops | ✅ Production |
| **Sequential** | Feng Shui automated fixes | ✅ Production |
| **Human-in-Loop** | requires_approval parameter | ✅ Production |

**Strengths:**
- ✅ **9/10 patterns implemented** (only Multi-Agent missing!)
- ✅ ReAct workflow with explicit reasoning loops
- ✅ Strong tool use capabilities (10+ tools)
- ✅ Excellent reflection (Gu Wu + Feng Shui)
- ✅ Production RAG (knowledge vault + MCP)
- ✅ Solid planning (work packages + dependencies)
- ✅ Sequential automation (Feng Shui fixes)
- ✅ Risk mitigation (requires_approval for dangerous ops)

**Opportunities:**
- Multi-agent collaboration (future enhancement)
- More sophisticated planning (dependency graphs)
- Stronger chain-of-thought (always show reasoning)

---

## Weaviate/Elysia Framework Insights (Feb 2026 Research)

**Context Engineering for AI Agents**:

Weaviate's Elysia framework introduces advanced agentic patterns specifically for RAG systems:

### Three Pillars of Context Engineering

1. **Tool Discovery**: Agent must know available tools
   - Built-in tools: `query`, `aggregate`, `text_response`, `cited_summarize`, `visualize`
   - Domain-specific tools: `weaviate_list_collections`, `weaviate_upsert`, `weaviate_delete`
   - Global context awareness via `preprocess()` for schema analysis

2. **Tool Selection and Planning**: Decide which tool for each step
   - Decision-tree architecture evaluates environment, tools, past actions
   - Automatic collection selection based on query semantics
   - Dynamic filter generation (e.g., date ranges, categories)

3. **Execution and Observation**: Run tool + review results
   - Thought-Action-Observation cycle for each tool
   - Post-execution review: Success? Iterate? Switch strategy?
   - Feedback loop enables self-correction

**Real-World Agent Example** (News Search):
```python
from elysia import configure, preprocess

# 1. PREPROCESS: Global schema analysis (once)
preprocess(["NewsArchive", "ResearchPapers"])

# 2. AGENT WORKFLOW:
# User: "Find articles about AI agents published this week"
# 
# THOUGHT: Need recent articles about AI agents
# ACTION: query(collection="NewsArchive", 
#               filters={"publishDate": ">2026-01-30"},
#               search="AI agents")
# OBSERVATION: Found 15 articles
# THOUGHT: User wants summary
# ACTION: cited_summarize(articles)
# OBSERVATION: Summary generated with citations
# RESULT: Delivered to user
```

**Why Elysia Pattern Works**:
- ✅ **Global Context**: `preprocess()` analyzes schemas once, infers relationships
- ✅ **5 Built-in Tools**: Cover 90% of RAG use cases
- ✅ **Decision Tree**: Dynamic evaluation prevents tool confusion
- ✅ **Reflection Loop**: Each action reviewed before proceeding
- ✅ **Multi-Modal**: Supports text, images, structured data

**Integration with Our Patterns**:
- Elysia Reflection = Our Gu Wu Reflection Engine
- Elysia Tool Use = Our Cline toolset
- Elysia Planning = Our PROJECT_TRACKER.md work packages
- Elysia RAG = Our Knowledge Vault + MCP memory

**Source**: Weaviate Context Engineering blog (Dec 2025)

---

## Key Takeaways

1. **Agentic workflows enable autonomy**: AI moves from Q&A → problem-solving
2. **Multiple patterns work together**: Real systems combine 3-5 patterns
3. **ReAct is the foundation**: Reason → Act → Observe loop drives modern agents
4. **Reflection is critical**: Self-critique improves quality dramatically
5. **Tool use extends capabilities**: Real-world actions, not just text generation
6. **Planning enables complexity**: Break down → conquer → synthesize
7. **Thought-Action-Observation**: Core cycle from Weaviate/Elysia research
8. **Context Engineering**: Tool discovery + selection + execution = smarter agents
9. **Decision framework**: Choose based on predictability, quality needs, complexity
10. **Cost optimization**: Capable model for planning + cheap models for execution = 90% savings
11. **Start simple**: ReAct + Tools first, add complexity only when needed
12. **Our project uses 9/10 patterns**: Already a sophisticated production-ready agentic system!

**Production Validation**: All patterns validated by Google, AWS, and industry deployments

---

## References

- **Gu Wu Testing Framework**: Self-reflection + iterative refinement
- **Feng Shui Architecture Engine**: Reflection + tool use + planning
- **Knowledge Vault**: RAG pattern for institutional memory
- **PROJECT_TRACKER.md**: Planning pattern with work packages
- **.clinerules**: Defines workflow patterns and standards

---

## Next Steps for Enhanced Agentic Capabilities

**Short-Term (Phases 4.13-4.14)**:
1. CI/CD Integration: Automated planning + tool use
2. Web Dashboard: Real-time monitoring + reflection visibility

**Long-Term (Future)**:
3. Multi-Agent System: Specialized agents for architecture/code/tests/docs
4. Advanced Planning: Dependency graphs, parallel execution
5. Stronger Reflection: Formal verification of decisions

---

**Status**: Production-ready agentic system with 6/7 patterns implemented  
**Transformation**: Single-shot responses → Autonomous problem-solving  
**Philosophy**: "AI that thinks, plans, acts, and improves itself"