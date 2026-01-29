# Automated UI Testing for SAP UI5

**Type**: Guideline  
**Category**: Quality Assurance  
**Created**: 2026-01-29  
**Status**: Active

## Overview

Industry-standard automated UI testing approach for SAP UI5 applications, eliminating need for manual browser testing. This document provides a complete testing strategy using **OPA5** (SAP UI5 native) and **Playwright** (modern E2E) for comprehensive coverage.

## Related Documentation

- [[Testing Standards]] - Overall testing pyramid
- [[SAP Fiori Design Standards]] - UI patterns to test
- [[Modular Architecture]] - Testing modular components

## The Problem

**Current State**: Manual browser testing required
- ❌ Human opens browser
- ❌ Human clicks tiles
- ❌ Human verifies results
- ❌ Slow (5-10 minutes per test cycle)
- ❌ Error-prone (humans miss edge cases)
- ❌ Not repeatable

**Desired State**: Automated testing
- ✅ Tests run in CI/CD pipeline
- ✅ Complete coverage in < 1 minute
- ✅ Catches regressions immediately
- ✅ Runs on every commit
- ✅ Zero human interaction

## Industry Best Practices for SAP UI5

### 1. OPA5 (One Page Acceptance) - SAP Standard ⭐ RECOMMENDED

**What**: SAP UI5's built-in integration testing framework  
**When**: Testing UI5 controls, interactions, workflows  
**Why**: Native support, control awareness, recommended by SAP

**Advantages**:
- ✅ Built into SAPUI5 framework
- ✅ Understands UI5 controls natively
- ✅ Async-aware (waits for controls automatically)
- ✅ Page Object pattern support
- ✅ Used by SAP internally
- ✅ Extensive documentation

**Example: Testing Data Products Tile Click**:
```javascript
// test/integration/pages/DataProducts.js
sap.ui.define([
    "sap/ui/test/Opa5",
    "sap/ui/test/actions/Press",
    "sap/ui/test/matchers/Properties"
], function(Opa5, Press, Properties) {
    "use strict";

    Opa5.createPageObjects({
        onTheDataProductsPage: {
            actions: {
                iClickDataProductTile: function(productName) {
                    return this.waitFor({
                        controlType: "sap.m.GenericTile",
                        matchers: new Properties({
                            header: productName
                        }),
                        actions: new Press(),
                        errorMessage: "Could not find tile: " + productName
                    });
                },
                
                iCloseTheDialog: function() {
                    return this.waitFor({
                        controlType: "sap.m.Dialog",
                        success: function(aDialogs) {
                            aDialogs[0].close();
                        }
                    });
                }
            },
            
            assertions: {
                iShouldSeeDataProductDialog: function(productName) {
                    return this.waitFor({
                        controlType: "sap.m.Dialog",
                        matchers: new Properties({
                            title: productName
                        }),
                        success: function() {
                            Opa5.assert.ok(true, "Dialog opened: " + productName);
                        },
                        errorMessage: "Dialog not found: " + productName
                    });
                },
                
                iShouldSeeTablesListed: function(expectedCount) {
                    return this.waitFor({
                        controlType: "sap.m.List",
                        success: function(aLists) {
                            var oList = aLists[0];
                            var items = oList.getItems();
                            Opa5.assert.strictEqual(
                                items.length,
                                expectedCount,
                                "Expected " + expectedCount + " tables"
                            );
                        }
                    });
                },
                
                iShouldSeeStructureButton: function() {
                    return this.waitFor({
                        controlType: "sap.m.Button",
                        matchers: new Properties({
                            text: "Structure"
                        }),
                        success: function() {
                            Opa5.assert.ok(true, "Structure button found");
                        }
                    });
                },
                
                iShouldSeeViewDataButton: function() {
                    return this.waitFor({
                        controlType: "sap.m.Button",
                        matchers: new Properties({
                            text: "View Data"
                        }),
                        success: function() {
                            Opa5.assert.ok(true, "View Data button found");
                        }
                    });
                }
            }
        }
    });
});
```

**Test Journey**:
```javascript
// test/integration/DataProductsJourney.js
sap.ui.define([
    "sap/ui/test/opaQunit"
], function(opaTest) {
    "use strict";

    QUnit.module("Data Products");

    opaTest("Should see data product tiles", function(Given, When, Then) {
        // Arrange
        Given.iStartMyApp();

        // Act
        When.onTheDataProductsPage.iClickDataProductTile("Payment Terms (Local)");

        // Assert
        Then.onTheDataProductsPage.iShouldSeeDataProductDialog("Payment Terms (Local)");
        Then.onTheDataProductsPage.iShouldSeeTablesListed(4);
        Then.onTheDataProductsPage.iShouldSeeStructureButton();
        Then.onTheDataProductsPage.iShouldSeeViewDataButton();

        // Cleanup
        Then.onTheDataProductsPage.iCloseTheDialog();
    });

    opaTest("Should handle Company Code tile", function(Given, When, Then) {
        // Act
        When.onTheDataProductsPage.iClickDataProductTile("Company Code (Local)");

        // Assert
        Then.onTheDataProductsPage.iShouldSeeDataProductDialog("Company Code (Local)");
        Then.onTheDataProductsPage.iShouldSeeTablesListed(9);

        // Cleanup
        Then.onTheDataProductsPage.iCloseTheDialog();
        Then.iTeardownMyApp();
    });
});
```

**Run Tests**:
```bash
# In browser (development)
open http://localhost:5000/test/integration/opaTests.qunit.html

# Command line (CI/CD)
npm run test:opa5
```

### 2. Playwright - Modern E2E Framework ⭐ ALSO RECOMMENDED

**What**: Modern browser automation framework by Microsoft  
**When**: Complex workflows, cross-browser testing, screenshots  
**Why**: Fast, reliable, excellent debugging, modern API

**Advantages**:
- ✅ Fast execution (parallel tests)
- ✅ Auto-wait (no manual waits needed)
- ✅ Cross-browser (Chromium, Firefox, WebKit)
- ✅ Screenshot/video capture
- ✅ Excellent debugging (trace viewer)
- ✅ TypeScript support
- ✅ Industry standard

**Example: Same Test in Playwright**:
```javascript
// tests/e2e/dataProducts.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Data Products Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:5000');
        await page.waitForSelector('[data-page="dataProducts"]');
    });

    test('should open Payment Terms dialog when tile clicked', async ({ page }) => {
        // Click the tile
        await page.click('text=Payment Terms (Local)');
        
        // Wait for dialog
        const dialog = page.locator('.sapMDialog');
        await expect(dialog).toBeVisible();
        
        // Verify dialog title
        await expect(dialog.locator('.sapMDialogTitle')).toContainText('Payment Terms');
        
        // Verify tables listed
        const tableRows = dialog.locator('.sapMListItems .sapMLIB');
        await expect(tableRows).toHaveCount(4);
        
        // Verify action buttons
        await expect(dialog.locator('button:has-text("Structure")')).toBeVisible();
        await expect(dialog.locator('button:has-text("View Data")')).toBeVisible();
        
        // Close dialog
        await dialog.locator('button:has-text("Close")').click();
        await expect(dialog).not.toBeVisible();
    });

    test('should open Company Code dialog', async ({ page }) => {
        await page.click('text=Company Code (Local)');
        
        const dialog = page.locator('.sapMDialog');
        await expect(dialog).toBeVisible();
        await expect(dialog.locator('.sapMDialogTitle')).toContainText('Company Code');
        
        const tableRows = dialog.locator('.sapMListItems .sapMLIB');
        await expect(tableRows).toHaveCount(9);
    });

    test('should test all data product tiles', async ({ page }) => {
        const testCases = [
            { name: 'Payment Terms (Local)', tables: 4 },
            { name: 'Journal Entry Header (Local)', tables: 2 },
            { name: 'Company Code (Local)', tables: 9 }
        ];

        for (const testCase of testCases) {
            await page.click(`text=${testCase.name}`);
            
            const dialog = page.locator('.sapMDialog');
            await expect(dialog).toBeVisible();
            
            const tableRows = dialog.locator('.sapMListItems .sapMLIB');
            await expect(tableRows).toHaveCount(testCase.tables);
            
            await dialog.locator('button:has-text("Close")').click();
            await expect(dialog).not.toBeVisible();
        }
    });

    test('should handle Structure button click', async ({ page }) => {
        await page.click('text=Payment Terms (Local)');
        
        const dialog = page.locator('.sapMDialog');
        await expect(dialog).toBeVisible();
        
        // Click Structure button on first table
        await dialog.locator('button:has-text("Structure")').first().click();
        
        // Verify structure dialog appears
        // (Add assertions based on your structure view implementation)
    });
});
```

**Run Tests**:
```bash
# Run all tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test dataProducts

# Debug mode
npx playwright test --debug

# Generate report
npx playwright show-report
```

### 3. UIVeri5 - SAP's E2E Framework (Optional)

**What**: SAP's E2E testing tool built on Protractor/WebDriverJS  
**When**: Testing Fiori apps with specific SAP integration needs  
**Why**: SAP-specific, OData integration

**Status**: ⚠️ Less recommended due to Protractor deprecation  
**Alternative**: Use Playwright or OPA5 instead

## Recommended Testing Strategy

### Layered Approach

```
┌─────────────────────────────────────┐
│   Playwright (E2E Workflows)        │ ← Full user journeys
│   - Cross-page navigation           │
│   - Complex workflows                │
│   - Screenshot validation            │
└─────────────────────────────────────┘
           ↓ Calls
┌─────────────────────────────────────┐
│   OPA5 (UI5 Component Tests)        │ ← UI5-specific interactions
│   - Tile clicks                     │
│   - Dialog interactions              │
│   - Control state verification       │
└─────────────────────────────────────┘
           ↓ Calls
┌─────────────────────────────────────┐
│   Jest/jsdom (Unit Tests)           │ ← Business logic
│   - API calls                        │
│   - Data transformations             │
│   - Utility functions                │
└─────────────────────────────────────┘
```

### When to Use Each

| Framework | Use Case | Speed | Coverage |
|-----------|----------|-------|----------|
| **Jest** | Business logic, API layer | Very Fast | Unit level |
| **OPA5** | UI5 control interactions | Fast | Component level |
| **Playwright** | Full workflows, cross-browser | Medium | E2E level |

## Implementation Plan

### Phase 1: Setup (Week 1)

**1. Install Dependencies**:
```bash
# OPA5 (built into UI5, no install needed)

# Playwright
npm install --save-dev @playwright/test
npx playwright install
```

**2. Create Test Structure**:
```
app/static/tests/
├── unit/                    # Jest tests
│   ├── api/
│   │   └── dataProducts.test.js
│   └── utils/
│       └── formatters.test.js
├── integration/             # OPA5 tests
│   ├── pages/
│   │   ├── DataProducts.js
│   │   ├── Connections.js
│   │   └── Settings.js
│   ├── journeys/
│   │   ├── DataProductsJourney.js
│   │   └── FeatureManagerJourney.js
│   └── opaTests.qunit.html
└── e2e/                     # Playwright tests
    ├── dataProducts.spec.js
    ├── connections.spec.js
    └── playwright.config.js
```

**3. Configure package.json**:
```json
{
  "scripts": {
    "test": "npm run test:unit && npm run test:opa5 && npm run test:e2e",
    "test:unit": "jest",
    "test:opa5": "karma start karma.conf.js",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "jest": "^29.7.0",
    "karma": "^6.4.2",
    "karma-qunit": "^4.1.2"
  }
}
```

### Phase 2: Write Tests (Week 2)

**Priority 1: Critical User Flows**
- ✅ Data Products tile click → dialog opens
- ✅ Tables listed correctly
- ✅ Structure/View Data buttons visible
- ✅ Dialog closes

**Priority 2: Feature Interactions**
- ✅ Feature toggle (settings page)
- ✅ Connection add/edit/delete
- ✅ SQL execution

**Priority 3: Edge Cases**
- ✅ Error handling
- ✅ Empty states
- ✅ Loading states

### Phase 3: CI/CD Integration (Week 3)

**GitHub Actions Workflow**:
```yaml
# .github/workflows/ui-tests.yml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          npm ci
          npx playwright install --with-deps
      
      - name: Start server
        run: |
          python -m pip install -r app/requirements.txt
          python server.py &
          sleep 5  # Wait for server
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run OPA5 tests
        run: npm run test:opa5
      
      - name: Run Playwright tests
        run: npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

### Phase 4: Maintenance (Ongoing)

**Best Practices**:
- ✅ Add tests for every new feature
- ✅ Update tests when UI changes
- ✅ Run locally before commit
- ✅ Review failed tests immediately
- ✅ Keep tests fast (< 5 min total)

## Example: Complete Test for Data Products

### OPA5 Version (Recommended for UI5)

```javascript
// test/integration/DataProductsJourney.js
sap.ui.define([
    "sap/ui/test/opaQunit",
    "./pages/DataProducts"
], function(opaTest) {
    "use strict";

    QUnit.module("Data Products - Tile Interactions");

    opaTest("Should display all data product tiles", function(Given, When, Then) {
        Given.iStartMyApp();
        Then.onTheDataProductsPage.iShouldSeeTiles(9);
    });

    opaTest("Should open Payment Terms dialog", function(Given, When, Then) {
        When.onTheDataProductsPage.iClickDataProductTile("Payment Terms (Local)");
        Then.onTheDataProductsPage.iShouldSeeDataProductDialog("Payment Terms (Local)");
        Then.onTheDataProductsPage.iShouldSeeTablesListed(4);
        Then.onTheDataProductsPage.iShouldSeeActionButtons();
    });

    opaTest("Should verify all tables have correct record counts", function(Given, When, Then) {
        Then.onTheDataProductsPage.iShouldSeeTableWithRecords("PaymentTerms", 20);
        Then.onTheDataProductsPage.iShouldSeeTableWithRecords("PaymentTermsConditions", 20);
    });

    opaTest("Should close dialog", function(Given, When, Then) {
        When.onTheDataProductsPage.iCloseTheDialog();
        Then.onTheDataProductsPage.iShouldNotSeeDialog();
        Then.iTeardownMyApp();
    });
});
```

### Playwright Version (Recommended for E2E)

```javascript
// tests/e2e/dataProducts.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Data Products - Complete Flow', () => {
    test('should handle complete data product workflow', async ({ page }) => {
        // Navigate to app
        await page.goto('http://localhost:5000');
        
        // Wait for page load
        await page.waitForSelector('[data-page="dataProducts"]');
        
        // Verify tiles loaded
        const tiles = page.locator('.sapMGT');
        await expect(tiles).toHaveCount(9);
        
        // Test each data product
        const testCases = [
            { name: 'Payment Terms (Local)', tables: 4 },
            { name: 'Journal Entry Header (Local)', tables: 2 },
            { name: 'Company Code (Local)', tables: 9 }
        ];
        
        for (const { name, tables } of testCases) {
            // Click tile
            await page.click(`text=${name}`);
            
            // Verify dialog
            const dialog = page.locator('.sapMDialog');
            await expect(dialog).toBeVisible();
            await expect(dialog.locator('.sapMDialogTitle')).toContainText(name.split(' (')[0]);
            
            // Verify table count
            const tableRows = dialog.locator('.sapMListItems .sapMLIB');
            await expect(tableRows).toHaveCount(tables);
            
            // Verify buttons
            await expect(dialog.locator('button:has-text("Structure")')).toHaveCount(tables);
            await expect(dialog.locator('button:has-text("View Data")')).toHaveCount(tables);
            
            // Close
            await dialog.locator('button:has-text("Close")').click();
            await expect(dialog).not.toBeVisible();
        }
    });
});
```

## Visual Regression Testing (Optional)

### Playwright Screenshots

```javascript
test('should match data products page snapshot', async ({ page }) => {
    await page.goto('http://localhost:5000');
    await page.waitForSelector('[data-page="dataProducts"]');
    
    // Take screenshot
    await expect(page).toHaveScreenshot('dataProducts.png');
});
```

**Benefits**:
- ✅ Catches visual regressions
- ✅ Verifies layout changes
- ✅ Automatic comparison

## Performance Testing

### Lighthouse Integration

```javascript
// tests/performance/lighthouse.spec.js
const playwright = require('playwright');
const { playAudit } = require('playwright-lighthouse');

test('should meet performance budgets', async () => {
    const browser = await playwright.chromium.launch();
    const page = await browser.newPage();
    
    await page.goto('http://localhost:5000');
    
    await playAudit({
        page,
        thresholds: {
            performance: 90,
            accessibility: 95,
            'best-practices': 90,
            seo: 80
        }
    });
    
    await browser.close();
});
```

## Accessibility Testing

### axe-core Integration

```javascript
// tests/a11y/accessibility.spec.js
const { test, expect } = require('@playwright/test');
const { injectAxe, checkA11y } = require('axe-playwright');

test('should have no accessibility violations', async ({ page }) => {
    await page.goto('http://localhost:5000');
    await injectAxe(page);
    
    await checkA11y(page, null, {
        detailedReport: true,
        detailedReportOptions: {
            html: true
        }
    });
});
```

## Cost-Benefit Analysis

### Current Manual Testing
- ⏱️ **Time**: 5-10 minutes per test cycle
- 👤 **Human**: Required for every test
- 🐛 **Coverage**: Inconsistent (humans skip steps)
- 💰 **Cost**: High (developer time)

### Automated Testing
- ⏱️ **Time**: 30-60 seconds per full suite
- 👤 **Human**: Not required
- 🐛 **Coverage**: 100% consistent
- 💰 **Cost**: Low (one-time setup)

### ROI Calculation
- Setup time: 16 hours (2 weeks)
- Time saved per test: 10 minutes
- Tests per day: 10-20
- **Payback**: 2-3 weeks
- **Annual savings**: ~400 hours

## Status

✅ **RECOMMENDED APPROACH**:
1. **OPA5** for UI5-specific component tests
2. **Playwright** for E2E workflows
3. **CI/CD integration** for automation

**Next Steps**:
1. Install Playwright
2. Create test structure
3. Write critical path tests
4. Integrate with CI/CD
5. Add to pre-commit hooks

## References

- **OPA5 Documentation**: https://ui5.sap.com/#/topic/2696ab50faad458f9b4027ec2f9b884d
- **Playwright Documentation**: https://playwright.dev
- **SAP Testing Guide**: https://ui5.sap.com/#/topic/291c9121e6044ab381e0b51716f97f52
- **Related**: [[Testing Standards]], [[SAP Fiori Design Standards]]

---

**Last Updated**: 2026-01-29  
**Next Review**: After first automated test implementation  
**Compliance**: Recommended for all UI development