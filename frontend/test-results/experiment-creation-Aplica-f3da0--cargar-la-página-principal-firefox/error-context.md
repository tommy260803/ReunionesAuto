# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: experiment-creation.spec.ts >> Aplicación Frontend - Verificación >> debería cargar la página principal
- Location: e2e\experiment-creation.spec.ts:4:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "http://localhost:3000/", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Aplicación Frontend - Verificación', () => {
  4  |   test('debería cargar la página principal', async ({ page }) => {
> 5  |     await page.goto('/');
     |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  6  |     await expect(page).toHaveTitle(/ReunionesAuto/);
  7  |   });
  8  | 
  9  |   test('debería tener el body visible', async ({ page }) => {
  10 |     await page.goto('/');
  11 |     await expect(page.locator('body')).toBeVisible();
  12 |   });
  13 | });
  14 | 
```