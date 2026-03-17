#!/usr/bin/env node
import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { normalizeArtist } from '../src/lib/normalize.ts'

const START_YEAR = 1958
const END_YEAR = 2024

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT_DIR = path.resolve(__dirname, '..')

const CHARTS_DIR = path.join(ROOT_DIR, 'public', 'data', 'charts')
const ALBUMS_DIR = path.join(ROOT_DIR, 'public', 'data', 'albums')
const OUTPUT_DIR = path.join(ROOT_DIR, 'public', 'data', 'artist-gravity')

const toNumber = (value) => {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value)
    if (Number.isFinite(parsed)) return parsed
  }
  return null
}

const toArtist = (value) => (typeof value === 'string' ? value.trim() : '')

const readJsonArrayOrEmpty = async (filePath) => {
  try {
    const raw = await fs.readFile(filePath, 'utf8')
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') return []
    throw error
  }
}

const scoreEntry = (peak, weeks) => (100 - peak) + weeks * 0.1

const roundScore = (value) => Math.round(value * 10) / 10

const writeJsonAtomic = async (outputPath, payload) => {
  const tempPath = `${outputPath}.tmp-${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}`
  await fs.writeFile(tempPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8')
  await fs.rename(tempPath, outputPath)
}

const buildYearGravity = async (year) => {
  const chartsPath = path.join(CHARTS_DIR, `${year}.json`)
  const albumsPath = path.join(ALBUMS_DIR, `${year}.json`)

  const [chartRows, albumRows] = await Promise.all([readJsonArrayOrEmpty(chartsPath), readJsonArrayOrEmpty(albumsPath)])

  const byArtist = new Map()

  const accumulate = (rows) => {
    for (const row of rows) {
      if (!row || typeof row !== 'object') continue
      const artistRaw = toArtist(row.artist)
      if (!artistRaw) continue

      const normalized = normalizeArtist(artistRaw)
      if (!normalized) continue

      const peak = toNumber(row.peak)
      const weeks = toNumber(row.weeks)
      if (peak === null || weeks === null) continue

      const delta = scoreEntry(peak, weeks)
      if (!Number.isFinite(delta)) continue

      let bucket = byArtist.get(normalized)
      if (!bucket) {
        bucket = {
          score: 0,
          bestLabel: artistRaw,
          bestLabelScore: 0,
          labelScores: new Map(),
        }
        byArtist.set(normalized, bucket)
      }

      bucket.score += delta

      const labelScore = (bucket.labelScores.get(artistRaw) ?? 0) + delta
      bucket.labelScores.set(artistRaw, labelScore)
      if (labelScore > bucket.bestLabelScore) {
        bucket.bestLabel = artistRaw
        bucket.bestLabelScore = labelScore
      }
    }
  }

  accumulate(chartRows)
  accumulate(albumRows)

  return [...byArtist.values()]
    .map((entry) => ({
      artist: entry.bestLabel,
      score: roundScore(entry.score),
    }))
    .sort((left, right) => right.score - left.score || left.artist.localeCompare(right.artist))
}

const run = async () => {
  await fs.mkdir(OUTPUT_DIR, { recursive: true })

  for (let year = START_YEAR; year <= END_YEAR; year += 1) {
    const payload = await buildYearGravity(year)
    const outPath = path.join(OUTPUT_DIR, `${year}.json`)
    await writeJsonAtomic(outPath, payload)
    console.log(`[artist-gravity] ${year}: ${payload.length} artists`)
  }

  console.log(`[artist-gravity] complete ${START_YEAR}-${END_YEAR}`)
}

run().catch((error) => {
  console.error('[artist-gravity] failed:', error)
  process.exit(1)
})
