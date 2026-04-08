# CITMS 3.6 - E2E Testing Plan (Playwright)

Đây là kịch bản kiểm thử luồng nghiệp vụ chính (End-to-End) sử dụng Playwright.

## 1. Luồng: Login -> Ingest -> Dashboard -> Ticket

```typescript
import { test, expect } from '@playwright/test';

test.describe('CITMS Main Business Flow', () => {
  
  test('should login, ingest device, and see it on dashboard', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'admin@citms.com');
    await page.fill('input[name="password"]', 'P@ssw0rd123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // 2. Simulate Agent Ingestion (via API call from test)
    const ingestResponse = await page.request.post('/api/v1/inventory/ingest', {
      data: {
        hostname: 'PC-TEST-E2E',
        serial_number: 'SN-E2E-999',
        os_info: { name: 'Ubuntu', version: '22.04' },
        hardware: { cpu: 'AMD Ryzen 9', ram_gb: 64, disk_gb: 2048 },
        software_list: [{ name: 'Docker', version: '24.0.5' }],
        mode: 'FULL_REPLACE'
      },
      headers: { 'Authorization': `Bearer ${process.env.TEST_TOKEN}` }
    });
    expect(ingestResponse.status()).toBe(202);

    // 3. Verify on Dashboard
    await page.reload();
    await expect(page.locator('text=Total Assets')).toContainText('1,249'); // 1,248 + 1
    
    // 4. Create a Support Ticket for this device
    await page.goto('/tickets');
    await page.click('button:has-text("New Ticket")');
    await page.fill('input[name="title"]', 'E2E Test: Broken Screen');
    await page.selectOption('select[name="priority"]', 'HIGH');
    await page.fill('textarea[name="description"]', 'Screen is flickering on PC-TEST-E2E');
    await page.click('button:has-text("Create")');
    
    // 5. Verify Ticket in Kanban
    await expect(page.locator('text=E2E Test: Broken Screen')).toBeVisible();
    await expect(page.locator('text=HIGH')).toBeVisible();
  });

  test('should handle offline inventory scan and sync', async ({ page, context }) => {
    // 1. Go to Physical Inventory
    await page.goto('/inventory/physical');
    await expect(page.locator('text=Online')).toBeVisible();

    // 2. Simulate Offline Mode
    await context.setOffline(true);
    await expect(page.locator('text=Offline Mode')).toBeVisible();

    // 3. Perform a Scan (Mocked)
    await page.evaluate(() => {
      // Simulate calling the internal handleInventoryCheck function
      (window as any).handleInventoryCheck('SN-OFFLINE-001');
    });
    await expect(page.locator('text=Pending Sync')).toContainText('1 Items');

    // 4. Go back Online and Sync
    await context.setOffline(false);
    await expect(page.locator('text=Online')).toBeVisible();
    await page.click('button:has-text("Sync Data")');
    
    // 5. Verify sync success
    await expect(page.locator('text=Successfully Scanned!')).toBeVisible();
    await expect(page.locator('text=No pending sync items.')).toBeVisible();
  });

});
```

## 2. Cách chạy
1. Cài đặt Playwright: `npm install -D @playwright/test`
2. Chạy test: `npx playwright test`
3. Xem báo cáo: `npx playwright show-report`
