// Renders the textured mockups v3_front.svg / v3_back.svg (written by generate.py) to PNG at 2 px per SVG unit.
// Needs Node with Playwright and its Chromium:  node design/v3/render_png.cjs
const { chromium } = require('playwright');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 916, height: 600 }, deviceScaleFactor: 2 });
  for (const name of ['v3_front', 'v3_back']) {
    await page.goto(pathToFileURL(path.join(__dirname, name + '.svg')).href);
    await page.screenshot({ path: path.join(__dirname, name + '.png'), omitBackground: true });
    console.log('wrote', name + '.png');
  }
  await browser.close();
})();
