# Testing Guide for P2P Data Products

This document describes the testing infrastructure and how to run different types of tests.

## 📋 Overview

We use a **multi-layered testing approach** for comprehensive quality assurance:

1. **API Tests** (Node.js + jsdom) - Business logic testing
2. **OPA5 Tests** (SAP UI5) - Component-level UI testing
3. **Playwright Tests** (E2E) - End-to-end user workflow testing

## 🎯 Testing Pyramid

```
        /\
       /  \      E2E Tests (Playwright)
      /____\     - Full user workflows
     /      \    - Cross-browser testing
    /________\   - Performance testing
   /          \  
  /____________\ UI Component Tests (OPA5)
 /              \- SAP UI5 controls
/________________\- User interactions
                  - Page navigation

   API/Unit Tests (Node.js)
   - Business logic
   - Data transformation
   - API contracts
```

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
npm run playwright:install
```

### Run All Tests

```bash
npm run test:all
```

### Run Specific Test Suites

```bash
# API tests only
npm run test:api

# OPA5 UI component tests
npm run test:ui

# Playwright E2E tests
npm run test:e2e
```

## 📦 Test Structure

```
app/static/tests/
├── README.md                           # This file
├── run-all-tests.js                    # API test runner
├── *API.test.js                        # API/Unit tests (Node.js + jsdom)
├── opa5/                               # SAP UI5 component tests
│   ├── dataProductsPage.opa5.test.html # OPA5 test page
│   └── dataProductsPage.opa5.test.js   # OPA5 test implementation
└── e2e/                                # End-to-end tests
    └── dataProducts.spec.js            # Playwright E2E tests
```

## 1️⃣ API Tests (Node.js + jsdom)

### Purpose
Test business logic, APIs, and data transformation **without a browser**.

### Technology
- **Node.js** - JavaScript runtime
- **jsdom** - DOM simulation
- **Custom test runner** - Lightweight, fast

### When to Use
- ✅ Testing API methods
- ✅ Data transformation logic
- ✅ Validating API contracts
- ✅ Quick feedback during development

### Running API Tests

```bash
npm run test:api
# or
node app/static/tests/run-all-tests.js
```

### Example Test Structure

```javascript
async function testDataProductsAPI() {
    console.log('Testing DataProductsAPI...');
    
    const api = new DataProductsAPI();
    await api.initialize();
    
    const result = await api.getAvailableProducts();
    
    assert(result.rows.length > 0, 'Should return product rows');
    assert(result.columns.length > 0, 'Should return columns');
    
    console.log('✓ All DataProductsAPI tests passed');
}
```

### Coverage
- ✅ dataProductsAPI.test.js
- ✅ hanaConnectionAPI.test.js
- ✅ sqlExecutionAPI.test.js
- ✅ logViewerAPI.test.js
- ✅ resultFormatterAPI.test.js
- ✅ debugLogger.test.js

## 2️⃣ OPA5 Tests (SAP UI5 Component Testing)

### Purpose
Test SAP UI5 **controls, user interactions, and component behavior**.

### Technology
- **OPA5** (One Page Acceptance) - SAP's official UI5 testing framework
- **QUnit** - Test framework
- **SAP UI5 SDK** - Loaded from CDN

### When to Use
- ✅ Testing SAP UI5 controls (Table, List, Button, etc.)
- ✅ User interaction flows (click, type, select)
- ✅ Page navigation within UI5
- ✅ Control properties and state
- ✅ SAP-specific functionality

### Running OPA5 Tests

**Option 1: Command Line (Headless)**
```bash
npm run test:ui
```

**Option 2: Browser (Visual)**
```
1. Start server: python server.py
2. Open: http://localhost:5000/app/static/tests/opa5/dataProductsPage.opa5.test.html
3. View results in browser
```

### Example OPA5 Test

```javascript
opaTest("Should load Data Products page with table", function(Given, When, Then) {
    // Arrangement
    Given.iStartMyAppInAFrame("../../index.html#/dataProducts");

    // Action
    When.waitFor({
        controlType: "sap.ui.table.Table",
        success: function(aTables) {
            Opa5.assert.ok(aTables.length > 0, "Table found");
        }
    });

    // Assertion
    Then.waitFor({
        controlType: "sap.ui.table.Table",
        success: function(aTables) {
            Opa5.assert.ok(aTables[0].getRows().length > 0, "Table has rows");
        }
    });

    // Cleanup
    Then.iTeardownMyApp();
});
```

### Coverage
- ✅ Page loading
- ✅ Table display and columns
- ✅ Search/filter functionality
- ✅ Row selection
- ✅ Button states
- ✅ Loading indicators

## 3️⃣ Playwright Tests (E2E Testing)

### Purpose
Test **complete user workflows** across **real browsers**.

### Technology
- **Playwright** - Modern E2E testing framework by Microsoft
- **Multi-browser** - Chromium, Firefox, WebKit
- **Mobile simulation** - Test responsive design

### When to Use
- ✅ Full user journeys (login → navigate → action → verify)
- ✅ Cross-browser compatibility
- ✅ Performance testing
- ✅ Mobile responsiveness
- ✅ Integration between components
- ✅ Real network conditions

### Running Playwright Tests

**Run all E2E tests:**
```bash
npm run test:e2e
```

**Run specific browser:**
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

**Run specific test file:**
```bash
npx playwright test app/static/tests/e2e/dataProducts.spec.js
```

**Run in headed mode (see browser):**
```bash
npx playwright test --headed
```

**Debug mode:**
```bash
npx playwright test --debug
```

**Generate report:**
```bash
npx playwright show-report app/static/tests/e2e/playwright-report
```

### Example Playwright Test

```javascript
test('should navigate to Data Products page when tile is clicked', async ({ page }) => {
    // Navigate to home
    await page.goto('/');
    
    // Click tile
    await page.click('text=Data Products');
    
    // Verify navigation
    await page.waitForURL('**/index.html#/dataProducts');
    
    // Check page title
    const pageTitle = page.locator('.sapMPageHeader .sapMTitle');
    await expect(pageTitle).toContainText('Data Products');
});
```

### Coverage
- ✅ Home page navigation
- ✅ Tile click navigation
- ✅ Data table display
- ✅ Search/filter
- ✅ Row selection
- ✅ Export functionality
- ✅ Mobile responsiveness
- ✅ Performance budgets
- ✅ API integration
- ✅ Error handling

### Browser Coverage
- ✅ Desktop Chrome (Chromium)
- ✅ Desktop Firefox
- ✅ Desktop Safari (WebKit)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

## 📊 Test Comparison Matrix

| Feature | API Tests | OPA5 Tests | Playwright E2E |
|---------|-----------|------------|----------------|
| **Speed** | ⚡ Fastest (< 5s) | 🚀 Fast (10-30s) | 🐢 Slower (30s-2min) |
| **Isolation** | ✅ High | ⚠️ Medium | ❌ Low |
| **Real Browser** | ❌ No (jsdom) | ✅ Yes | ✅ Yes |
| **Cross-browser** | ❌ No | ❌ No | ✅ Yes |
| **UI5 Controls** | ❌ Limited | ✅ Full | ⚠️ Black-box |
| **User Interactions** | ❌ Simulated | ✅ Real | ✅ Real |
| **Debugging** | ✅ Easy | ⚠️ Medium | ✅ Good |
| **CI/CD Friendly** | ✅ Yes | ⚠️ Requires setup | ✅ Yes |
| **Mobile Testing** | ❌ No | ❌ No | ✅ Yes |

## 🎯 Testing Best Practices

### 1. Test Naming Convention
```javascript
// API Tests
async function testMethodName() { ... }

// OPA5 Tests
opaTest("Should do something when action occurs", ...)

// Playwright Tests
test('should do something when action occurs', ...)
```

### 2. Test Organization
- **Arrange** - Set up test data and state
- **Act** - Perform the action being tested
- **Assert** - Verify the outcome
- **Cleanup** - Reset state (especially OPA5)

### 3. Use Proper Selectors
```javascript
// ❌ Bad - Fragile
page.locator('div > span:nth-child(3)')

// ✅ Good - Semantic
page.locator('[data-testid="export-button"]')
page.locator('text=Export')
page.locator('button[title="Export to Excel"]')
```

### 4. Handle Async Properly
```javascript
// Always await Playwright actions
await page.click('button');
await page.waitForSelector('.table');

// Use waitFor in OPA5
When.waitFor({
    controlType: "sap.m.Button",
    success: function() { ... }
});
```

### 5. Test Isolation
Each test should be **independent** and **repeatable**.

```javascript
test.beforeEach(async ({ page }) => {
    // Reset state before each test
    await page.goto('/');
});

test.afterEach(async ({ page }) => {
    // Clean up after each test
    await page.close();
});
```

## 🐛 Debugging Tests

### API Tests
```bash
# Add console.log statements
console.log('Result:', result);

# Run single test file
node app/static/tests/dataProductsAPI.test.js
```

### OPA5 Tests
1. Open test page in browser
2. Open browser DevTools (F12)
3. Check Console tab for errors
4. Use QUnit UI to run specific tests

### Playwright Tests
```bash
# Debug mode (step through)
npx playwright test --debug

# Headed mode (see browser)
npx playwright test --headed

# UI mode (interactive)
npx playwright test --ui

# Trace viewer (after test run)
npx playwright show-trace trace.zip
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run playwright:install
      - run: npm run test:all
```

## 📚 Additional Resources

### SAP UI5 / OPA5
- [OPA5 Documentation](https://sdk.openui5.org/topic/2696ab50faad458f9b4027ec2f9b884d)
- [UI5 Testing Guide](https://sdk.openui5.org/topic/291c9121e6044ab381e0b51716f97f52)

### Playwright
- [Playwright Documentation](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)

### General Testing
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

## 🎓 Quick Command Reference

```bash
# Install dependencies
npm install
npm run playwright:install

# Run tests
npm run test:all          # All tests
npm run test:api          # API tests only
npm run test:ui           # OPA5 tests only
npm run test:e2e          # Playwright tests only

# Playwright specific
npx playwright test                        # Run all E2E tests
npx playwright test --headed               # See browser
npx playwright test --debug                # Debug mode
npx playwright test --ui                   # Interactive UI
npx playwright test --project=chromium     # Specific browser
npx playwright show-report                 # View HTML report
npx playwright codegen http://localhost:5000  # Record test
```

## ✅ Testing Checklist

Before committing code:

- [ ] All API tests pass (`npm run test:api`)
- [ ] OPA5 tests pass (browser or CLI)
- [ ] Playwright tests pass (`npm run test:e2e`)
- [ ] Tests cover new functionality
- [ ] Tests are independent and repeatable
- [ ] No commented-out tests
- [ ] Test names are descriptive

---

**Version:** 1.0  
**Last Updated:** 2026-01-29  
**Maintained by:** P2P Development Team