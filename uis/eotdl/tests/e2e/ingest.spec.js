// @ts-check
// const { test, expect } = require('@playwright/test');
import { test, expect } from '@playwright/test';

test('ingest dataset', async ({ page }) => {
  await page.goto('/datasets');

  // Click the ingest dataset button.
  await page.getByRole('checkbox', { name: 'Ingest Dataset', exact: true }).click();
});
