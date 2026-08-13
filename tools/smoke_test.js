"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.COURSE_SITE_URL || "http://127.0.0.1:8765/";
const chromePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const qaDirectory = path.resolve(__dirname, "..", "qa");
const manifest = JSON.parse(fs.readFileSync(path.resolve(__dirname, "..", "site-manifest.json"), "utf8"));
const topics = manifest.units.flatMap(unit => unit.topics.map(topic => ({ unit: unit.number, title: topic[0], url: topic[1] })));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function run() {
  fs.mkdirSync(qaDirectory, { recursive: true });
  assert(fs.existsSync(chromePath), `Chrome not found at ${chromePath}`);
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const errors = [];
  const failedResources = [];
  page.on("console", message => {
    if (message.type() === "error" && !message.text().startsWith("Failed to load resource")) errors.push(message.text());
  });
  page.on("pageerror", error => errors.push(error.message));
  page.on("response", resource => {
    if (resource.status() >= 400) failedResources.push(`${resource.status()} ${resource.url()}`);
  });

  let response = await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  assert(response && response.ok(), "Course home did not load");
  assert(await page.locator('[role="tab"]').count() === 3, "Course home must show three unit tabs");
  assert(await page.locator(".topic-grid a").count() === 33, "Course home must contain 33 topic links");
  await page.screenshot({ path: path.join(qaDirectory, "home-desktop.png"), fullPage: true });

  const tabs = page.locator('[role="tab"]');
  for (let index = 0; index < 3; index += 1) {
    await tabs.nth(index).click();
    assert(await page.locator(`#panel-u${index + 1}`).isVisible(), `Unit ${index + 1} panel did not open`);
  }

  for (const topic of topics) {
    response = await context.request.get(new URL(topic.url, baseUrl).toString());
    assert(response.ok(), `${topic.title} returned HTTP ${response.status()}`);
    await response.dispose();
  }

  const sampleUrls = [topics[0].url, topics[9].url, topics[24].url];
  for (const url of sampleUrls) {
    await page.goto(new URL(url, baseUrl).toString(), { waitUntil: "domcontentloaded" });
    assert(await page.locator("h1").count() === 1, `${url} must have one h1`);
  }

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  assert(await page.locator('[role="tab"]').first().isVisible(), "Mobile unit selector is not visible");
  assert(await page.evaluate(() => document.documentElement.scrollWidth === document.documentElement.clientWidth), "Mobile home has horizontal overflow");
  await page.screenshot({ path: path.join(qaDirectory, "home-mobile.png"), fullPage: true });

  await browser.close();
  assert(errors.length === 0, `Browser console errors:\n${errors.join("\n")}`);
  assert(failedResources.length === 0, `Failed browser resources:\n${failedResources.join("\n")}`);
  console.log("BROWSER SMOKE TEST PASSED");
  console.log("- Three unit panels: passed");
  console.log("- 33 topic URLs: HTTP 200");
  console.log("- Unit I, II and III sample pages: rendered");
  console.log("- Desktop and mobile course home: passed");
  console.log("- Browser console errors: 0");
}

run().catch(error => {
  console.error(`BROWSER SMOKE TEST FAILED\n${error.stack}`);
  process.exitCode = 1;
});
