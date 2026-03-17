#!/usr/bin/env node
import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { runWithLineage } from '../../lib/lineage-hook.js'
import { getDatasetPath } from '../../lib/registry-loader.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const rootDir = path.resolve(__dirname, '..', '..', '..')
const webPublicDataDir = getDatasetPath('web_public_data', path.join(rootDir, 'apps', 'web', 'public', 'data'))

const sourceFile = process.argv[2] ? path.resolve(process.argv[2]) : path.join(webPublicDataDir, 'video-index.json')
const destDir = process.argv[3] ? path.resolve(process.argv[3]) : path.dirname(sourceFile)

const canonicalDecades = []
for (let year = 1950; year <= 2020; year += 10) canonicalDecades.push(`${year}s`)

const parseYearValue = (value) => {
  if (typeof value === 'number' && Number.isFinite(value)) return Math.trunc(value)
  if (typeof value === 'string' && /^\d{4}$/.test(value.trim())) return Number(value.trim())
  return null
}

const parseYearFromFilename = (row) => {
  const rawPath =
    typeof row?.filePath === 'string'
      ? row.filePath
      : typeof row?.filepath === 'string'
        ? row.filepath
        : ''
  if (!rawPath) return null

  const filename = rawPath.split(/[/\\]/).pop() || rawPath
  const match = filename.match(/\b(19\d{2}|20\d{2})\b/)
  return match ? Number(match[1]) : null
}

const decadeLabelForYear = (year) => `${Math.floor(year / 10) * 10}s`

const loadItems = async () => {
  const raw = await fs.readFile(sourceFile, 'utf8')
  const body = JSON.parse(raw)
  if (Array.isArray(body)) return body
  if (Array.isArray(body?.items)) return body.items
  if (Array.isArray(body?.videos)) return body.videos
  return []
}

const writeOutputs = async () => {
  const items = await loadItems()
  await fs.mkdir(destDir, { recursive: true })

  const buckets = new Map()
  for (const decade of canonicalDecades) buckets.set(decade, [])

  let reassignedTo2020s = 0
  let filenameResolved = 0

  for (const row of items) {
    let year = parseYearValue(row?.year)
    if (year === null) {
      year = parseYearFromFilename(row)
      if (year !== null) filenameResolved += 1
    }
    if (year === null) {
      year = 2020
      reassignedTo2020s += 1
    }

    const decade = decadeLabelForYear(year)
    if (!buckets.has(decade)) buckets.set(decade, [])
    buckets.get(decade).push(row)
  }

  const decadeLabels = [...buckets.keys()].sort((left, right) => Number(left.replace('s', '')) - Number(right.replace('s', '')))
  for (const decade of decadeLabels) {
    const outPath = path.join(destDir, `video-index-${decade}.json`)
    const rows = buckets.get(decade) ?? []
    await fs.writeFile(outPath, `${JSON.stringify(rows)}\n`, 'utf8')
    console.log(`[split-index] wrote ${path.basename(outPath)} (${rows.length} items)`)
  }

  console.log(`[split-index] total items=${items.length}`)
  console.log(`[split-index] filename-resolved years=${filenameResolved}`)
  console.log(`[split-index] reassigned to 2020s=${reassignedTo2020s}`)
}

runWithLineage(writeOutputs).catch((error) => {
  console.error('[split-index] failed:', error)
  process.exit(1)
})
