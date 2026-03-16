import { loadBillboardSongs } from './billboardLoader.js'
import { loadVideoMetadata } from './videoLoader.js'
import type { BillboardSongRecord, VideoMetadataRecord } from '../types/gameData.js'

const YEAR_CUTOFF = 2000
const MIN_CHART_WEEKS = 5

type SongPools = {
  playableSongs: BillboardSongRecord[]
  hitSongs: BillboardSongRecord[]
  yearIdentifiers: BillboardSongRecord[]
  chartClimbers: BillboardSongRecord[]
}

let songPoolsPromise: Promise<SongPools> | null = null
let videoPuzzlesPromise: Promise<VideoMetadataRecord[]> | null = null

const normalizeText = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

const sortSongs = (left: BillboardSongRecord, right: BillboardSongRecord) =>
  left.year - right.year || left.artist.localeCompare(right.artist) || left.title.localeCompare(right.title)

const sortVideos = (left: VideoMetadataRecord, right: VideoMetadataRecord) =>
  left.year - right.year || left.artist.localeCompare(right.artist) || left.title.localeCompare(right.title)

const sanitizeChartRun = (value: unknown) => {
  if (!Array.isArray(value)) return []

  return value
    .map((entry) => Number(entry))
    .filter((entry) => Number.isInteger(entry) && entry >= 1 && entry <= 100)
}

const normalizeSong = (song: BillboardSongRecord): BillboardSongRecord | null => {
  const artist = typeof song.artist === 'string' ? song.artist.trim() : ''
  const title = typeof song.title === 'string' ? song.title.trim() : ''
  const year = Number(song.year)
  const chartRun = sanitizeChartRun(song.chart_run)

  if (!artist || !title) return null
  if (!Number.isInteger(year)) return null
  if (chartRun.length < MIN_CHART_WEEKS) return null

  return {
    artist,
    title,
    year,
    peak: Math.min(...chartRun),
    chart_run: chartRun,
  }
}

const preferSong = (current: BillboardSongRecord | undefined, candidate: BillboardSongRecord) => {
  if (!current) return candidate
  if (candidate.chart_run.length !== current.chart_run.length) {
    return candidate.chart_run.length > current.chart_run.length ? candidate : current
  }
  if (candidate.peak !== current.peak) {
    return candidate.peak < current.peak ? candidate : current
  }
  return current
}

const buildSongPools = (): SongPools => {
  const deduped = new Map<string, BillboardSongRecord>()

  for (const song of loadBillboardSongs()) {
    const normalized = normalizeSong(song)
    if (!normalized) continue

    const key = `${normalizeText(normalized.artist)}::${normalizeText(normalized.title)}::${normalized.year}`
    deduped.set(key, preferSong(deduped.get(key), normalized))
  }

  const songs = Array.from(deduped.values()).sort(sortSongs)
  const byYear = (song: BillboardSongRecord) => song.year < YEAR_CUTOFF

  return {
    playableSongs: songs.filter((song) => byYear(song) && song.chart_run.length >= 6),
    hitSongs: songs.filter((song) => byYear(song) && song.peak <= 20 && song.chart_run.length >= 8),
    yearIdentifiers: songs.filter((song) => byYear(song) && song.peak <= 10),
    chartClimbers: songs.filter((song) => byYear(song) && song.chart_run.length >= 10 && song.peak <= 20),
  }
}

const normalizeVideo = (video: VideoMetadataRecord): VideoMetadataRecord | null => {
  const artist = typeof video.artist === 'string' ? video.artist.trim() : ''
  const title = typeof video.title === 'string' ? video.title.trim() : ''
  const year = Number(video.year)
  const thumbnail = typeof video.thumbnail === 'string' ? video.thumbnail.trim() : ''

  if (!artist || !title) return null
  if (!Number.isInteger(year)) return null
  if (year >= YEAR_CUTOFF) return null

  return {
    artist,
    title,
    year,
    thumbnail,
  }
}

const buildVideoPuzzles = (): VideoMetadataRecord[] => {
  const deduped = new Map<string, VideoMetadataRecord>()

  for (const video of loadVideoMetadata()) {
    const normalized = normalizeVideo(video)
    if (!normalized) continue

    const key = `${normalizeText(normalized.artist)}::${normalizeText(normalized.title)}::${normalized.year}`
    const current = deduped.get(key)

    if (!current || (!current.thumbnail && normalized.thumbnail)) {
      deduped.set(key, normalized)
    }
  }

  return Array.from(deduped.values()).sort(sortVideos)
}

const getSongPools = async () => {
  if (!songPoolsPromise) {
    songPoolsPromise = Promise.resolve()
      .then(buildSongPools)
      .catch((error) => {
        songPoolsPromise = null
        throw error
      })
  }

  return songPoolsPromise
}

export const getPlayableSongs = async () => (await getSongPools()).playableSongs

export const getHitSongs = async () => (await getSongPools()).hitSongs

export const getYearIdentifiers = async () => (await getSongPools()).yearIdentifiers

export const getChartClimbers = async () => (await getSongPools()).chartClimbers

export const getVideoPuzzles = async () => {
  if (!videoPuzzlesPromise) {
    videoPuzzlesPromise = Promise.resolve()
      .then(buildVideoPuzzles)
      .catch((error) => {
        videoPuzzlesPromise = null
        throw error
      })
  }

  return videoPuzzlesPromise
}
