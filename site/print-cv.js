// Prints site/out/cv-{en,fr}.html to docs/assets/cv/ as one-page A4 PDFs (Playwright, Chromium).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  for (const lang of ['en', 'fr']) {
    const p = await b.newPage();
    await p.goto('file://' + path.join(__dirname, 'out', `cv-${lang}.html`));
    await p.waitForTimeout(300);
    const out = path.join(__dirname, '..', 'docs', 'assets', 'cv', `gabriel-ghanem-cv-${lang}.pdf`);
    await p.pdf({ path: out, format: 'A4', preferCSSPageSize: true, printBackground: true });
    console.log(out);
    await p.close();
  }
  await b.close();
})();
