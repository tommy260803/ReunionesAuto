import { test, expect } from '@playwright/test';

test.describe('Aplicación Frontend - Verificación', () => {
  test('debería cargar la página principal', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ReunionesAuto/);
  });

  test('debería tener el body visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });
});
