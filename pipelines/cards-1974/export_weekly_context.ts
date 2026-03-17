import fs from 'node:fs'
import path from 'node:path'
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

interface ParseReport {
  source_file: string
  generated_weeks: number
  source_rows: number
  warnings: string[]
  errors: string[]
  generated_at: string
}

const ROOT = process.cwd()
const CARDS_DATASET_DIR = getDatasetPath('cards_1974_dataset', path.join(ROOT, 'data', 'derived', 'cards', '1974'))
const WEB_PUBLIC_DATA_DIR = getDatasetPath('web_public_data', path.join(ROOT, 'apps', 'web', 'public', 'data'))
const INPUT_PATH = path.join(CARDS_DATASET_DIR, '1974_weekly_context.md')
const OUTPUT_PATH = path.join(CARDS_DATASET_DIR, '1974_weekly_context.json')
const PUBLIC_OUTPUT_PATH = path.join(WEB_PUBLIC_DATA_DIR, '1974_weekly_context.json')
const REPORT_PATH = path.join(CARDS_DATASET_DIR, '1974_weekly_context.parse_report.json')

const FIELD_ALIASES = {
  week: ['week', 'wk'],
  start_date: ['start_date', 'range_start', 'week_start', 'start', 'startdate'],
  end_date: ['end_date', 'range_end', 'week_end', 'end', 'enddate'],
  song_title: ['song_title', 'title', 'song', 'no1_song', 'number_1_song'],
  song_artist: ['song_artist', 'artist', 'no1_artist', 'number_1_artist'],
  movie_anchor_title: ['movie_anchor_title', 'movie_anchor', 'movie_title', 'anchor_movie'],
  movie_anchor_genre: ['movie_anchor_genre', 'movie_genre', 'anchor_movie_genre'],
  movie_pool_titles: ['movie_pool_titles', 'movie_pool', 'movie_pool_title', 'movie_pool_movies'],
  movie_pool_title_1: ['movie_pool_title_1', 'movie_pool_1', 'movie_1', 'movie_pool_a'],
  movie_pool_title_2: ['movie_pool_title_2', 'movie_pool_2', 'movie_2', 'movie_pool_b'],
  tv_anchor: ['tv_anchor', 'tv_anchor_show', 'tv_anchor_program'],
  tv_daytime: ['tv_daytime', 'daytime_tv', 'tv_daytime_show'],
  tv_pbs: ['tv_pbs', 'pbs', 'pbs_show'],
  headline: ['headline', 'news_headline', 'weekly_headline'],
  mood_tags: ['mood_tags', 'mood', 'tags', 'vibe_tags'],
} as const

function normalizeHeader(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[`*]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}

function parseMarkdownRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim())
}

function isSeparatorRow(line: string): boolean {
  const compact = line.replace(/\|/g, '').trim()
  return compact.length > 0 && /^[\-: ]+$/.test(compact)
}

function isMissing(value: string): boolean {
  const normalized = value.trim().toLowerCase()
  return !normalized || normalized === 'missing' || normalized === 'n/a' || normalized === 'na' || normalized === 'tbd'
}

function pickCell(row: Record<string, string>, aliases: readonly string[]): string {
  for (const alias of aliases) {
    if (alias in row) {
      const value = row[alias]?.trim() ?? ''
      if (value) return value
    }
  }
  return ''
}

function parseListCell(raw: string, splitOnComma = false): string[] {
  const value = raw.trim()
  if (!value) return []

  if (value.startsWith('[') && value.endsWith(']')) {
    try {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed)) {
        return parsed
          .map((item) => String(item).trim())
          .filter((item) => item.length > 0)
      }
    } catch {
      // Continue with delimiter-based parsing.
    }
  }

  const divider = splitOnComma ? /\s*[,;]\s*/ : /\s*[;]\s*|\s+\/\s+/
  return value
    .split(divider)
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
}

function normalizePool(items: string[]): [string, string] {
  const clean = items.map((item) => item.trim()).filter((item) => item.length > 0)
  if (clean.length === 0) return ['', '']
  if (clean.length === 1) return [clean[0], '']
  return [clean[0], clean[1]]
}

function emptyWeek(week: number): WeeklyContext {
  return {
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
  }
}

function buildWeeklyRow(row: Record<string, string>, rowIndex: number, warnings: string[], errors: string[]): WeeklyContext | null {
  const weekRaw = pickCell(row, FIELD_ALIASES.week)
  const inferredWeek = Number.parseInt(weekRaw || String(rowIndex + 1), 10)

  if (!Number.isFinite(inferredWeek) || inferredWeek < 1 || inferredWeek > 52) {
    errors.push(`Row ${rowIndex + 1}: invalid week "${weekRaw || '(empty)'}"`)
    return null
  }

  if (!weekRaw) {
    warnings.push(`Row ${rowIndex + 1}: week missing, inferred as ${inferredWeek}.`)
  }

  const moviePoolFromSingle = parseListCell(pickCell(row, FIELD_ALIASES.movie_pool_titles))
  const moviePoolFromSplit = [
    pickCell(row, FIELD_ALIASES.movie_pool_title_1),
    pickCell(row, FIELD_ALIASES.movie_pool_title_2),
  ].filter(Boolean)
  const moviePoolTitles = normalizePool(moviePoolFromSingle.length > 0 ? moviePoolFromSingle : moviePoolFromSplit)

  const moodTags = parseListCell(pickCell(row, FIELD_ALIASES.mood_tags), true)

  const dedupedMoodTags = [...new Set(moodTags)]

  return {
    week: inferredWeek,
    start_date: pickCell(row, FIELD_ALIASES.start_date),
    end_date: pickCell(row, FIELD_ALIASES.end_date),
    song_title: pickCell(row, FIELD_ALIASES.song_title),
    song_artist: pickCell(row, FIELD_ALIASES.song_artist),
    movie_anchor_title: pickCell(row, FIELD_ALIASES.movie_anchor_title),
    movie_anchor_genre: pickCell(row, FIELD_ALIASES.movie_anchor_genre),
    movie_pool_titles: moviePoolTitles,
    tv_anchor: pickCell(row, FIELD_ALIASES.tv_anchor),
    tv_daytime: pickCell(row, FIELD_ALIASES.tv_daytime),
    tv_pbs: pickCell(row, FIELD_ALIASES.tv_pbs),
    headline: pickCell(row, FIELD_ALIASES.headline),
    mood_tags: dedupedMoodTags,
  }
}

function parseMarkdownTable(markdown: string): Record<string, string>[] {
  const tableLines = markdown
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.startsWith('|'))

  if (tableLines.length === 0) {
    throw new Error('No markdown table rows found.')
  }

  const headerLineIndex = tableLines.findIndex((line) => !isSeparatorRow(line))
  if (headerLineIndex === -1) {
    throw new Error('Could not find table header row.')
  }

  const headers = parseMarkdownRow(tableLines[headerLineIndex]).map(normalizeHeader)
  if (headers.length === 0) {
    throw new Error('Table header row is empty.')
  }

  const rows: Record<string, string>[] = []

  for (let index = headerLineIndex + 1; index < tableLines.length; index += 1) {
    const line = tableLines[index]
    if (isSeparatorRow(line)) continue

    const cells = parseMarkdownRow(line)
    const hasContent = cells.some((cell) => cell.trim().length > 0)
    if (!hasContent) continue

    const row: Record<string, string> = {}
    headers.forEach((header, cellIndex) => {
      row[header] = cells[cellIndex]?.trim() ?? ''
    })
    rows.push(row)
  }

  return rows
}

function validateColumnCoverage(rows: Record<string, string>[], warnings: string[]) {
  const availableColumns = new Set<string>()
  rows.forEach((row) => {
    Object.keys(row).forEach((key) => availableColumns.add(key))
  })

  const columnsToCheck: Array<keyof typeof FIELD_ALIASES> = [
    'week',
    'start_date',
    'end_date',
    'song_title',
    'song_artist',
    'movie_anchor_title',
    'movie_anchor_genre',
    'movie_pool_titles',
    'tv_anchor',
    'tv_daytime',
    'tv_pbs',
    'headline',
    'mood_tags',
  ]

  columnsToCheck.forEach((field) => {
    const aliases = FIELD_ALIASES[field]
    const present = aliases.some((alias) => availableColumns.has(alias))
    if (!present) {
      warnings.push(`Input table is missing a recognized column for "${field}".`)
    }
  })
}

function applyWeek52Fallback(weeks: WeeklyContext[], warnings: string[]) {
  const week51 = weeks[50]
  const week52 = weeks[51]

  if (!week51 || !week52) return

  if (isMissing(week52.song_title) && !isMissing(week51.song_title)) {
    week52.song_title = week51.song_title
    warnings.push('Week 52 song_title missing; reused week 51 song_title.')
  }

  if (isMissing(week52.song_artist) && !isMissing(week51.song_artist)) {
    week52.song_artist = week51.song_artist
    warnings.push('Week 52 song_artist missing; reused week 51 song_artist.')
  }
}

function validateWeeks(weeks: WeeklyContext[], warnings: string[]) {
  weeks.forEach((weekRow) => {
    if (!weekRow.start_date) warnings.push(`Week ${weekRow.week}: start_date missing.`)
    if (!weekRow.end_date) warnings.push(`Week ${weekRow.week}: end_date missing.`)
    if (!weekRow.song_title) warnings.push(`Week ${weekRow.week}: song_title missing.`)
    if (!weekRow.song_artist) warnings.push(`Week ${weekRow.week}: song_artist missing.`)
    if (!weekRow.movie_anchor_title) warnings.push(`Week ${weekRow.week}: movie_anchor_title missing.`)
    if (!weekRow.movie_anchor_genre) warnings.push(`Week ${weekRow.week}: movie_anchor_genre missing.`)
    if (!weekRow.tv_anchor) warnings.push(`Week ${weekRow.week}: tv_anchor missing.`)
    if (!weekRow.tv_daytime) warnings.push(`Week ${weekRow.week}: tv_daytime missing.`)
    if (!weekRow.tv_pbs) warnings.push(`Week ${weekRow.week}: tv_pbs missing.`)
    if (!weekRow.headline) warnings.push(`Week ${weekRow.week}: headline missing.`)
    if (!weekRow.movie_pool_titles[0] || !weekRow.movie_pool_titles[1]) {
      warnings.push(`Week ${weekRow.week}: movie_pool_titles should contain two values.`)
    }
    if (weekRow.mood_tags.length === 0) warnings.push(`Week ${weekRow.week}: mood_tags missing.`)
  })
}

function writeJson(filePath: string, data: unknown) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8')
}

function main() {
  if (!fs.existsSync(INPUT_PATH)) {
    throw new Error(
      `Missing ${INPUT_PATH}. Paste/export the Canvas markdown table into this file and rerun npm run build:1974.`,
    )
  }

  const sourceMarkdown = fs.readFileSync(INPUT_PATH, 'utf8')

  const warnings: string[] = []
  const errors: string[] = []

  const sourceRows = parseMarkdownTable(sourceMarkdown)
  validateColumnCoverage(sourceRows, warnings)

  const weeksByNumber = new Map<number, WeeklyContext>()

  sourceRows.forEach((row, rowIndex) => {
    const parsed = buildWeeklyRow(row, rowIndex, warnings, errors)
    if (!parsed) return

    if (weeksByNumber.has(parsed.week)) {
      warnings.push(`Duplicate week ${parsed.week} encountered; later row replaced earlier row.`)
    }

    weeksByNumber.set(parsed.week, parsed)
  })

  const weeks: WeeklyContext[] = []

  for (let week = 1; week <= 52; week += 1) {
    if (weeksByNumber.has(week)) {
      weeks.push(weeksByNumber.get(week) as WeeklyContext)
    } else {
      warnings.push(`Week ${week} is missing from input; generated an empty placeholder row.`)
      weeks.push(emptyWeek(week))
    }
  }

  applyWeek52Fallback(weeks, warnings)
  validateWeeks(weeks, warnings)

  writeJson(OUTPUT_PATH, weeks)
  writeJson(PUBLIC_OUTPUT_PATH, weeks)

  const report: ParseReport = {
    source_file: INPUT_PATH,
    generated_weeks: weeks.length,
    source_rows: sourceRows.length,
    warnings,
    errors,
    generated_at: new Date().toISOString(),
  }

  writeJson(REPORT_PATH, report)

  console.log(`[1974 export] Wrote ${weeks.length} weekly rows to ${OUTPUT_PATH}`)
  console.log(`[1974 export] Mirrored JSON to ${PUBLIC_OUTPUT_PATH}`)
  console.log(`[1974 export] Parse report: ${REPORT_PATH}`)
  console.log(`[1974 export] Warnings: ${warnings.length}`)
  console.log(`[1974 export] Errors: ${errors.length}`)

  if (warnings.length > 0) {
    warnings.forEach((warning) => {
      console.warn(`[1974 export][warning] ${warning}`)
    })
  }

  if (errors.length > 0) {
    errors.forEach((error) => {
      console.error(`[1974 export][error] ${error}`)
    })
  }
}

main()
runLineageGeneration()
