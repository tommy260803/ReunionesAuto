# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend\e2e\analysis-creation.spec.ts >> Creación de Análisis Estadístico >> debería mostrar el formulario de creación
- Location: frontend\e2e\analysis-creation.spec.ts:9:7

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "/research/analyses/new", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Creación de Análisis Estadístico', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Navegar a la página de creación de análisis
> 6  |     await page.goto('/research/analyses/new');
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  7  |   });
  8  | 
  9  |   test('debería mostrar el formulario de creación', async ({ page }) => {
  10 |     await expect(page.locator('h1')).toContainText('Nuevo Análisis Estadístico');
  11 |     await expect(page.locator('input[name="nombre"]')).toBeVisible();
  12 |     await expect(page.locator('select[name="diseno"]')).toBeVisible();
  13 |   });
  14 | 
  15 |   test('debería requerir campos obligatorios', async ({ page }) => {
  16 |     // Intentar enviar sin campos obligatorios
  17 |     await page.click('button[type="submit"]');
  18 |     
  19 |     // Verificar validación HTML5
  20 |     const nombreInput = page.locator('input[name="nombre"]');
  21 |     await expect(nombreInput).toHaveAttribute('required');
  22 |   });
  23 | 
  24 |   test('debería crear un análisis con datos válidos', async ({ page }) => {
  25 |     // Llenar el formulario
  26 |     await page.fill('input[name="nombre"]', 'Análisis de prueba E2E');
  27 |     await page.fill('textarea[name="objetivo"]', 'Objetivo de prueba');
  28 |     await page.fill('input[name="variable_resultado"]', 'calidad');
  29 |     await page.fill('input[name="variable_grupo"]', 'version');
  30 |     await page.selectOption('select[name="diseno"]', 'INDEPENDIENTE');
  31 |     await page.selectOption('select[name="prueba_solicitada"]', '');
  32 |     await page.fill('input[name="alpha"]', '0.05');
  33 |     await page.selectOption('select[name="correccion_multiple"]', 'HOLM');
  34 | 
  35 |     // Enviar formulario
  36 |     await page.click('button[type="submit"]');
  37 | 
  38 |     // Verificar redirección a página de detalle
  39 |     await expect(page).toHaveURL(/.*analyses\/[a-f0-9-]+/);
  40 |   });
  41 | 
  42 |   test('debería cancelar y volver atrás', async ({ page }) => {
  43 |     await page.click('text=Cancelar');
  44 |     await expect(page).toHaveURL(/.*research/);
  45 |   });
  46 | });
  47 | 
```