# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: analysis-creation.spec.ts >> Aplicación Frontend >> debería cargar la aplicación
- Location: e2e\analysis-creation.spec.ts:4:7

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
  3  | test.describe('Aplicación Frontend', () => {
  4  |   test('debería cargar la aplicación', async ({ page }) => {
> 5  |     await page.goto('/');
     |                ^ Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
  6  |     await expect(page).toHaveTitle(/ReunionesAuto/);
  7  |   });
  8  | 
  9  |   test('debería tener contenido visible', async ({ page }) => {
  10 |     await page.goto('/');
  11 |     await expect(page.locator('body')).toBeVisible();
  12 |   });
  13 | });
  14 | 
```