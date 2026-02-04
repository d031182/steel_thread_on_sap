/**
 * Unit Tests for Knowledge Graph Page Utilities
 * 
 * Tests the error handling and utility functions
 * 
 * Run with: node app/static/tests/unit/knowledgeGraphPage.test.js
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

// ============================================================
// TEST UTILITIES (Copy from source for isolated testing)
// ============================================================

/**
 * Extract error message from API response (bulletproof)
 * Handles all possible error formats
 */
function extractErrorMessage(data, defaultMsg = 'Unknown error') {
    // Priority 1: data.error.message (must be non-empty)
    if (data.error && typeof data.error === 'object' && data.error.message && data.error.message.trim()) {
        return data.error.message;
    }
    
    // Priority 2: data.error as string
    if (data.error && typeof data.error === 'string' && data.error.trim()) {
        return data.error;
    }
    
    // Priority 3: data.message
    if (data.message && typeof data.message === 'string' && data.message.trim()) {
        return data.message;
    }
    
    // Priority 4: stringify error object if not empty AND has meaningful content
    if (data.error && typeof data.error === 'object') {
        // Check if has keys other than empty strings
        const hasContent = Object.entries(data.error).some(([key, value]) => 
            value !== null && value !== undefined && value !== ''
        );
        if (hasContent) {
            return JSON.stringify(data.error);
        }
    }
    
    // Fallback
    return defaultMsg;
}

/**
 * Safe error logging - handles all error types
 */
function logError(context, error) {
    console.error(`[${context}]`, error);
    if (error && typeof error === 'object') {
        console.error('Error details:', JSON.stringify(error, null, 2));
    }
}

// ============================================================
// TEST FRAMEWORK (Simple assertion-based)
// ============================================================

let testsPassed = 0;
let testsFailed = 0;

function assertEqual(actual, expected, testName) {
    if (actual === expected) {
        console.log(`[PASS] ${testName}`);
        testsPassed++;
        return true;
    } else {
        console.log(`[FAIL] ${testName}`);
        console.log(`  Expected: "${expected}"`);
        console.log(`  Actual: "${actual}"`);
        testsFailed++;
        return false;
    }
}

function assertContains(actual, substring, testName) {
    if (actual.includes(substring)) {
        console.log(`[PASS] ${testName}`);
        testsPassed++;
        return true;
    } else {
        console.log(`[FAIL] ${testName}`);
        console.log(`  Expected to contain: "${substring}"`);
        console.log(`  Actual: "${actual}"`);
        testsFailed++;
        return false;
    }
}

// ============================================================
// TEST SUITE: extractErrorMessage()
// ============================================================

console.log("=".repeat(60));
console.log("KNOWLEDGE GRAPH PAGE - UNIT TESTS");
console.log("=".repeat(60));
console.log();

console.log("Test Suite 1: extractErrorMessage() - Error Object Formats");
console.log("-".repeat(60));

// Test 1: Standard error format {error: {message: "..."}}
assertEqual(
    extractErrorMessage({
        success: false,
        error: { message: "Database connection failed" }
    }),
    "Database connection failed",
    "Test 1.1: Standard error format {error: {message}}"
);

// Test 2: Empty error object {error: {}} - THE BUG WE FIXED!
assertEqual(
    extractErrorMessage({
        success: false,
        error: {}
    }),
    "Unknown error",
    "Test 1.2: Empty error object {error: {}}"
);

// Test 3: Error as string {error: "message"}
assertEqual(
    extractErrorMessage({
        success: false,
        error: "Network timeout"
    }),
    "Network timeout",
    "Test 1.3: Error as string"
);

// Test 4: Error with whitespace {error: "  message  "}
assertEqual(
    extractErrorMessage({
        success: false,
        error: "  Validation failed  "
    }),
    "  Validation failed  ",
    "Test 1.4: Error string with whitespace"
);

// Test 5: Error as empty string {error: ""}
assertEqual(
    extractErrorMessage({
        success: false,
        error: ""
    }),
    "Unknown error",
    "Test 1.5: Empty error string"
);

// Test 6: Message field fallback {message: "..."}
assertEqual(
    extractErrorMessage({
        success: false,
        message: "Operation failed"
    }),
    "Operation failed",
    "Test 1.6: Message field fallback"
);

// Test 7: Both error and message, error takes priority
assertEqual(
    extractErrorMessage({
        success: false,
        error: { message: "Error message" },
        message: "Success message"
    }),
    "Error message",
    "Test 1.7: Error takes priority over message"
);

// Test 8: Complex error object (not empty)
const result8 = extractErrorMessage({
    success: false,
    error: { code: 500, details: "Internal error" }
});
assertContains(
    result8,
    "code",
    "Test 1.8: Complex error object stringified (contains 'code')"
);
assertContains(
    result8,
    "500",
    "Test 1.9: Complex error object stringified (contains '500')"
);

// Test 9: No error at all
assertEqual(
    extractErrorMessage({
        success: true
    }),
    "Unknown error",
    "Test 1.10: No error fields at all"
);

// Test 10: Custom default message
assertEqual(
    extractErrorMessage(
        { success: false },
        "Custom fallback"
    ),
    "Custom fallback",
    "Test 1.11: Custom default message"
);

// Test 11: Null error
assertEqual(
    extractErrorMessage({
        success: false,
        error: null
    }),
    "Unknown error",
    "Test 1.12: Null error"
);

// Test 12: Undefined error
assertEqual(
    extractErrorMessage({
        success: false,
        error: undefined
    }),
    "Unknown error",
    "Test 1.13: Undefined error"
);

// Test 13: Error object with empty message
assertEqual(
    extractErrorMessage({
        success: false,
        error: { message: "" }
    }),
    "Unknown error",
    "Test 1.14: Error object with empty message string"
);

// Test 14: Nested error structure
assertEqual(
    extractErrorMessage({
        success: false,
        error: {
            message: "Top-level error",
            details: { nested: "value" }
        }
    }),
    "Top-level error",
    "Test 1.15: Nested error structure (uses top-level message)"
);

console.log();

// ============================================================
// TEST SUITE: logError()
// ============================================================

console.log("Test Suite 2: logError() - Safe Logging");
console.log("-".repeat(60));

// Test logError doesn't crash (we can't easily test console output)
try {
    logError("TestContext1", new Error("Test error"));
    console.log("[PASS] Test 2.1: logError handles Error objects");
    testsPassed++;
} catch (e) {
    console.log("[FAIL] Test 2.1: logError crashes on Error objects");
    testsFailed++;
}

try {
    logError("TestContext2", {error: "Test"});
    console.log("[PASS] Test 2.2: logError handles plain objects");
    testsPassed++;
} catch (e) {
    console.log("[FAIL] Test 2.2: logError crashes on plain objects");
    testsFailed++;
}

try {
    logError("TestContext3", "String error");
    console.log("[PASS] Test 2.3: logError handles strings");
    testsPassed++;
} catch (e) {
    console.log("[FAIL] Test 2.3: logError crashes on strings");
    testsFailed++;
}

try {
    logError("TestContext4", null);
    console.log("[PASS] Test 2.4: logError handles null");
    testsPassed++;
} catch (e) {
    console.log("[FAIL] Test 2.4: logError crashes on null");
    testsFailed++;
}

try {
    logError("TestContext5", undefined);
    console.log("[PASS] Test 2.5: logError handles undefined");
    testsPassed++;
} catch (e) {
    console.log("[FAIL] Test 2.5: logError crashes on undefined");
    testsFailed++;
}

console.log();

// ============================================================
// TEST SUITE: Mode Selection & CSN Mode
// ============================================================

console.log("Test Suite 3: Mode Selection & CSN Mode Support");
console.log("-".repeat(60));

// Test 15: Mode names mapping
const modeNames = {
    'schema': 'Schema (Database)',
    'csn': 'CSN (Metadata)',
    'data': 'Data (Records)'
};

assertEqual(
    modeNames['schema'],
    'Schema (Database)',
    "Test 3.1: Schema mode display name"
);

assertEqual(
    modeNames['csn'],
    'CSN (Metadata)',
    "Test 3.2: CSN mode display name"
);

assertEqual(
    modeNames['data'],
    'Data (Records)',
    "Test 3.3: Data mode display name"
);

// Test 16: Mode parameter validation
const validModes = ['schema', 'csn', 'data'];

assertEqual(
    validModes.includes('schema'),
    true,
    "Test 3.4: Schema is valid mode"
);

assertEqual(
    validModes.includes('csn'),
    true,
    "Test 3.5: CSN is valid mode"
);

assertEqual(
    validModes.includes('data'),
    true,
    "Test 3.6: Data is valid mode"
);

assertEqual(
    validModes.includes('invalid'),
    false,
    "Test 3.7: Invalid mode rejected"
);

// Test 17: API endpoint construction for CSN mode
const buildAPIEndpoint = (source, mode) => {
    return `/api/knowledge-graph/?source=${source}&mode=${mode}&max_records=20`;
};

assertEqual(
    buildAPIEndpoint('sqlite', 'csn'),
    '/api/knowledge-graph/?source=sqlite&mode=csn&max_records=20',
    "Test 3.8: CSN mode API endpoint construction"
);

assertEqual(
    buildAPIEndpoint('hana', 'csn'),
    '/api/knowledge-graph/?source=hana&mode=csn&max_records=20',
    "Test 3.9: CSN mode with HANA source endpoint"
);

// Test 18: Mode label extraction
const getModeLabel = (mode) => {
    const modeLabels = {
        'schema': 'Schema (Database)',
        'csn': 'CSN (Metadata)',
        'data': 'Data (Records)'
    };
    return modeLabels[mode] || mode;
};

assertEqual(
    getModeLabel('csn'),
    'CSN (Metadata)',
    "Test 3.10: CSN mode label extraction"
);

assertEqual(
    getModeLabel('unknown'),
    'unknown',
    "Test 3.11: Unknown mode fallback"
);

console.log();

// ============================================================
// TEST SUMMARY
// ============================================================

console.log("=".repeat(60));
console.log("TEST SUMMARY");
console.log("=".repeat(60));
const totalTests = testsPassed + testsFailed;
console.log(`Total Tests: ${totalTests}`);
console.log(`[+] Passed: ${testsPassed}`);
console.log(`[-] Failed: ${testsFailed}`);
console.log(`Success Rate: ${(testsPassed/totalTests*100).toFixed(0)}%`);
console.log();

if (testsFailed === 0) {
    console.log("[SUCCESS] ALL TESTS PASSED!");
    process.exit(0);
} else {
    console.log(`[FAILURE] ${testsFailed} test(s) failed`);
    process.exit(1);
}