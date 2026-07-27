"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.COURSE_SITE_URL || "http://127.0.0.1:8765/";
const chromePath =
  process.env.CHROME_PATH ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const qaDirectory = path.resolve(__dirname, "..", "qa");

const moduleSlugs = [
  "01-concept-of-entrepreneurship",
  "02-characteristics-of-entrepreneurship",
  "03-types-of-entrepreneurship",
  "04-factors-affecting-entrepreneurs",
  "05-entrepreneurship-mindset",
  "06-inventors-and-entrepreneurs",
  "07-companies-and-startups",
  "08-entrepreneurial-environment-and-growth",
  "09-entrepreneurship-economic-development",
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function assertSuccessfulResponse(request, relativeUrl) {
  const response = await request.get(new URL(relativeUrl, baseUrl).toString());
  assert(
    response.ok(),
    `${relativeUrl} returned HTTP ${response.status()}`
  );
}

async function run() {
  fs.mkdirSync(qaDirectory, { recursive: true });
  assert(fs.existsSync(chromePath), `Chrome not found at ${chromePath}`);

  const browser = await chromium.launch({
    executablePath: chromePath,
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(20000);
  page.setDefaultNavigationTimeout(30000);
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));

  console.log("Opening desktop homepage...");
  const response = await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  assert(response && response.ok(), `Homepage failed with HTTP ${response?.status()}`);
  await page.locator(".home-module-card").first().waitFor();
  assert(
    (await page.locator(".unit-navigation details").count()) === 6,
    "Course menu must contain five units plus MCQs"
  );
  assert(
    (await page.locator(".home-module-card").count()) === 9,
    "Homepage must contain exactly nine Unit I module cards"
  );
  assert(
    await page.locator("#course-sidebar").isVisible(),
    "Desktop unit sidebar is not visible"
  );
  await page.screenshot({
    path: path.join(qaDirectory, "home-desktop.png"),
    fullPage: false,
  });
  console.log("Desktop viewport captured.");

  console.log("Checking module launch paths...");
  for (const slug of moduleSlugs) {
    await assertSuccessfulResponse(context.request, `modules/${slug}/index.html`);
    await assertSuccessfulResponse(context.request, `modules/${slug}/story.html`);
  }

  console.log("Checking mobile navigation...");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: "domcontentloaded" });
  const menuToggle = page.locator(".course-menu-toggle");
  assert(await menuToggle.isVisible(), "Mobile course-menu button is not visible");
  await menuToggle.click();
  assert(
    (await menuToggle.getAttribute("aria-expanded")) === "true",
    "Mobile course menu did not open"
  );
  assert(
    await page.locator("#course-sidebar").isVisible(),
    "Mobile course sidebar is not visible after opening"
  );
  await page.keyboard.press("Escape");
  assert(
    (await menuToggle.getAttribute("aria-expanded")) === "false",
    "Escape did not close the mobile course menu"
  );
  await page.screenshot({
    path: path.join(qaDirectory, "home-mobile.png"),
    fullPage: false,
  });

  await browser.close();
  assert(
    consoleErrors.length === 0,
    `Browser console errors:\n${consoleErrors.join("\n")}`
  );
  console.log("BROWSER SMOKE TEST PASSED");
  console.log("- Chrome desktop layout: passed");
  console.log("- Chrome mobile layout and menu: passed");
  console.log("- Nine module wrappers and Storyline launch files: HTTP 200");
  console.log("- Browser console errors: 0");
}

run().catch((error) => {
  console.error(`BROWSER SMOKE TEST FAILED\n${error.stack}`);
  process.exitCode = 1;
});
