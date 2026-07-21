# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend\e2e\research-dashboard.spec.ts >> Módulo de Investigación >> debería navegar a la página de análisis
- Location: frontend\e2e\research-dashboard.spec.ts:20:7

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "/research", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Módulo de Investigación', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Navegar al dashboard de investigación
> 6  |     await page.goto('/research');
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  7  |   });
  8  | 
  9  |   test('debería mostrar el dashboard de investigación', async ({ page }) => {
  10 |     await expect(page.locator('h1')).toContainText('Dashboard de Investigación');
  11 |   });
  12 | 
  13 |   test('debería mostrar estadísticas clave', async ({ page }) => {
  14 |     // Verificar que se muestren las estadísticas
  15 |     await expect(page.locator('text=/Análisis/')).toBeVisible();
  16 |     await expect(page.locator('text=/Experimentos/')).toBeVisible();
  17 |     await expect(page.locator('text=/Evaluaciones/')).toBeVisible();
  18 |   });
  19 | 
  20 |   test('debería navegar a la página de análisis', async ({ page }) => {
  21 |     await page.click('text=Análisis Estadísticos');
  22 |     await expect(page).toHaveURL(/.*analyses/);
  23 |     await expect(page.locator('h1')).toContainText('Análisis Estadísticos');
  24 |   });
  25 | 
  26 |   test('debería navegar a la página de experimentos', async ({ page }) => {
  27 |     await page.click('text=Sesiones Experimentales');
  28 |     await expect(page).toHaveURL(/.*experiments/);
  29 |     await expect(page.locator('h1')).toContainText('Sesiones Experimentales');
  30 |   });
  31 | 
  32 |   test('debería navegar a la página de evaluaciones', async ({ page }) => {
  33 |     await page.click('text=Evaluaciones');
  34 |     await expect(page).toHaveURL(/.*evaluations/);
  35 |     await expect(page.locator('h1')).toContainText('Evaluaciones');
  36 |   });
  37 | });
  38 | 
```