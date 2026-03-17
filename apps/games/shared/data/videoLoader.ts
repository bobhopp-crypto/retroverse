import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { VideoMetadataRecord } from '../types/gameData.js'

const YEAR_CUTOFF = 2000

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(MODULE_DIR, '../../../../')
const VIDEO_DATA_PATHS = [
  path.join(process.cwd(), 'data', 'derived', 'media-index', 'output', 'video-index.json'),
  path.join(REPO_ROOT, 'data', 'derived', 'media-index', 'output', 'video-index.json'),
  path.join(process.cwd(), 'apps', 'web', 'public', 'data', 'video-index.json'),
]

type RawVideoRecord = {
  artist?: unknown
  author?: unknown
  title?: unknown
  year?: unknown
  thumbnail?: unknown
  thumbnail_url?: unknown
  thumbnailUrl?: unknown
  image?: unknown
  poster?: unknown
  poster_url?: unknown
  posterUrl?: unknown
  tags?: {
    artist?: unknown
    title?: unknown
    year?: unknown
  } | null
}

let cachedVideos: VideoMetadataRecord[] | null = null

const toStringOrEmpty = (value: unknown) => (typeof value === 'string' ? value.trim() : '')

const normalizeText = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

const firstString = (...values: unknown[]) => {
  for (const value of values) {
    const stringValue = toStringOrEmpty(value)
    if (stringValue) return stringValue
  }
  return ''
}

const toYear = (value: unknown) => {
  const parsed = Number(value)
  return Number.isInteger(parsed) ? parsed : null
}

const findVideoDataPath = () => {
  for (const candidate of VIDEO_DATA_PATHS) {
    if (fs.existsSync(candidate)) return candidate
  }
  throw new Error('Video metadata dataset not found')
}

export const loadVideoMetadata = (): VideoMetadataRecord[] => {
  if (cachedVideos) return cachedVideos

  const raw = fs.readFileSync(findVideoDataPath(), 'utf8')
  const parsed = JSON.parse(raw)
  const rows = Array.isArray(parsed)
    ? parsed
    : Array.isArray(parsed?.items)
      ? parsed.items
      : Array.isArray(parsed?.videos)
        ? parsed.videos
        : []

  const deduped = new Map<string, VideoMetadataRecord>()

  for (const row of rows as RawVideoRecord[]) {
    const artist = firstString(row.artist, row.author, row.tags?.artist)
    const title = firstString(row.title, row.tags?.title)
    const year = toYear(row.year ?? row.tags?.year)

    if (!artist || !title || year === null || year >= YEAR_CUTOFF) continue

    const thumbnail = firstString(
      row.thumbnail,
      row.thumbnail_url,
      row.thumbnailUrl,
      row.image,
      row.poster,
      row.poster_url,
      row.posterUrl,
    )

    const key = `${normalizeText(artist)}::${normalizeText(title)}::${year}`
    const current = deduped.get(key)

    if (!current || (!current.thumbnail && thumbnail)) {
      deduped.set(key, {
        artist,
        title,
        year,
        thumbnail,
      })
    }
  }

  cachedVideos = Array.from(deduped.values()).sort(
    (left, right) => left.year - right.year || left.artist.localeCompare(right.artist) || left.title.localeCompare(right.title),
  )

  return cachedVideos
}

export const getVideoMetadataCount = () => loadVideoMetadata().length

