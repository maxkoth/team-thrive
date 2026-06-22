const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const FPS = 30, DUR = 30, total = FPS * DUR;
  const onlyPreview = process.argv.includes('--preview');
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb','--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);

  const outDir = path.join(__dirname, 'out');
  require('fs').mkdirSync(outDir, { recursive: true });

  if (onlyPreview) {
    const previews = [1.0, 5.5, 9.2, 14.0, 22.0, 27.5];
    for (let i = 0; i < previews.length; i++) {
      const t = previews[i];
      await page.evaluate((tt) => window.__render(tt), t);
      await page.screenshot({ path: path.join(outDir, `preview_${i}.png`) });
    }
    console.log('preview done');
    await browser.close();
    return;
  }

  const pad = n => String(n).padStart(4, '0');
  for (let f = 0; f < total; f++) {
    const t = f / FPS;
    await page.evaluate((tt) => window.__render(tt), t);
    await page.screenshot({ path: path.join(outDir, `f_${pad(f)}.png`) });
    if (f % 60 === 0) console.log(`frame ${f}/${total}`);
  }
  console.log('render complete:', total, 'frames');
  await browser.close();
})();
