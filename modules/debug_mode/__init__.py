"""
Debug Mode Module
================
Enhanced debugging with verbose logging and performance tracking.

Quick Start:
    import { debugLogger } from './modules/debug_mode/frontend/debugLogger.js';
    
    // Enable debug mode
    debugLogger.enable();
    
    // Log messages
    debugLogger.log('Debug message', { data: 'value' });
    
    // Trace function calls
    const start = debugLogger.entry('myFunction', { param: 'value' });
    // ... function logic ...
    debugLogger.exit('myFunction', result, start);

Features:
- Conditional logging (only when enabled)
- LocalStorage persistence
- Function entry/exit tracing
- Performance timers
- Object inspection
- Colored console output

Author: P2P Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'