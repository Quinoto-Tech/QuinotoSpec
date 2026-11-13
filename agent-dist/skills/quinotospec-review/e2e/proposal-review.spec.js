import fs from "node:fs";
import path from "node:path";
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.QS_BASE_URL || "";
const PROPOSAL_SLUG = process.env.QS_PROPOSAL_SLUG || "";
const TASK_ID = process.env.QS_TASK_ID || "";
const OUTPUT_DIR = process.env.QS_OUTPUT_DIR || "test-results";

const checks = [];
const consoleErrors = [];
const pageErrors = [];
const failedRequests = [];
const screenshots = [];

function addCheck(id, status, detail) {
  checks.push({ id, status, detail: String(detail || "") });
}

function screenshotPath(name) {
  const directory = path.join(OUTPUT_DIR, "screenshots");
  fs.mkdirSync(directory, { recursive: true });
  return path.join(directory, name + ".png");
}

test.describe.configure({ mode: "serial" });

test.beforeAll(() => {
  fs.mkdirSync(path.join(OUTPUT_DIR, "screenshots"), { recursive: true });
  if (!BASE_URL) throw new Error("QS_BASE_URL no definido");
  if (!PROPOSAL_SLUG) throw new Error("QS_PROPOSAL_SLUG no definido");
});

test("proposal renders correctly in the local UI", async ({ page }) => {
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(String(error)));
  page.on("requestfailed", (request) => {
    failedRequests.push(
      `${request.method()} ${request.url()} ${request.failure()?.errorText || "failed"}`,
    );
  });

  const response = await page.goto(`${BASE_URL}/proposals/${encodeURIComponent(PROPOSAL_SLUG)}`, {
    waitUntil: "domcontentloaded",
  });
  addCheck("http-status", response && response.status() === 200 ? "pass" : "fail", response ? response.status() : "sin respuesta");
  expect.soft(response?.status(), "la pagina de propuesta debe responder 200").toBe(200);

  const title = page.locator('[data-testid="proposal-title"]');
  addCheck("proposal-title", (await title.count()) === 1 ? "pass" : "fail", "titulo de propuesta");
  expect.soft(await title.count(), "debe existir un titulo de propuesta").toBe(1);

  const content = page.locator('[data-testid="proposal-content"]');
  const contentCount = await content.count();
  addCheck("proposal-content", contentCount === 1 ? "pass" : "fail", "contenido Markdown de la propuesta");
  expect.soft(contentCount, "debe existir el contenido renderizado").toBe(1);

  if (contentCount === 1) {
    const text = await content.innerText();
    addCheck("proposal-text", text.trim().length > 0 ? "pass" : "fail", "contenido no vacio");
    expect.soft(text.trim().length, "el contenido no debe estar vacio").toBeGreaterThan(0);
  }

  const mermaidBlocks = page.locator('[data-testid="mermaid-block"]');
  const mermaidCount = await mermaidBlocks.count();
  if (mermaidCount > 0) {
    await content.scrollIntoViewIfNeeded().catch(() => {});
    await page
      .waitForFunction(
        () =>
          Array.from(document.querySelectorAll('[data-testid="mermaid-block"]')).every((element) =>
            ["rendered", "error"].includes(element.getAttribute("data-mermaid-state") || ""),
          ),
        null,
        { timeout: 20_000 },
      )
      .catch(() => {});
    const rendered = await page
      .locator('[data-testid="mermaid-block"][data-mermaid-state="rendered"]')
      .count();
    addCheck("mermaid", rendered === mermaidCount ? "pass" : "fail", `${rendered}/${mermaidCount} bloques renderizados`);
    expect.soft(rendered, "todos los bloques Mermaid deben renderizarse").toBe(mermaidCount);
  } else {
    addCheck("mermaid", "pass", "sin bloques Mermaid");
  }

  const viewports = [
    { name: "desktop", width: 1440, height: 900 },
    { name: "tablet", width: 768, height: 1024 },
    { name: "mobile", width: 390, height: 844 },
  ];
  for (const viewport of viewports) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.waitForTimeout(150);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth + 1,
    );
    addCheck(
      `overflow-${viewport.name}`,
      overflow ? "warn" : "pass",
      overflow ? "hay overflow horizontal" : "sin overflow horizontal",
    );
    const file = screenshotPath(viewport.name);
    await page.screenshot({ path: file, fullPage: true });
    screenshots.push(file);
  }

  const h1Count = await page.locator("h1").count();
  addCheck("a11y-h1", h1Count === 1 ? "pass" : "warn", `${h1Count} h1`);
  const searchInput = page.locator('[data-testid="proposal-search"]');
  if ((await searchInput.count()) > 0) {
    const hasLabel = await searchInput.first().evaluate((element) => {
      const id = element.getAttribute("id");
      return Boolean(element.getAttribute("aria-label") || (id && document.querySelector(`label[for="${id}"]`)));
    });
    addCheck("a11y-search-label", hasLabel ? "pass" : "warn", "label del buscador");
  }

  if (TASK_ID) {
    const taskResponse = await page.goto(`${BASE_URL}/tasks/${encodeURIComponent(TASK_ID)}`, {
      waitUntil: "domcontentloaded",
    });
    addCheck("task-http-status", taskResponse && taskResponse.status() === 200 ? "pass" : "fail", taskResponse ? taskResponse.status() : "sin respuesta");
    expect.soft(taskResponse?.status(), "la pagina de tarea debe responder 200").toBe(200);
    const taskTitle = page.locator('[data-testid="task-title"]');
    addCheck("task-title", (await taskTitle.count()) === 1 ? "pass" : "fail", "titulo de tarea");
    expect.soft(await taskTitle.count(), "debe existir un titulo de tarea").toBe(1);
  }

  expect.soft(pageErrors, "no debe haber pageerror").toEqual([]);
  expect.soft(consoleErrors, "no debe haber console.error").toEqual([]);
  expect.soft(failedRequests, "no debe haber requests fallidos").toEqual([]);
});

test.afterAll(() => {
  const failedChecks = checks.filter((check) => check.status === "fail");
  const warnedChecks = checks.filter((check) => check.status === "warn");
  let result = "pass";
  if (pageErrors.length || consoleErrors.length || failedRequests.length || failedChecks.length) {
    result = "fail";
  } else if (warnedChecks.length) {
    result = "warn";
  }
  const payload = {
    schema_version: 1,
    base_url: BASE_URL,
    proposal: PROPOSAL_SLUG,
    task_id: TASK_ID || null,
    viewports: ["1440x900", "768x1024", "390x844"],
    checks,
    console_errors: consoleErrors,
    page_errors: pageErrors,
    failed_requests: failedRequests,
    screenshots,
    result,
    generated_at: new Date().toISOString(),
  };
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUTPUT_DIR, "playwright-raw.json"), JSON.stringify(payload, null, 2) + "\n", "utf-8");
});
