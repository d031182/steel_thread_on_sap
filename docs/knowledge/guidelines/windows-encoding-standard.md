# Windows Encoding Standard

**Status**: MANDATORY  
**Applies To**: All Python scripts  
**Problem**: Windows cp1252 encoding cannot handle Unicode characters (✓, ✗, →, etc.)

---

## The Problem

**Symptom**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2717' 
in position 3: character maps to <undefined>
```

**Root Cause**:
- Windows console defaults to cp1252 encoding
- cp1252 cannot encode Unicode characters
- Python scripts crash when printing ✓, ✗, →, etc.

**Impact**:
- ❌ Wasted time debugging same issue repeatedly
- ❌ Scripts fail in production
- ❌ Poor user experience

---

## The Solution

**MANDATORY for ALL Python scripts**:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Description
"""

import sys
import io

# Fix Windows encoding issue (cp1252 → utf-8)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Rest of imports...
```

**Place this IMMEDIATELY after imports, BEFORE any other code.**

---

## When to Apply

**REQUIRED**:
- ✅ ALL new Python scripts
- ✅ ANY script that prints to console
- ✅ Scripts using Unicode characters (✓, ✗, →, ⚠️, etc.)
- ✅ Test scripts, utility scripts, migration scripts

**Enforcement**:
- Code review must check for this pattern
- AI assistants must add this automatically
- No exceptions

---

## Quality Check

Before committing any Python script, verify:

1. ✅ Has `# -*- coding: utf-8 -*-` at top
2. ✅ Has encoding fix after imports
3. ✅ Test runs successfully on Windows

---

## Why This Matters

**Time Math**:
- Fix once (5 seconds) vs. Debug repeatedly (5-30 minutes each time)
- One standard prevents 100+ future issues
- Zero tolerance for recurring problems

**User Impact**:
- Scripts work reliably
- Professional output
- No encoding errors ever again

---

## MCP Memory Entry

Store this in knowledge graph:

```json
{
  "name": "Windows_Encoding_Standard",
  "entityType": "quality-standard",
  "observations": [
    "WHAT: All Python scripts must fix Windows cp1252 encoding",
    "WHY: Windows console can't handle Unicode (✓, ✗, →)",
    "HOW: Add encoding fix after imports (see template)",
    "ENFORCEMENT: Mandatory - no exceptions",
    "CONSEQUENCE: Scripts crash without this fix",
    "TIME_COST: 5 seconds to add, 30 minutes to debug if missing",
    "APPLIES_TO: All Python scripts that print to console",
    "TEMPLATE: See windows-encoding-standard.md"
  ]
}
```

---

## Template

Copy-paste this into every new Python script:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[Script Description]
"""

import sys
import io

# Fix Windows encoding issue (cp1252 → utf-8)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Your imports here
from pathlib import Path
# ...

def main():
    # Your code here
    print("✓ Works on Windows now!")
    
if __name__ == '__main__':
    main()
```

---

## Related Standards

- [[Python Coding Standards]]
- [[Quality Culture]]
- [[Zero Defects Philosophy]]

**Remember**: Fix once, benefit forever. No more encoding issues.