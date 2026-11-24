import { expect, test } from './support/fixtures';

// The admin pages are Admin's alone: the Tooling PMC and infra root, who keep the tool running and
// read nothing of the roster itself.

test('an admin reaches the server status from the header and browses the database', async ({ page }) => {
  await page.goto('/e2e/login/admin-browser?roles=admin');

  await page.getByRole('link', { name: 'Server status' }).click();
  await expect(page).toHaveURL(/\/admin\/server-status$/);
  await expect(page.getByTestId('server-status')).toBeVisible();

  await page.getByRole('link', { name: 'Browse the database' }).click();
  await expect(page).toHaveURL(/\/admin\/data$/);
  await expect(page.getByTestId('no-tables')).toBeVisible();

  await page.screenshot({ path: 'screenshots/admin-data.png', fullPage: true });
});

test('a secretary has no server status link, and is refused the admin pages', async ({ page }) => {
  await page.goto('/e2e/login/admin-secretary?roles=secretary');

  // only somebody holding a role is shown the Documentation link: the role was granted
  await expect(page.getByRole('link', { name: 'Documentation' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Server status' })).toHaveCount(0);
  for (const path of ['/admin/server-status', '/admin/data']) {
    const response = await page.goto(path);
    expect(response?.status()).toBe(403);
  }
});
