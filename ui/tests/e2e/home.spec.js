// @ts-check
// const { test, expect } = require('@playwright/test');
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle("EOTDL | Home");
});

test('datasets link', async ({ page }) => {
  await page.goto('/');

  // Click the datasets link.
  await page.getByRole('link', { name: 'Datasets', exact: true }).click();


  // Expects the URL to contain datasets.
  await expect(page).toHaveURL(/.*datasets/);
});
