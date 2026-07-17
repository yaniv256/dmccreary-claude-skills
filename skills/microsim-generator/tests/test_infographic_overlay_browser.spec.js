const { test, expect } = require('@playwright/test');

const fixtureUrl =
  process.env.INFOGRAPHIC_OVERLAY_FIXTURE_URL ||
  'http://127.0.0.1:8765/skills/microsim-generator/tests/fixtures/callout-overlay/';
const gridFixtureUrl =
  process.env.GRID_OVERLAY_FIXTURE_URL ||
  'http://127.0.0.1:8765/docs/sims/grid-overlay-test/main.html';

for (const viewport of [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]) {
  test(`callout controls remain stable at ${viewport.name} width`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));

    await page.goto(fixtureUrl);
    const overlay = page.frameLocator('#overlay');
    await expect(overlay.locator('#sim-title')).toHaveText(
      'Callout Overlay Contract Fixture'
    );
    await expect(overlay.locator('.label-row')).toHaveCount(2);

    const controls = overlay.locator('#controls');
    const initialTop = await controls.evaluate((element) =>
      element.getBoundingClientRect().top
    );

    await overlay.locator('.label-row[data-id="short"]').hover();
    await expect(overlay.locator('#infobox-label')).toHaveText('Short callout');
    const shortTop = await controls.evaluate((element) =>
      element.getBoundingClientRect().top
    );

    await overlay.locator('.label-row[data-id="long"]').hover();
    await expect(overlay.locator('#infobox-label')).toHaveText('Long callout');
    const longTop = await controls.evaluate((element) =>
      element.getBoundingClientRect().top
    );

    expect(Math.abs(shortTop - initialTop)).toBeLessThan(0.5);
    expect(Math.abs(longTop - initialTop)).toBeLessThan(0.5);

    const overflow = await overlay.locator('html').evaluate((element) => ({
      horizontal: element.scrollWidth > window.innerWidth + 1,
      vertical: element.scrollHeight > window.innerHeight + 1,
    }));
    expect(overflow).toEqual({ horizontal: false, vertical: false });
    expect(pageErrors).toEqual([]);
  });
}

test('grid zones expose names, tab order, and native keyboard activation', async ({ page }) => {
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.goto(gridFixtureUrl);

  const zones = page.getByRole('button', {
    name: /Static|Interactive|Adaptive/,
  });
  await expect(zones).toHaveCount(3);
  await expect(page.getByRole('button', { name: 'Static — Level 1' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Interactive — Level 2' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Adaptive — Level 3+' })).toBeVisible();

  await page.keyboard.press('Tab');
  const staticZone = page.getByRole('button', { name: 'Static — Level 1' });
  const interactiveZone = page.getByRole('button', { name: 'Interactive — Level 2' });
  const adaptiveZone = page.getByRole('button', { name: 'Adaptive — Level 3+' });
  await expect(staticZone).toBeFocused();
  const focusStyle = await staticZone.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
      boxShadow: style.boxShadow,
    };
  });
  expect(focusStyle.outlineStyle).toBe('solid');
  expect(focusStyle.outlineWidth).toBe('3px');
  expect(focusStyle.boxShadow).not.toBe('none');

  await page.keyboard.press('Tab');
  await expect(interactiveZone).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(adaptiveZone).toBeFocused();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Shift+Tab');
  await expect(staticZone).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#panel-label')).toHaveText('Static — Level 1');
  await interactiveZone.click();
  await expect(page.locator('#panel-label')).toHaveText('Interactive — Level 2');

  await page.getByRole('button', { name: 'Quiz Me' }).click();
  const correctZoneId = await page.evaluate(() => sim.quizQueue[0].correct_zone);
  const correctZone = page.locator(`.grid-zone[data-id="${correctZoneId}"]`);
  await correctZone.focus();
  await page.keyboard.press('Space');
  await expect(page.locator('#correct-modal')).toHaveClass(/show/);
  await expect(page.getByRole('button', { name: 'OK' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(correctZone).toBeFocused();
  expect(pageErrors).toEqual([]);
});

test('grid edit mode keeps calibration handles and removes learning zones from tab order', async ({ page }) => {
  await page.goto(`${gridFixtureUrl}?edit=true`);
  await expect(page.locator('.grid-zone.edit-zone')).toHaveCount(3);
  await expect(page.locator('.corner-handle')).toHaveCount(12);
  for (const zone of await page.locator('.grid-zone').all()) {
    await expect(zone).toHaveAttribute('tabindex', '-1');
    await expect(zone).toHaveAttribute('aria-disabled', 'true');
  }
});

for (const viewport of [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]) {
  test(`grid keyboard controls remain framed at ${viewport.name} width`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto(gridFixtureUrl);
    await expect(page.locator('.grid-zone')).toHaveCount(3);
    const geometry = await page.evaluate(() => ({
      bodyWidth: document.body.scrollWidth,
      viewportWidth: window.innerWidth,
      zones: [...document.querySelectorAll('.grid-zone')].map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          left: rect.left,
          right: rect.right,
          width: rect.width,
          height: rect.height,
        };
      }),
    }));
    expect(geometry.bodyWidth).toBeLessThanOrEqual(geometry.viewportWidth + 1);
    for (const zone of geometry.zones) {
      expect(zone.left).toBeGreaterThanOrEqual(0);
      expect(zone.right).toBeLessThanOrEqual(geometry.viewportWidth + 1);
      expect(zone.width).toBeGreaterThan(0);
      expect(zone.height).toBeGreaterThan(0);
    }
  });
}
