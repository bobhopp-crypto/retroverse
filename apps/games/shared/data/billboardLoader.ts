import Database from 'better-sqlite3'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { BillboardSongRecord } from '../types/gameData.js'

const SOURCE_SYSTEM = 'RVA-HOT100'
const YEAR_CUTOFF = 2000

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(MODULE_DIR, '../../../../')
const DB_PATHS = [
  path.join(process.cwd(), 'data', 'raw', 'charts', 'billboard-hot-100.db'),
  path.join(REPO_ROOT, 'data', 'raw', 'charts', 'billboard-hot-100.db'),
  path.join(process.cwd(), 'retroverse-data', 'databases', 'source_billboard_hot_100.db'),
]

type SongRow = {
  work_id: string | null
  issue_date: string | null
  rank: number | null
  title: string | null
  artist: string | null
}

type SongAccumulator = {
  artist: string
  title: string
  ranksByDate: Map<string, number>
}

let cachedSongs: BillboardSongRecord[] | null = null

const toDisplayText = (value: unknown, fallback: string) => {
  if (typeof value !== 'string') return fallback
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : fallback
}

const normalizeText = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

const findDbPath = () => {
  for (const candidate of DB_PATHS) {
    if (fs.existsSync(candidate)) return candidate
  }
  throw new Error('Billboard Hot 100 database not found')
}

export const loadBillboardSongs = (): BillboardSongRecord[] => {
  if (cachedSongs) return cachedSongs

  const db = new Database(findDbPath(), { readonly: true, fileMustExist: true })

  try {
    const rows = db
      .prepare(
        `SELECT ee.work_id AS work_id,
                e.issue_date AS issue_date,
                ee.rank AS rank,
                w.title_display AS title,
                p.name_display AS artist
           FROM event_entry ee
           JOIN event e ON ee.event_id = e.event_id
           JOIN work w ON ee.work_id = w.work_id
      LEFT JOIN person p ON w.primary_person_id = p.person_id
          WHERE e.source_system = ?
            AND ee.rank BETWEEN 1 AND 100
          ORDER BY ee.work_id ASC, e.issue_date ASC, ee.rank ASC`
      )
      .all(SOURCE_SYSTEM) as SongRow[]

    const songs = new Map<string, SongAccumulator>()

    for (const row of rows) {
      const issueDate = typeof row.issue_date === 'string' ? row.issue_date.trim() : ''
      const rank = Number(row.rank)

      if (!/^\d{4}-\d{2}-\d{2}$/.test(issueDate)) continue
      if (!Number.isInteger(rank) || rank < 1 || rank > 100) continue

      const title = toDisplayText(row.title, 'Unknown Title')
      const artist = toDisplayText(row.artist, 'Unknown Artist')
      const fallbackId = `${normalizeText(artist)}::${normalizeText(title)}`
      const songId = typeof row.work_id === 'string' && row.work_id.trim() ? row.work_id.trim() : fallbackId

      const current =
        songs.get(songId) ??
        {
          artist,
          title,
          ranksByDate: new Map<string, number>(),
        }

      if (current.artist === 'Unknown Artist' && artist !== 'Unknown Artist') current.artist = artist
      if (current.title === 'Unknown Title' && title !== 'Unknown Title') current.title = title

      const existingRank = current.ranksByDate.get(issueDate)
      if (existingRank === undefined || rank < existingRank) {
        current.ranksByDate.set(issueDate, rank)
      }

      songs.set(songId, current)
    }

    cachedSongs = Array.from(songs.values())
      .map((song) => {
        const orderedDates = Array.from(song.ranksByDate.keys()).sort()
        if (orderedDates.length === 0) return null

        const year = Number.parseInt(orderedDates[0]!.slice(0, 4), 10)
        if (!Number.isInteger(year) || year >= YEAR_CUTOFF) return null

        const chartRun = orderedDates.map((date) => song.ranksByDate.get(date)!).filter((rank) => Number.isInteger(rank))
        if (chartRun.length === 0) return null

        return {
          artist: song.artist,
          title: song.title,
          year,
          chart_run: chartRun,
          peak: Math.min(...chartRun),
        } satisfies BillboardSongRecord
      })
      .filter((song): song is BillboardSongRecord => song !== null)
      .sort((left, right) => left.year - right.year || left.artist.localeCompare(right.artist) || left.title.localeCompare(right.title))

    return cachedSongs
  } finally {
    db.close()
  }
}

export const getBillboardSongCount = () => loadBillboardSongs().length

