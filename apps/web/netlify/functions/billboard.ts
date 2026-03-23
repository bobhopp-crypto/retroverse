import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { getBillboardSongCount } from '../../../games/shared/data/billboardLoader.js'
import {
  getChartClimbers,
  getHitSongs,
  getPlayableSongs,
  getVideoPuzzles,
  getYearIdentifiers,
} from '../../../games/shared/data/playablePools.js'
import { getVideoMetadataCount } from '../../../games/shared/data/videoLoader.js'
import { generateChartClimberRound } from '../../../games/shared/generators/chartClimber.js'
import { generateGuessPeakRound } from '../../../games/shared/generators/guessPeak.js'
import { generateVideoYearRound } from '../../../games/shared/generators/videoYear.js'
import { generateYearShuffleRound } from '../../../games/shared/generators/yearShuffle.js'

type NetlifyEvent = {
  path?: string
  rawQuery?: string
  httpMethod?: string
  body?: string | null
  isBase64Encoded?: boolean
}

type HandlerResponse = {
  statusCode: number
  headers: Record<string, string>
  body: string
}

type BillboardCsvRow = {
  chartDate: string
  year: number
  week: number
  position: number
  title: string
  artist: string
  songId: string
  artistKey: string
  weeksOnChart: number | null
  peakPosition: number | null
}

type BillboardMovement = 'new_entry' | 'rising' | 'falling' | 're_entry' | 'steady'

type BillboardWeekEntry = {
  songId: string
  rank: number
  movement: BillboardMovement
  title: string
  artist: string
  lastWeek: number | null
  peakPosition: number | null
  weeksOnChart: number | null
}

type BillboardArtistTimelineEntry = {
  songId: string
  title: string
  rank: number
  lastWeek: number | null
  peakPosition: number | null
  weeksOnChart: number | null
}

type BillboardArtistSongStat = {
  songId: string
  title: string
  bestRank: number
  chartWeeks: number
  weeksAtPeak: number
  firstAppearance: string
  lastAppearance: string
}

type BillboardDataCache = {
  rows: BillboardCsvRow[]
  source: string
  availableYears: number[]
  weeksByYear: Map<number, number[]>
  previousDateByDate: Map<string, string | null>
}

const JSON_HEADERS = {
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'public, max-age=300',
}

const BILLBOARD_SOURCE = 'Billboard Hot 100 CSV'
const BILLBOARD_CHART_NAME = 'Billboard Hot 100'
const CHART_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/

/** Build ordered list of candidate paths for billboard_hot100.csv (Netlify packaged via included_files) */
const getBillboardCsvCandidates = (): string[] => {
  const cwd = process.cwd()
  const candidates: string[] = []

  const envPath = process.env.NETLIFY_BILLBOARD_CSV_PATH?.trim()
  if (envPath) candidates.push(path.resolve(cwd, envPath))

  candidates.push(path.join(cwd, 'data', 'derived', 'culture', 'processed', 'billboard_hot100.csv'))

  const moduleDir =
    typeof __dirname === 'string'
      ? __dirname
      : typeof import.meta !== 'undefined' && typeof import.meta.url === 'string'
        ? path.dirname(fileURLToPath(import.meta.url))
        : cwd
  candidates.push(
    path.join(moduleDir, 'data', 'derived', 'culture', 'processed', 'billboard_hot100.csv')
  )

  const repoRootFromFunction = path.resolve(moduleDir, '..', '..', '..', '..')
  candidates.push(
    path.join(repoRootFromFunction, 'data', 'derived', 'culture', 'processed', 'billboard_hot100.csv')
  )

  return [...new Set(candidates)]
}

let cachePromise: Promise<BillboardDataCache> | null = null

const json = (statusCode: number, payload: unknown): HandlerResponse => ({
  statusCode,
  headers: JSON_HEADERS,
  body: JSON.stringify(payload),
})

const parseCountParam = (url: URL) => Math.min(20, Math.max(1, Number.parseInt(url.searchParams.get('count') || '1', 10) || 1))
const parseGuessPeakCountParam = (url: URL) => Math.min(10, Math.max(1, Number.parseInt(url.searchParams.get('count') || '1', 10) || 1))

const buildRounds = async <T>(count: number, generator: () => Promise<T | null> | T | null) => {
  const rounds: T[] = []
  for (let index = 0; index < count; index += 1) {
    const round = await generator()
    if (round) rounds.push(round)
  }
  return rounds
}

const normalizeText = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

const makeSongId = (artist: string, title: string) => `${normalizeText(artist)}::${normalizeText(title)}`

const toNullablePositiveInt = (value: string): number | null => {
  const parsed = Number.parseInt(value, 10)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null
}

const toMovement = (rank: number, lastWeek: number | null, weeksOnChart: number | null): BillboardMovement => {
  if (lastWeek === null) return weeksOnChart !== null && weeksOnChart > 1 ? 're_entry' : 'new_entry'
  if (rank < lastWeek) return 'rising'
  if (rank > lastWeek) return 'falling'
  return 'steady'
}

const parseCsv = (input: string): string[][] => {
  const rows: string[][] = []
  let row: string[] = []
  let field = ''
  let inQuotes = false

  for (let index = 0; index < input.length; index += 1) {
    const char = input[index]

    if (inQuotes) {
      if (char === '"') {
        if (input[index + 1] === '"') {
          field += '"'
          index += 1
        } else {
          inQuotes = false
        }
      } else {
        field += char
      }
      continue
    }

    if (char === '"') {
      inQuotes = true
      continue
    }
    if (char === ',') {
      row.push(field)
      field = ''
      continue
    }
    if (char === '\n') {
      row.push(field)
      rows.push(row)
      row = []
      field = ''
      continue
    }
    if (char !== '\r') {
      field += char
    }
  }

  if (field.length > 0 || row.length > 0) {
    row.push(field)
    rows.push(row)
  }

  return rows
}

const findBillboardCsvPath = async (): Promise<string> => {
  const candidates = getBillboardCsvCandidates()
  for (const candidate of candidates) {
    try {
      await fs.access(candidate)
      if (process.env.NETLIFY_BILLBOARD_DEBUG === '1') {
        console.log('[billboard] CSV resolved to:', candidate)
      }
      return candidate
    } catch {
      continue
    }
  }

  const tried = candidates.join(', ')
  const err = new Error(
    `Billboard CSV not found. Tried: ${tried}. Set NETLIFY_BILLBOARD_CSV_PATH if using a custom path.`
  )
  console.error('[billboard]', err.message)
  throw err
}

const loadBillboardData = async (): Promise<BillboardDataCache> => {
  if (!cachePromise) {
    cachePromise = (async () => {
      const dataPath = await findBillboardCsvPath()
      const raw = await fs.readFile(dataPath, 'utf8')
      const records = parseCsv(raw)
      const [headerRow, ...bodyRows] = records

      if (!headerRow) {
        throw new Error('Billboard CSV was empty')
      }

      const headerIndex = new Map(headerRow.map((value, index) => [value.trim(), index]))
      const dateIndex = headerIndex.get('chart_date')
      const rankIndex = headerIndex.get('rank')
      const titleIndex = headerIndex.get('title')
      const artistIndex = headerIndex.get('artist')
      const weeksIndex = headerIndex.get('weeks_on_chart')
      const peakIndex = headerIndex.get('peak_position')

      if (
        dateIndex === undefined ||
        rankIndex === undefined ||
        titleIndex === undefined ||
        artistIndex === undefined ||
        weeksIndex === undefined ||
        peakIndex === undefined
      ) {
        throw new Error('Billboard CSV was missing one or more required columns')
      }

      const rowsWithoutWeek: Array<Omit<BillboardCsvRow, 'week'>> = []
      const datesByYear = new Map<number, Set<string>>()
      const allDates = new Set<string>()

      for (const record of bodyRows) {
        const chartDate = (record[dateIndex] || '').trim()
        const title = (record[titleIndex] || '').trim()
        const artist = (record[artistIndex] || '').trim()
        const position = toNullablePositiveInt(record[rankIndex] || '')

        if (!CHART_DATE_PATTERN.test(chartDate) || !title || !artist || position === null || position > 100) {
          continue
        }

        const year = Number.parseInt(chartDate.slice(0, 4), 10)
        if (!Number.isInteger(year)) continue

        if (!datesByYear.has(year)) datesByYear.set(year, new Set<string>())
        datesByYear.get(year)!.add(chartDate)
        allDates.add(chartDate)

        rowsWithoutWeek.push({
          chartDate,
          year,
          position,
          title,
          artist,
          songId: makeSongId(artist, title),
          artistKey: normalizeText(artist),
          weeksOnChart: toNullablePositiveInt(record[weeksIndex] || ''),
          peakPosition: toNullablePositiveInt(record[peakIndex] || ''),
        })
      }

      const weekLookup = new Map<string, number>()
      const weeksByYear = new Map<number, number[]>()
      const availableYears = Array.from(datesByYear.keys()).sort((left, right) => right - left)

      for (const year of availableYears) {
        const dates = Array.from(datesByYear.get(year) ?? []).sort()
        const yearWeeks: number[] = []

        dates.forEach((date, index) => {
          const week = index + 1
          weekLookup.set(`${year}:${date}`, week)
          yearWeeks.push(week)
        })

        weeksByYear.set(year, yearWeeks.reverse())
      }

      const rows = rowsWithoutWeek
        .map((row) => ({
          ...row,
          week: weekLookup.get(`${row.year}:${row.chartDate}`) ?? 1,
        }))
        .sort((left, right) => right.chartDate.localeCompare(left.chartDate) || left.position - right.position)

      const sortedDatesAsc = Array.from(allDates).sort()
      const previousDateByDate = new Map<string, string | null>()
      sortedDatesAsc.forEach((date, index) => {
        previousDateByDate.set(date, index === 0 ? null : sortedDatesAsc[index - 1]!)
      })

      return {
        rows,
        source: `${BILLBOARD_SOURCE} (${path.basename(dataPath)})`,
        availableYears,
        weeksByYear,
        previousDateByDate,
      }
    })()
  }

  return cachePromise
}

const buildYearStats = (rows: BillboardCsvRow[], source: string, year: number) => {
  const bySong = new Map<
    string,
    {
      songId: string
      title: string
      artist: string
      bestRank: number
      chartWeeks: number
      rankCounts: Map<number, number>
    }
  >()

  for (const row of rows) {
    const current =
      bySong.get(row.songId) ??
      {
        songId: row.songId,
        title: row.title,
        artist: row.artist,
        bestRank: row.position,
        chartWeeks: 0,
        rankCounts: new Map<number, number>(),
      }

    current.chartWeeks += 1
    current.bestRank = Math.min(current.bestRank, row.position)
    current.rankCounts.set(row.position, (current.rankCounts.get(row.position) ?? 0) + 1)
    bySong.set(row.songId, current)
  }

  const stats = Array.from(bySong.values()).map((entry) => ({
    songId: entry.songId,
    title: entry.title,
    artist: entry.artist,
    bestRank: entry.bestRank,
    chartWeeks: entry.chartWeeks,
    weeksAtPeak: entry.rankCounts.get(entry.bestRank) ?? 0,
  }))

  const byPeakWeeks = (left: typeof stats[number], right: typeof stats[number]) =>
    right.weeksAtPeak - left.weeksAtPeak ||
    left.bestRank - right.bestRank ||
    right.chartWeeks - left.chartWeeks ||
    left.artist.localeCompare(right.artist) ||
    left.title.localeCompare(right.title)

  const byChartRun = (left: typeof stats[number], right: typeof stats[number]) =>
    right.chartWeeks - left.chartWeeks ||
    left.bestRank - right.bestRank ||
    right.weeksAtPeak - left.weeksAtPeak ||
    left.artist.localeCompare(right.artist) ||
    left.title.localeCompare(right.title)

  const artistTotals = new Map<
    string,
    {
      artist: string
      songIds: Set<string>
      bestRank: number
      totalWeeksAtPeak: number
      totalChartWeeks: number
    }
  >()

  for (const song of stats) {
    const current =
      artistTotals.get(song.artist) ??
      {
        artist: song.artist,
        songIds: new Set<string>(),
        bestRank: song.bestRank,
        totalWeeksAtPeak: 0,
        totalChartWeeks: 0,
      }

    current.songIds.add(song.songId)
    current.bestRank = Math.min(current.bestRank, song.bestRank)
    current.totalWeeksAtPeak += song.weeksAtPeak
    current.totalChartWeeks += song.chartWeeks
    artistTotals.set(song.artist, current)
  }

  const topArtists = Array.from(artistTotals.values())
    .map((entry) => ({
      artist: entry.artist,
      songCount: entry.songIds.size,
      bestRank: entry.bestRank,
      totalWeeksAtPeak: entry.totalWeeksAtPeak,
      totalChartWeeks: entry.totalChartWeeks,
    }))
    .sort(
      (left, right) =>
        right.songCount - left.songCount ||
        left.bestRank - right.bestRank ||
        right.totalChartWeeks - left.totalChartWeeks ||
        left.artist.localeCompare(right.artist),
    )
    .slice(0, 12)

  return {
    year,
    totalSongsCharted: stats.length,
    top10Songs: [...stats].sort(byPeakWeeks).slice(0, 10),
    numberOneSongs: stats.filter((song) => song.bestRank === 1).sort(byPeakWeeks),
    longestChartRuns: [...stats].sort(byChartRun).slice(0, 10),
    topArtists,
    source,
  }
}

const buildArtistStats = (rows: BillboardCsvRow[], source: string, requestedArtist: string) => {
  const bySong = new Map<string, BillboardArtistSongStat & { rankCounts: Map<number, number> }>()
  const weeks = new Map<string, { chartDate: string; bestRank: number; entries: BillboardArtistTimelineEntry[] }>()

  let firstChartAppearance: string | null = null
  let peakPosition: number | null = null

  for (const row of rows) {
    if (firstChartAppearance === null || row.chartDate < firstChartAppearance) firstChartAppearance = row.chartDate
    if (peakPosition === null || row.position < peakPosition) peakPosition = row.position

    const currentSong =
      bySong.get(row.songId) ??
      {
        songId: row.songId,
        title: row.title,
        bestRank: row.position,
        chartWeeks: 0,
        weeksAtPeak: 0,
        firstAppearance: row.chartDate,
        lastAppearance: row.chartDate,
        rankCounts: new Map<number, number>(),
      }

    currentSong.chartWeeks += 1
    currentSong.bestRank = Math.min(currentSong.bestRank, row.position)
    if (row.chartDate < currentSong.firstAppearance) currentSong.firstAppearance = row.chartDate
    if (row.chartDate > currentSong.lastAppearance) currentSong.lastAppearance = row.chartDate
    currentSong.rankCounts.set(row.position, (currentSong.rankCounts.get(row.position) ?? 0) + 1)
    currentSong.weeksAtPeak = currentSong.rankCounts.get(currentSong.bestRank) ?? 0
    bySong.set(row.songId, currentSong)

    const currentWeek =
      weeks.get(row.chartDate) ??
      {
        chartDate: row.chartDate,
        bestRank: row.position,
        entries: [],
      }

    currentWeek.bestRank = Math.min(currentWeek.bestRank, row.position)
    currentWeek.entries.push({
      songId: row.songId,
      title: row.title,
      rank: row.position,
      lastWeek: null,
      peakPosition: row.peakPosition,
      weeksOnChart: row.weeksOnChart,
    })
    weeks.set(row.chartDate, currentWeek)
  }

  if (firstChartAppearance === null || peakPosition === null) {
    return null
  }

  return {
    artist: rows[0]?.artist ?? requestedArtist,
    firstChartAppearance,
    totalChartEntries: rows.length,
    totalWeeksOnChart: rows.length,
    distinctWeeksOnChart: weeks.size,
    peakPosition,
    songs: Array.from(bySong.values())
      .map(({ rankCounts: _rankCounts, ...song }) => song)
      .sort(
        (left, right) =>
          left.bestRank - right.bestRank ||
          right.chartWeeks - left.chartWeeks ||
          left.title.localeCompare(right.title),
      ),
    timeline: Array.from(weeks.values())
      .map((week) => ({
        ...week,
        entries: [...week.entries].sort((left, right) => left.rank - right.rank || left.title.localeCompare(right.title)),
      }))
      .sort((left, right) => left.chartDate.localeCompare(right.chartDate)),
    source,
  }
}

const buildSearchResults = (rows: BillboardCsvRow[], query: string) => {
  const queryKey = normalizeText(query)
  if (!queryKey) return []

  const bySong = new Map<
    string,
    {
      chart_song_id: string
      artist: string
      title: string
      first_chart_year: number
      last_chart_year: number
      peak_position: number
      chart_appearances: number
    }
  >()

  for (const row of rows) {
    const current =
      bySong.get(row.songId) ??
      {
        chart_song_id: row.songId,
        artist: row.artist,
        title: row.title,
        first_chart_year: row.year,
        last_chart_year: row.year,
        peak_position: row.position,
        chart_appearances: 0,
      }

    current.first_chart_year = Math.min(current.first_chart_year, row.year)
    current.last_chart_year = Math.max(current.last_chart_year, row.year)
    current.peak_position = Math.min(current.peak_position, row.position)
    current.chart_appearances += 1
    bySong.set(row.songId, current)
  }

  return Array.from(bySong.values())
    .filter((song) => normalizeText(`${song.artist} ${song.title}`).includes(queryKey))
    .sort(
      (left, right) =>
        left.peak_position - right.peak_position ||
        right.chart_appearances - left.chart_appearances ||
        left.artist.localeCompare(right.artist) ||
        left.title.localeCompare(right.title),
    )
}

const normalizeFunctionPath = (value: string) => {
  const functionPrefix = '/.netlify/functions/billboard'
  if (value.startsWith('/api/')) return value
  if (value === '/api') return value
  if (value.startsWith(functionPrefix)) {
    const suffix = value.slice(functionPrefix.length)
    return `/api${suffix || '/health'}`
  }
  return value
}

const routeRequest = async (method: string, urlValue: string): Promise<HandlerResponse> => {
  if (method === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        ...JSON_HEADERS,
        Allow: 'GET, OPTIONS',
      },
      body: '',
    }
  }

  if (method !== 'GET') {
    return json(405, { error: 'Method not allowed' })
  }

  const url = new URL(urlValue, 'https://retroverse.live')
  const pathname = normalizeFunctionPath(url.pathname)

  if (pathname === '/api/health' || pathname === '/health') {
    return json(200, { ok: true, source: BILLBOARD_SOURCE })
  }

  if (pathname === '/api/debug/games-data') {
    try {
      const [playableSongs, hitSongs, yearIdentifiers, chartClimbers, videoPuzzles] = await Promise.all([
        getPlayableSongs(),
        getHitSongs(),
        getYearIdentifiers(),
        getChartClimbers(),
        getVideoPuzzles(),
      ])

      return json(200, {
        songs_loaded: getBillboardSongCount(),
        videos_loaded: getVideoMetadataCount(),
        playable_songs: playableSongs.length,
        hit_songs: hitSongs.length,
        year_identifiers: yearIdentifiers.length,
        chart_climbers: chartClimbers.length,
        video_puzzles: videoPuzzles.length,
      })
    } catch (error) {
      return json(503, {
        error: (error as Error).message,
        songs_loaded: 0,
        videos_loaded: 0,
        playable_songs: 0,
        hit_songs: 0,
        year_identifiers: 0,
        chart_climbers: 0,
        video_puzzles: 0,
      })
    }
  }

  if (pathname === '/api/chart-climber') {
    const count = parseCountParam(url)
    const rounds = await buildRounds(count, generateChartClimberRound)
    if (rounds.length === 0) {
      return json(503, { error: 'No chart rounds available', rounds: [] })
    }
    return json(200, { rounds, count: rounds.length })
  }

  if (pathname === '/api/year-shuffle') {
    const count = parseCountParam(url)
    const rounds = await buildRounds(count, generateYearShuffleRound)
    if (rounds.length === 0) {
      return json(503, { error: 'No year shuffle rounds available', rounds: [] })
    }
    return json(200, { rounds, count: rounds.length })
  }

  if (pathname === '/api/video-year') {
    const count = parseCountParam(url)
    const rounds = await buildRounds(count, generateVideoYearRound)
    if (rounds.length === 0) {
      return json(503, { error: 'No video-year rounds available', rounds: [] })
    }
    return json(200, { rounds, count: rounds.length })
  }

  if (pathname === '/api/guess-peak') {
    const count = parseGuessPeakCountParam(url)
    const rounds = await buildRounds(count, generateGuessPeakRound)
    if (rounds.length === 0) {
      return json(503, { error: 'No guess-peak rounds available', rounds: [] })
    }
    return json(200, { rounds })
  }

  const data = await loadBillboardData()

  if (pathname === '/api/charts/billboard/rows') {
    const yearParam = (url.searchParams.get('year') || '').trim()
    const weekParam = (url.searchParams.get('week') || '').trim()
    const limitParam = (url.searchParams.get('limit') || '').trim()
    const offsetParam = (url.searchParams.get('offset') || '').trim()

    const year = yearParam ? Number.parseInt(yearParam, 10) : null
    const week = weekParam ? Number.parseInt(weekParam, 10) : null
    const limit = limitParam ? Number.parseInt(limitParam, 10) : 250
    const offset = offsetParam ? Number.parseInt(offsetParam, 10) : 0

    if (yearParam && !Number.isInteger(year)) return json(400, { error: 'Invalid year parameter' })
    if (weekParam && !Number.isInteger(week)) return json(400, { error: 'Invalid week parameter' })
    if (week !== null && year === null) return json(400, { error: 'Week filter requires a year filter' })
    if (!Number.isInteger(limit) || limit < 1 || limit > 2000) return json(400, { error: 'Invalid limit parameter (1-2000)' })
    if (!Number.isInteger(offset) || offset < 0) return json(400, { error: 'Invalid offset parameter' })

    const filtered = data.rows.filter((row) => {
      if (year !== null && row.year !== year) return false
      if (week !== null && row.week !== week) return false
      return true
    })

    const entries = filtered.slice(offset, offset + limit).map((row) => ({
      chartDate: row.chartDate,
      year: row.year,
      week: row.week,
      position: row.position,
      title: row.title,
      artist: row.artist,
    }))

    return json(200, {
      entries,
      totalRows: filtered.length,
      limit,
      offset,
      filters: { year, week },
      availableYears: data.availableYears,
      availableWeeks: year !== null ? data.weeksByYear.get(year) ?? [] : [],
      source: data.source,
    })
  }

  const yearMatch = pathname.match(/^\/api\/charts\/billboard\/year\/(\d{4})$/)
  if (yearMatch) {
    const year = Number.parseInt(yearMatch[1]!, 10)
    const rows = data.rows.filter((row) => row.year === year)
    if (rows.length === 0) return json(404, { error: `No Billboard chart rows found for year ${year}` })
    return json(200, buildYearStats(rows, data.source, year))
  }

  const weekMatch = pathname.match(/^\/api\/charts\/billboard\/week\/([^/]+)$/)
  if (weekMatch) {
    const chartDate = decodeURIComponent(weekMatch[1] ?? '').trim()
    if (!CHART_DATE_PATTERN.test(chartDate)) return json(400, { error: 'Invalid date parameter. Expected YYYY-MM-DD' })

    const rows = data.rows
      .filter((row) => row.chartDate === chartDate)
      .sort((left, right) => left.position - right.position || left.title.localeCompare(right.title))

    if (rows.length === 0) return json(404, { error: `No Billboard chart rows found for week ${chartDate}` })

    const previousDate = data.previousDateByDate.get(chartDate) ?? null
    const previousWeekLookup = new Map<string, number>()
    if (previousDate) {
      data.rows
        .filter((row) => row.chartDate === previousDate)
        .forEach((row) => previousWeekLookup.set(row.songId, row.position))
    }

    const entries: BillboardWeekEntry[] = rows.map((row) => {
      const lastWeek = previousWeekLookup.get(row.songId) ?? null
      return {
        songId: row.songId,
        rank: row.position,
        movement: toMovement(row.position, lastWeek, row.weeksOnChart),
        title: row.title,
        artist: row.artist,
        lastWeek,
        peakPosition: row.peakPosition,
        weeksOnChart: row.weeksOnChart,
      }
    })

    return json(200, {
      chartDate,
      chartName: BILLBOARD_CHART_NAME,
      totalEntries: entries.length,
      entries,
      source: data.source,
    })
  }

  const artistMatch = pathname.match(/^\/api\/charts\/billboard\/artist\/([^/]+)$/)
  if (artistMatch) {
    const artistName = decodeURIComponent(artistMatch[1] ?? '').trim()
    if (!artistName) return json(400, { error: 'Invalid artist parameter' })

    const artistKey = normalizeText(artistName)
    const rows = data.rows.filter((row) => row.artistKey === artistKey)
    const payload = buildArtistStats(rows, data.source, artistName)
    if (!payload) return json(404, { error: `No Billboard chart rows found for artist ${artistName}` })
    return json(200, payload)
  }

  if (pathname === '/api/search/billboard') {
    const query = (url.searchParams.get('query') || '').trim()
    const limit = Math.min(Number.parseInt(url.searchParams.get('limit') || '20', 10) || 20, 100)
    if (!query) return json(400, { error: 'Query required' })

    const results = buildSearchResults(data.rows, query).slice(0, limit)
    return json(200, {
      query,
      limit,
      count: results.length,
      results,
      source: data.source,
    })
  }

  return json(404, { error: 'Not found' })
}

export const handler = async (event: NetlifyEvent): Promise<HandlerResponse> => {
  const method = (event.httpMethod || 'GET').toUpperCase()
  const pathname = event.path || '/api/health'
  const rawQuery = event.rawQuery ? `?${event.rawQuery}` : ''
  return routeRequest(method, `${pathname}${rawQuery}`)
}
