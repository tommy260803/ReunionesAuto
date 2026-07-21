# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend\e2e\experiment-creation.spec.ts >> Creación de Sesión Experimental >> debería mostrar el formulario de creación
- Location: frontend\e2e\experiment-creation.spec.ts:9:7

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "/research/experiments/new", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Creación de Sesión Experimental', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     // Navegar a la página de creación de sesión experimental
> 6  |     await page.goto('/research/experiments/new');
     |                ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  7  |   });
  8  | 
  9  |   test('debería mostrar el formulario de creación', async ({ page }) => {
  10 |     await expect(page.locator('h1')).toContainText('Nueva Sesión Experimental');
  11 |     await expect(page.locator('input[name="nombre"]')).toBeVisible();
  12 |     await expect(page.locator('select[name="estado"]')).toBeVisible();
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
  24 |   test('debería crear una sesión con datos válidos', async ({ page }) => {
  25 |     // Llenar el formulario
  26 |     await page.fill('input[name="nombre"]', 'Sesión de prueba E2E');
  27 |     await page.fill('textarea[name="descripcion"]', 'Descripción de prueba');
  28 |     await page.selectOption('select[name="estado"]', 'PLANIFICADO');
  29 | 
  30 |     // Enviar formulario
  31 |     await page.click('button[type="submit"]');
  32 | 
  33 |     // Verificar redirección a página de detalle
  34 |     await expect(page).toHaveURL(/.*experiments\/[a-f0-9-]+/);
  35 |   });
  36 | 
  37 |   test('debería cancelar y volver atrás', async ({ page }) => {
  38 |     await page.click('text=Cancelar');
  39 |     await expect(page).toHaveURL(/.*research/);
  40 |   });
  41 | });
  42 | 
```