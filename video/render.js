const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const FPS = 30, DUR = 30, total = FPS * DUR;
  const onlyPreview = process.argv.includes('--preview');
  // --overlay : footage-ready pass. Footage-scene backgrounds are transparent
  // and frames are exported as RGBA PNGs (to be composited over clips with ffmpeg).
  const overlay = process.argv.includes('--overlay');

  const browser = await chromium.launch({ args: ['--force-color-profile=srgb','--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const url = 'file://' + path.join(__dirname, 'index.html') + (overlay ? '?overlay=1' : '');
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);

  const outDir = path.join(__dirname, overlay ? 'out_overlay' : 'out');
  require('fs').mkdirSync(outDir, { recursive: true });
  const shot = (p) => page.screenshot({ path: p, omitBackground: overlay });

  if (onlyPreview) {
    const previews = [1.0, 5.5, 9.2, 14.0, 22.0, 27.5];
    for (let i = 0; i < previews.length; i++) {
      await page.evaluate((tt) => window.__render(tt), previews[i]);
      await shot(path.join(outDir, `preview_${i}.png`));
    }
    console.log('preview done');
    await browser.close();
    return;
  }

  const pad = n => String(n).padStart(4, '0');
  for (let f = 0; f < total; f++) {
    await page.evaluate((tt) => window.__render(tt), f / FPS);
    await shot(path.join(outDir, `f_${pad(f)}.png`));
    if (f % 60 === 0) console.log(`frame ${f}/${total}`);
  }
  console.log('render complete:', total, 'frames', overlay ? '(overlay/RGBA)' : '');
  await browser.close();
})();
