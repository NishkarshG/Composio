// Headless smoke test: loads dist/index.html, mocks window.claude.sample, exercises library + live generation.
import { chromium } from 'playwright';
import fs from 'node:fs';
const html = fs.readFileSync(new URL('../dist/index.html', import.meta.url), 'utf8');
const errors = [];
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium', args: ['--no-sandbox'] }).catch(async () => chromium.launch({ args: ['--no-sandbox'] }));
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|ERR_|Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
await page.route('**/*', (r) => (r.request().url().startsWith('file:') || r.request().url().startsWith('data:') || r.request().url().startsWith('about:') ? r.continue() : r.abort()));

// Mock of the viewer runtime: sample.json drives the page's tools like the real one would.
await page.addInitScript(() => {
  window.__calls = [];
  const draft = { name: 'Pipedrive', summary: 'Pipedrive app approval via Marketplace.', difficulty: 3, difficultyWhy: 'Needs Marketplace review for public apps.', time: { setup: '~20 min', approval: '1-2 weeks', total: '2 weeks' }, gatingModel: 'review-required', devModeLimits: 'Sandbox account only.', stages: [{ name: 'Create app', duration: '20 min', owner: 'you' }, { name: 'Marketplace review', duration: '1-2 weeks', owner: 'provider' }], steps: [{ n: 1, title: 'Create developer sandbox', detail: 'Sign up.', owner: 'you', url: 'https://developers.pipedrive.com' }, { n: 2, title: 'Bad link', detail: 'x', owner: 'agent', url: 'javascript:alert(1)' }], requirements: ['Account'], gotchas: ['<img src=x onerror=window.__xss=1>'], blockers: [{ blocker: 'Review rejected', symptom: 's', whatToDo: 'w', escalation: null }], agentCanDo: ['Draft text'], youMustDo: ['Log in'], composio: { redirectUri: 'x', note: 'n' }, evidence: [{ claim: 'Review takes 1-2 weeks', status: 'verified', source: 'https://developers.pipedrive.com', note: null }], uncertainties: ['Timing'] };
  const sample = async () => { throw new Error('use sample.json'); };
  sample.json = async (prompt, opts = {}) => {
    window.__calls.push({ prompt: prompt.slice(0, 60), tools: (opts.tools || []).map((t) => t.name) });
    if (opts.tools) {
      const dir = await opts.tools[0].execute({ name: 'Pipedrive' }, { signal: new AbortController().signal });
      const ref = await opts.tools[1].execute({ slug: 'shopify' }, { signal: new AbortController().signal });
      window.__toolOut = { dir, refHasEvidence: Array.isArray(ref.evidence), refKeys: Object.keys(ref).length };
      await new Promise((r) => setTimeout(r, 150));
      return draft;
    }
    await new Promise((r) => setTimeout(r, 150));
    return { ...draft, uncertainties: ['Reviewer: timing is a guess', 'Timing'] };
  };
  window.claude = { use: async (n) => (n === 'sample' ? sample : null) };
});
await page.goto('file://' + new URL('../dist/index.html', import.meta.url).pathname, { waitUntil: 'load' });
const out = {};
out.overviewRows = await page.locator('tbody tr').count();
out.railButtons = await page.locator('#rail button').count();
// library guide
await page.click('#rail button[data-slug="spotify"]');
out.spotifyTitle = await page.locator('#guide h2').innerText();
out.spotifyEvidence = await page.locator('.ev').count();
out.spotifyMgd = await page.locator('#guide .chip').first().innerText();
// search behaviour
await page.fill('#q', 'pipe'); out.suggs = await page.locator('#sugg li').count();
out.suggFirst = await page.locator('#sugg li').first().innerText();
await page.fill('#q', 'x'); out.xSuggFirst = (await page.locator('#sugg li').first().innerText()).replace(/\n/g, ' | ');
await page.fill('#q', 'Meta Ads'); await page.press('#q', 'Enter');
out.metaOpened = await page.locator('#guide h2').innerText();
// live generation of an app not in library
await page.fill('#q', 'Pipedrive'); await page.press('#q', 'Enter');
await page.waitForSelector('.gen');
await page.waitForSelector('#guide h2', { timeout: 8000 });
out.genTitle = await page.locator('#guide h2').innerText();
out.genBanner = await page.locator('.banner').count();
out.genChips = (await page.locator('#guide .chips').innerText()).replace(/\n/g, ' | ');
out.genEvidenceChips = await page.locator('.ev .chip').allInnerTexts();
out.badLinkRendered = await page.locator('ol.steps a[href^="javascript"]').count();
out.xss = await page.evaluate(() => window.__xss === 1);
out.calls = await page.evaluate(() => window.__calls);
out.toolOut = await page.evaluate(() => window.__toolOut);
out.uncertainties = await page.locator('#guide ~ section ul.plain').last().innerText();
// copy markdown doesn't throw
await page.click('#cp'); out.copyNote = await page.locator('#cp-note').innerText();
// mobile overflow check
await page.setViewportSize({ width: 390, height: 800 });
out.mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
await page.click('#home'); out.mobileOverflowOverview = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
await page.click('#rail button[data-slug="workday"]'); out.mobileOverflowGuide = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
console.log(JSON.stringify({ out, errors }, null, 1));
await browser.close();
