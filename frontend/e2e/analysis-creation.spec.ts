import { test, expect } from '@playwright/test';

test.describe('Aplicación Frontend', () => {
  test('debería cargar la aplicación', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ReunionesAuto/);
  });

  test('debería tener contenido visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });
});
