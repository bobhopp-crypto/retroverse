import fs from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'
import { runLineageGeneration } from '../lib/lineage-hook.js'
import { getDatasetPath } from '../lib/registry-loader.js'

interface WeeklyContext {
  week: number
  start_date: string
  end_date: string
  song_title: string
  song_artist: string
  movie_anchor_title: string
  movie_anchor_genre: string
  movie_pool_titles: [string, string]
  tv_anchor: string
  tv_daytime: string
  tv_pbs: string
  headline: string
  mood_tags: string[]
}

interface RenderReport {
  source_json: string
  template_file: string
  css_file: string
  output_dir: string
  cards_generated: number
  warnings: string[]
  errors: string[]
  generated_at: string
}

const ROOT = process.cwd()
const CARDS_DATASET_DIR = getDatasetPath('cards_1974_dataset', path.join(ROOT, 'data', 'derived', 'cards', '1974'))
const WEB_PUBLIC_CARDS_DIR = getDatasetPath('web_public_cards_1974', path.join(ROOT, 'apps', 'web', 'public', 'cards', '1974'))
const DATA_PATH = path.join(CARDS_DATASET_DIR, '1974_weekly_context.json')
const TEMPLATE_PATH = path.join(ROOT, 'pipelines', 'cards-1974', 'card_template.html')
const CSS_PATH = path.join(ROOT, 'pipelines', 'cards-1974', 'card.css')
const OUTPUT_DIR = WEB_PUBLIC_CARDS_DIR
const REPORT_PATH = path.join(CARDS_DATASET_DIR, '1974_card_render_report.json')

const LAYOUTS = ['a', 'b', 'c'] as const

type LayoutFamily = (typeof LAYOUTS)[number]

function padWeek(week: number): string {
  return String(week).padStart(2, '0')
}

function layoutForWeek(week: number): LayoutFamily {
  return LAYOUTS[(week - 1) % LAYOUTS.length]
}

function asInlineJson(value: unknown): string {
  return JSON.stringify(value).replace(/</g, '\\u003c')
}

function normalizeWeeks(raw: WeeklyContext[], warnings: string[]): WeeklyContext[] {
  const byWeek = new Map<number, WeeklyContext>()

  raw.forEach((row) => {
    if (Number.isFinite(row.week) && row.week >= 1 && row.week <= 52) {
      byWeek.set(row.week, row)
    }
  })

  const result: WeeklyContext[] = []

  for (let week = 1; week <= 52; week += 1) {
    const existing = byWeek.get(week)
    if (existing) {
      result.push(existing)
      continue
    }

    warnings.push(`Week ${week} missing from JSON; rendering fallback placeholder row.`)
    result.push({
      week,
      start_date: '',
      end_date: '',
      song_title: '',
      song_artist: '',
      movie_anchor_title: '',
      movie_anchor_genre: '',
      movie_pool_titles: ['', ''],
      tv_anchor: '',
      tv_daytime: '',
      tv_pbs: '',
      headline: '',
      mood_tags: [],
    })
  }

  return result
}

function collectWeekWarnings(weekRow: WeeklyContext): string[] {
  const rowWarnings: string[] = []

  if (!weekRow.start_date || !weekRow.end_date) rowWarnings.push('date range incomplete')
  if (!weekRow.song_title || !weekRow.song_artist) rowWarnings.push('song information incomplete')
  if (!weekRow.movie_anchor_title || !weekRow.movie_anchor_genre) rowWarnings.push('movie anchor incomplete')
  if (!weekRow.tv_anchor || !weekRow.tv_daytime || !weekRow.tv_pbs) rowWarnings.push('TV context incomplete')
  if (!weekRow.headline) rowWarnings.push('headline missing')
  if (!Array.isArray(weekRow.movie_pool_titles) || weekRow.movie_pool_titles.filter(Boolean).length < 2) {
    rowWarnings.push('movie_pool_titles has fewer than 2 titles')
  }
  if (!Array.isArray(weekRow.mood_tags) || weekRow.mood_tags.length === 0) {
    rowWarnings.push('mood_tags missing')
  }

  return rowWarnings
}

function buildCardHtml(template: string, css: string, weekRow: WeeklyContext, layout: LayoutFamily): string {
  return template
    .replace('__CARD_CSS__', css)
    .replace('__CARD_DATA_JSON__', asInlineJson(weekRow))
    .replace('__LAYOUT_FAMILY__', layout.toUpperCase())
}

async function clearExistingCards() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true })
  const files = await fs.readdir(OUTPUT_DIR)
  await Promise.all(
    files
      .filter((file) => /^week-\d{2}\.png$/.test(file))
      .map((file) => fs.unlink(path.join(OUTPUT_DIR, file))),
  )
}

async function main() {
  const warnings: string[] = []
  const errors: string[] = []

  const [dataRaw, template, css] = await Promise.all([
    fs.readFile(DATA_PATH, 'utf8'),
    fs.readFile(TEMPLATE_PATH, 'utf8'),
    fs.readFile(CSS_PATH, 'utf8'),
  ])

  const parsedData = JSON.parse(dataRaw) as WeeklyContext[]
  if (!Array.isArray(parsedData)) {
    throw new Error(`Expected ${DATA_PATH} to contain an array of week rows.`)
  }

  const weeks = normalizeWeeks(parsedData, warnings)
  await clearExistingCards()

  let browser
  try {
    browser = await chromium.launch({ headless: true })
  } catch (error) {
    throw new Error(
      `Playwright could not start Chromium. Run: npx playwright install chromium.\nOriginal error: ${String(error)}`,
    )
  }

  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  })

  try {
    for (const weekRow of weeks) {
      const rowWarnings = collectWeekWarnings(weekRow)
      rowWarnings.forEach((message) => warnings.push(`Week ${weekRow.week}: ${message}`))

      const weekLabel = padWeek(weekRow.week)
      const outputFile = path.join(OUTPUT_DIR, `week-${weekLabel}.png`)
      const layout = layoutForWeek(weekRow.week)
      const html = buildCardHtml(template, css, weekRow, layout)

      await page.setContent(html, { waitUntil: 'networkidle' })
      await page.locator('#card-canvas').screenshot({ path: outputFile, type: 'png' })
    }
  } catch (error) {
    errors.push(String(error))
  } finally {
    await page.close()
    await browser.close()
  }

  const report: RenderReport = {
    source_json: DATA_PATH,
    template_file: TEMPLATE_PATH,
    css_file: CSS_PATH,
    output_dir: OUTPUT_DIR,
    cards_generated: 52,
    warnings,
    errors,
    generated_at: new Date().toISOString(),
  }

  await fs.mkdir(path.dirname(REPORT_PATH), { recursive: true })
  await fs.writeFile(REPORT_PATH, `${JSON.stringify(report, null, 2)}\n`, 'utf8')

  console.log(`[1974 render] Cards generated: 52`)
  console.log(`[1974 render] Output: ${OUTPUT_DIR}`)
  console.log(`[1974 render] Report: ${REPORT_PATH}`)
  console.log(`[1974 render] Warnings: ${warnings.length}`)
  console.log(`[1974 render] Errors: ${errors.length}`)

  if (warnings.length > 0) {
    warnings.forEach((warning) => console.warn(`[1974 render][warning] ${warning}`))
  }

  if (errors.length > 0) {
    errors.forEach((error) => console.error(`[1974 render][error] ${error}`))
    process.exitCode = 1
  }
}

main()
  .then(() => {
    if (process.exitCode && process.exitCode !== 0) return
    runLineageGeneration()
  })
  .catch((error) => {
    console.error(`[1974 render][fatal] ${error instanceof Error ? error.message : String(error)}`)
    process.exitCode = 1
  })
