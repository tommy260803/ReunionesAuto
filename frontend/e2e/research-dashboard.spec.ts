import { test, expect } from '@playwright/test';

test.describe('Página Principal', () => {
  test('debería cargar la página principal', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ReunionesAuto/);
  });

  test('debería mostrar el contenido principal', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });
});
