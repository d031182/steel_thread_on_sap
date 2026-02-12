/**
 * Playwright E2E Tests for API Playground
 * 
 * Tests the complete user workflow for API testing functionality.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

const { test, expect } = require('@playwright/test');

test.describe('API Playground Page', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to application
        await page.goto('http://localhost:5000');
        await page.waitForLoadState('networkidle');
    });

    test('should display API Playground tab in navigation', async ({ page }) => {
        // Check IconTabBar exists
        const tabBar = page.locator('#mainTabBar');
        await expect(tabBar).toBeVisible();
        
        // Check API Playground tab exists
        const apiPlaygroundTab = page.locator('text=API Playground');
        await expect(apiPlaygroundTab).toBeVisible();
    });

    test('should navigate to API Playground when tab is clicked', async ({ page }) => {
        // Click API Playground tab
        await page.click('text=API Playground');
        
        // Wait for page to render
        await page.waitForTimeout(1000);
        
        // Check if API Playground content is visible
        const title = page.locator('text=API Playground').first();
        await expect(title).toBeVisible();
        
        // Check if stats toolbar is visible
        const statsToolbar = page.locator('#apiStatsToolbar');
        await expect(statsToolbar).toBeVisible();
    });

    test('should display 3-column layout with all sections', async ({ page }) => {
        // Navigate to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(1000);
        
        // Check Flexible Column Layout exists
        const fcl = page.locator('#apiPlaygroundFCL');
        await expect(fcl).toBeVisible();
        
        // Check BEGIN column (API Explorer)
        const explorer = page.locator('#apiExplorerPage');
        await expect(explorer).toBeVisible();
        
        // Check MID column (Request Builder)
        const builder = page.locator('#requestBuilderPage');
        await expect(builder).toBeVisible();
        
        // Check END column (Response Viewer)
        const viewer = page.locator('#responseViewerPage');
        await expect(viewer).toBeVisible();
    });

    test('should discover and display module APIs', async ({ page }) => {
        // Navigate to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(2000); // Wait for API discovery
        
        // Check if stats are updated (non-zero)
        const statsModules = page.locator('#statsModules');
        const statsEndpoints = page.locator('#statsEndpoints');
        
        await expect(statsModules).not.toHaveText('0');
        await expect(statsEndpoints).not.toHaveText('0');
        
        // Check if API list has items
        const apiList = page.locator('#apiExplorerList');
        const listItems = apiList.locator('.sapMSLI'); // StandardListItem
        const count = await listItems.count();
        expect(count).toBeGreaterThan(0);
    });

    test('should load endpoint into request builder when clicked', async ({ page }) => {
        // Navigate to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(2000);
        
        // Click first endpoint in list
        const firstEndpoint = page.locator('#apiExplorerList .sapMSLI').first();
        await firstEndpoint.click();
        await page.waitForTimeout(500);
        
        // Check if URL input is populated
        const urlInput = page.locator('#endpointUrlInput input');
        const url = await urlInput.inputValue();
        expect(url).toBeTruthy();
        expect(url).toContain('/api/');
    });

    test('should have all request builder controls', async ({ page }) => {
        // Navigate to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(1000);
        
        // Check HTTP method selector
        const methodSelect = page.locator('#httpMethodSelect');
        await expect(methodSelect).toBeVisible();
        
        // Check endpoint URL input
        const urlInput = page.locator('#endpointUrlInput');
        await expect(urlInput).toBeVisible();
        
        // Check request body textarea
        const bodyInput = page.locator('#requestBodyInput');
        await expect(bodyInput).toBeVisible();
        
        // Check Execute button
        const executeBtn = page.locator('text=Execute');
        await expect(executeBtn).toBeVisible();
        
        // Check Clear button
        const clearBtn = page.locator('text=Clear').last(); // Last one is in Request Builder
        await expect(clearBtn).toBeVisible();
    });

    test('should have response viewer controls', async ({ page }) => {
        // Navigate to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(1000);
        
        // Check response metadata bar
        const metadataBar = page.locator('#responseMetadataBar');
        await expect(metadataBar).toBeVisible();
        
        // Check response tabs
        const tabBar = page.locator('#responseTabBar');
        await expect(tabBar).toBeVisible();
        
        // Check Formatted tab
        const formattedTab = page.locator('text=Formatted');
        await expect(formattedTab).toBeVisible();
        
        // Check Raw tab
        const rawTab = page.locator('text=Raw');
        await expect(rawTab).toBeVisible();
        
        // Check Copy button
        const copyBtn = page.locator('#copyResponseBtn');
        await expect(copyBtn).toBeVisible();
    });

    test('should switch between Data Products and API Playground', async ({ page }) => {
        // Start on Data Products (default)
        const dataProductsTitle = page.locator('text=Data Products').first();
        await expect(dataProductsTitle).toBeVisible();
        
        // Switch to API Playground
        await page.click('text=API Playground');
        await page.waitForTimeout(1000);
        
        // Verify API Playground is shown
        const apiPlaygroundTitle = page.locator('text=API Playground').first();
        await expect(apiPlaygroundTitle).toBeVisible();
        
        // Switch back to Data Products
        await page.click('text=Data Products').first();
        await page.waitForTimeout(1000);
        
        // Verify Data Products is shown again
        await expect(dataProductsTitle).toBeVisible();
    });
});