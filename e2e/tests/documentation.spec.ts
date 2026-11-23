import { expect, test } from './support/fixtures';

// Every section is on the page for every reader who may read it; `yours` marks the ones of their roles.

const mine = (page: import('@playwright/test').Page, key: string) =>
  page.locator(`[data-doc-section="${key}"]`);

test('a secretary follows the link and finds the secretary section marked theirs', async ({ page }) => {
  await page.goto('/e2e/login/doc-secretary?roles=secretary');

  await page.getByRole('link', { name: 'Documentation' }).click();
  await expect(page).toHaveURL(/\/documentation$/);
  await expect(mine(page, 'secretary')).toHaveAttribute('data-doc-mine', 'true');
  await expect(mine(page, 'admin')).toHaveAttribute('data-doc-mine', 'false');
  await expect(mine(page, 'admin')).toBeVisible();
  await expect(page.locator('[data-doc-mine="true"]')).toHaveCount(1);

  await page.screenshot({ path: 'screenshots/documentation-secretary.png', fullPage: true });
});

test('an admin finds the admin section marked theirs', async ({ page }) => {
  await page.goto('/e2e/login/doc-admin?roles=admin');

  await page.getByRole('link', { name: 'Documentation' }).click();
  await expect(mine(page, 'admin')).toHaveAttribute('data-doc-mine', 'true');
  await expect(mine(page, 'secretary')).toHaveAttribute('data-doc-mine', 'false');
  await expect(page.locator('[data-doc-mine="true"]')).toHaveCount(1);
});

test('somebody with no role has no link, and is refused the page', async ({ page }) => {
  await page.goto('/e2e/login/doc-nobody');

  await expect(page.getByRole('link', { name: 'Documentation' })).toHaveCount(0);
  const response = await page.goto('/documentation');
  expect(response?.status()).toBe(403);
});
