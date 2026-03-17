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

const GRAVITY_DIR = path.join(ROOT_DIR, 'public', 'data', 'artist-gravity')
const OUTPUT_PATH = path.join(ROOT_DIR, 'public', 'data', 'artist-timelines.json')

const toNumber = (value) => {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value)
    if (Number.isFinite(parsed)) return parsed
  }
  return null
}

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

const writeJsonAtomic = async (outputPath, payload) => {
  const tempPath = `${outputPath}.tmp-${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}`
  await fs.writeFile(tempPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8')
  await fs.rename(tempPath, outputPath)
}

const run = async () => {
  const byArtist = new Map()

  for (let year = START_YEAR; year <= END_YEAR; year += 1) {
    const gravityPath = path.join(GRAVITY_DIR, `${year}.json`)
    const rows = await readJsonArrayOrEmpty(gravityPath)

    for (let index = 0; index < rows.length; index += 1) {
      const row = rows[index]
      if (!row || typeof row !== 'object') continue

      const rawArtist = typeof row.artist === 'string' ? row.artist.trim() : ''
      if (!rawArtist) continue

      const normalizedArtist = normalizeArtist(rawArtist)
      if (!normalizedArtist) continue

      const score = toNumber(row.score)
      if (score === null) continue

      let bucket = byArtist.get(normalizedArtist)
      if (!bucket) {
        bucket = {
          artist: rawArtist,
          years: [],
        }
        byArtist.set(normalizedArtist, bucket)
      }

      bucket.years.push({
        year,
        rank: index + 1,
        score,
      })
    }
  }

  const output = [...byArtist.values()]
    .map((entry) => ({
      artist: entry.artist,
      years: [...entry.years].sort((left, right) => left.year - right.year || left.rank - right.rank),
    }))
    .sort((left, right) => left.artist.localeCompare(right.artist))

  await fs.mkdir(path.dirname(OUTPUT_PATH), { recursive: true })
  await writeJsonAtomic(OUTPUT_PATH, output)

  console.log(`[artist-timelines] wrote ${OUTPUT_PATH} (${output.length} artists)`)
}

run().catch((error) => {
  console.error('[artist-timelines] failed:', error)
  process.exit(1)
})
