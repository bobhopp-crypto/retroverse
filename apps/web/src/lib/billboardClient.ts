import { PIPELINE_API_BASE } from './pipelineApi'

export type BillboardYearSongStat = {
  songId: string
  title: string
  artist: string
  bestRank: number
  chartWeeks: number
  weeksAtPeak: number
}

export type BillboardYearArtistStat = {
  artist: string
  songCount: number
  bestRank: number
  totalWeeksAtPeak: number
  totalChartWeeks: number
}

export type BillboardYearStats = {
  year: number
  totalSongsCharted: number
  top10Songs: BillboardYearSongStat[]
  numberOneSongs: BillboardYearSongStat[]
  longestChartRuns: BillboardYearSongStat[]
  topArtists?: BillboardYearArtistStat[]
  source: string
}

type BillboardError = {
  error?: string
}

export type BillboardChartRow = {
  chartDate: string
  year: number
  week: number
  position: number
  title: string
  artist: string
}

export type BillboardRowsPayload = {
  entries: BillboardChartRow[]
  totalRows: number
  limit: number
  offset: number
  filters: {
    year: number | null
    week: number | null
  }
  availableYears: number[]
  availableWeeks: number[]
  source: string
}

export const fetchBillboardYearStats = async (year: number): Promise<BillboardYearStats> => {
  const response = await fetch(`${PIPELINE_API_BASE}/charts/billboard/year/${year}`)
  const payload = (await response.json().catch(() => ({}))) as BillboardYearStats | BillboardError

  if (!response.ok) {
    const maybeError = (payload as BillboardError).error
    const message = typeof maybeError === 'string' ? maybeError : `Failed to load year stats (${response.status})`
    throw new Error(message)
  }

  return payload as BillboardYearStats
}

type FetchBillboardRowsOptions = {
  year?: number | null
  week?: number | null
  limit?: number
  offset?: number
}

export const fetchBillboardRows = async (options: FetchBillboardRowsOptions = {}): Promise<BillboardRowsPayload> => {
  const query = new URLSearchParams()

  if (typeof options.year === 'number') {
    query.set('year', String(options.year))
  }
  if (typeof options.week === 'number') {
    query.set('week', String(options.week))
  }
  if (typeof options.limit === 'number') {
    query.set('limit', String(options.limit))
  }
  if (typeof options.offset === 'number') {
    query.set('offset', String(options.offset))
  }

  const url = `${PIPELINE_API_BASE}/charts/billboard/rows${query.toString() ? `?${query.toString()}` : ''}`
  const response = await fetch(url)
  const payload = (await response.json().catch(() => ({}))) as BillboardRowsPayload | BillboardError

  if (!response.ok) {
    const maybeError = (payload as BillboardError).error
    const message = typeof maybeError === 'string' ? maybeError : `Failed to load chart rows (${response.status})`
    throw new Error(message)
  }

  return payload as BillboardRowsPayload
}
