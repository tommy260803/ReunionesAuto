# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: research-dashboard.spec.ts >> Página Principal >> debería mostrar el contenido principal
- Location: e2e\research-dashboard.spec.ts:9:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
Call log:
  - navigating to "http://localhost:3000/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Página Principal', () => {
  4  |   test('debería cargar la página principal', async ({ page }) => {
  5  |     await page.goto('/');
  6  |     await expect(page).toHaveTitle(/ReunionesAuto/);
  7  |   });
  8  | 
  9  |   test('debería mostrar el contenido principal', async ({ page }) => {
> 10 |     await page.goto('/');
     |                ^ Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
  11 |     await expect(page.locator('body')).toBeVisible();
  12 |   });
  13 | });
  14 | 
```