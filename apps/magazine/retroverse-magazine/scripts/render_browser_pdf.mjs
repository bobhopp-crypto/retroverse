#!/usr/bin/env node
/**
 * Export RetroVerse magazine to PDF via Playwright.
 * Loads combined_for_print.html and prints with Letter size, print CSS.
 *
 * Usage: node scripts/render_browser_pdf.mjs [--year=1978]
 * Output: issues/{year}/output/retroverse_{year}.pdf
 */

import { chromium } from "playwright";
import { fileURLToPath } from "url";
import { dirname, join, resolve } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");

const yearArg = process.argv.find((a) => a.startsWith("--year="));
const year = yearArg ? parseInt(yearArg.split("=")[1], 10) : parseInt(process.env.YEAR || "1978", 10);

const layoutDir = join(PROJECT_ROOT, "issues", String(year), "layout");
const outputDir = join(PROJECT_ROOT, "issues", String(year), "output");
const htmlPath = join(layoutDir, "combined_for_print.html");
const pdfPath = join(outputDir, `retroverse_${year}.pdf`);

async function main() {
  const fs = await import("fs");
  if (!fs.existsSync(htmlPath)) {
    console.error(`Missing: ${htmlPath}`);
    console.error("Run: python3 scripts/build_issue.py --year", year);
    process.exit(1);
  }

  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage();

  const fileUrl = `file://${htmlPath}`;
  await page.goto(fileUrl, { waitUntil: "networkidle" });

  await page.pdf({
    path: pdfPath,
    format: "Letter",
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: "0.5in", right: "0.5in", bottom: "0.5in", left: "0.5in" },
  });

  await browser.close();
  console.log(`PDF saved: ${pdfPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
