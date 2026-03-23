import { useCallback, useEffect, useMemo, useState } from 'react'
import { dataUrl, VIDEO_INDEX_URL } from '../config/dataSources'
import { MEDIA_BASE } from '../config/media'
import { normalizeArtist, normalizeTitle } from '../lib/normalize'
import './AlbumChartPanel.css'

type AlbumChartRecord = {
  artist: string
  album: string
  peak: number
  weeks: number
}

type SongChartRecord = {
  title: string
  artist: string
  peak: number | null
}

type VideoMatchRecord = {
  playUrl: string | null
  pageUrl: string
}

const toFiniteNumber = (value: unknown): number | null => {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const toStringValue = (value: unknown): string => (typeof value === 'string' ? value.trim() : '')

const getAlbumKey = (entry: AlbumChartRecord): string => `${entry.artist}::${entry.album}::${entry.peak}::${entry.weeks}`

const makeSongLookupKey = (artist: string, title: string): string =>
  `${normalizeArtist(artist)}::${normalizeTitle(title)}`

const buildVideoUrlFromPath = (rawPath: string): string | null => {
  const marker = '/VIDEO/'
  const markerIndex = rawPath.indexOf(marker)
  if (markerIndex === -1) return null

  const relativePath = rawPath.slice(markerIndex + marker.length)
  if (!relativePath) return null

  const encoded = `video/${relativePath}`
    .split('/')
    .map((segment) => encodeURIComponent(segment))
    .join('/')

  return `${MEDIA_BASE}/${encoded}`
}

const parseAlbumChartRecord = (value: unknown): AlbumChartRecord | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const artist = toStringValue(row.artist)
  const album = toStringValue(row.album)
  const peak = toFiniteNumber(row.peak)
  const weeks = toFiniteNumber(row.weeks)

  if (!artist || !album || peak === null || weeks === null) return null

  return {
    artist,
    album,
    peak,
    weeks,
  }
}

const parseSongChartRecord = (value: unknown): SongChartRecord | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const title = toStringValue(row.title ?? row.song ?? row.track)
  const artist = toStringValue(row.artist)
  const peak = toFiniteNumber(row.peak ?? row.bestRank ?? row.best_rank ?? row.position)

  if (!title || !artist) return null

  return {
    title,
    artist,
    peak,
  }
}

type AlbumChartPanelProps = {
  year: number
}

export default function AlbumChartPanel({ year }: AlbumChartPanelProps) {
  const [rows, setRows] = useState<AlbumChartRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedAlbumKey, setExpandedAlbumKey] = useState<string | null>(null)
  const [songRows, setSongRows] = useState<SongChartRecord[] | null>(null)
  const [songsLoading, setSongsLoading] = useState(false)
  const [songsError, setSongsError] = useState<string | null>(null)
  const [videoLookup, setVideoLookup] = useState<Map<string, VideoMatchRecord>>(new Map())
  const [videoIndexLoading, setVideoIndexLoading] = useState(false)
  const [videoIndexLoaded, setVideoIndexLoaded] = useState(false)
  const [videoIndexError, setVideoIndexError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setExpandedAlbumKey(null)
    setSongRows(null)
    setSongsLoading(false)
    setSongsError(null)

    const url = dataUrl(`albums/${year}.json`)

    fetch(url)
      .then(async (response) => {
        if (response.status === 404) return []
        if (!response.ok) throw new Error(`Failed to load album chart data (${response.status}).`)

        const payload = (await response.json()) as unknown
        if (!Array.isArray(payload)) throw new Error('Album chart payload was not an array.')

        return payload
          .map(parseAlbumChartRecord)
          .filter((entry): entry is AlbumChartRecord => entry !== null)
      })
      .then((entries) => {
        if (cancelled) return
        setRows(entries)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setRows([])
        setError(err instanceof Error ? err.message : 'Unable to load album chart data.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [year])

  const topAlbums = useMemo(
    () =>
      [...rows]
        .sort((a, b) => a.peak - b.peak || b.weeks - a.weeks || a.album.localeCompare(b.album) || a.artist.localeCompare(b.artist))
        .slice(0, 10),
    [rows],
  )

  const songsByArtist = useMemo(() => {
    if (!songRows) return new Map<string, SongChartRecord[]>()

    const grouped = new Map<string, SongChartRecord[]>()
    for (const row of songRows) {
      const artistKey = normalizeArtist(row.artist)
      const bucket = grouped.get(artistKey)
      if (bucket) bucket.push(row)
      else grouped.set(artistKey, [row])
    }

    for (const bucket of grouped.values()) {
      bucket.sort((a, b) => {
        const leftPeak = a.peak ?? Number.MAX_SAFE_INTEGER
        const rightPeak = b.peak ?? Number.MAX_SAFE_INTEGER
        return leftPeak - rightPeak || a.title.localeCompare(b.title)
      })
    }

    return grouped
  }, [songRows])

  const loadSongsForYear = useCallback(() => {
    if (songRows !== null || songsLoading) return

    const url = dataUrl(`charts/${year}.json`)
    setSongsLoading(true)
    setSongsError(null)

    fetch(url)
      .then(async (response) => {
        if (response.status === 404) {
          throw new Error(`No song chart file found for ${year} at ${dataUrl(`charts/${year}.json`)}.`)
        }
        if (!response.ok) throw new Error(`Failed to load song chart data (${response.status}).`)

        const payload = (await response.json()) as unknown
        const rawRows = Array.isArray(payload)
          ? payload
          : Array.isArray((payload as { entries?: unknown[] } | null | undefined)?.entries)
            ? ((payload as { entries: unknown[] }).entries)
            : Array.isArray((payload as { songs?: unknown[] } | null | undefined)?.songs)
              ? ((payload as { songs: unknown[] }).songs)
              : []

        return rawRows
          .map(parseSongChartRecord)
          .filter((entry): entry is SongChartRecord => entry !== null)
      })
      .then((entries) => {
        setSongRows(entries)
        setSongsLoading(false)
      })
      .catch((err: unknown) => {
        setSongRows(null)
        setSongsError(err instanceof Error ? err.message : 'Unable to load song chart data.')
        setSongsLoading(false)
      })
  }, [songRows, songsLoading, year])

  const loadVideoIndex = useCallback(() => {
    if (videoIndexLoaded || videoIndexLoading) return

    const url = VIDEO_INDEX_URL
    setVideoIndexLoading(true)
    setVideoIndexError(null)

    fetch(url)
      .then(async (response) => {
        if (!response.ok) throw new Error(`Failed to load video index (${response.status}).`)

        const payload = (await response.json()) as unknown
        const rawRows = Array.isArray(payload)
          ? payload
          : Array.isArray((payload as { items?: unknown[] } | null | undefined)?.items)
            ? ((payload as { items: unknown[] }).items)
            : Array.isArray((payload as { videos?: unknown[] } | null | undefined)?.videos)
              ? ((payload as { videos: unknown[] }).videos)
              : []

        const lookup = new Map<string, VideoMatchRecord>()

        for (const rawRow of rawRows) {
          if (!rawRow || typeof rawRow !== 'object') continue
          const row = rawRow as Record<string, unknown>

          const tags = (row.tags && typeof row.tags === 'object' ? (row.tags as Record<string, unknown>) : null)
          const artist = toStringValue(row.artist ?? row.author ?? tags?.author)
          const title = toStringValue(row.title ?? tags?.title)
          if (!artist || !title) continue

          const explicitUrl = toStringValue(row.videoUrl ?? row.video_url)
          const filePath = toStringValue(row.filePath ?? row.filepath ?? row.relative_media_path)
          const playUrl = explicitUrl || buildVideoUrlFromPath(filePath) || null
          const key = makeSongLookupKey(artist, title)
          const existing = lookup.get(key)

          if (!existing || (!existing.playUrl && playUrl)) {
            lookup.set(key, {
              playUrl,
              pageUrl: '/video-library',
            })
          }
        }

        return lookup
      })
      .then((lookup) => {
        setVideoLookup(lookup)
        setVideoIndexLoaded(true)
        setVideoIndexLoading(false)
      })
      .catch((err: unknown) => {
        setVideoLookup(new Map())
        setVideoIndexError(err instanceof Error ? err.message : 'Unable to load video index.')
        setVideoIndexLoading(false)
      })
  }, [videoIndexLoaded, videoIndexLoading])

  const openVideoMatch = useCallback((videoMatch: VideoMatchRecord) => {
    if (videoMatch.playUrl) {
      window.open(videoMatch.playUrl, '_blank', 'noopener,noreferrer')
      return
    }
    window.location.assign(videoMatch.pageUrl)
  }, [])

  const onAlbumClick = useCallback(
    (entry: AlbumChartRecord) => {
      const key = getAlbumKey(entry)
      setExpandedAlbumKey((currentKey) => (currentKey === key ? null : key))
      loadSongsForYear()
      loadVideoIndex()
    },
    [loadSongsForYear, loadVideoIndex],
  )

  return (
    <div className="section">
      <h2 className="section-title section-badge-album">Top Albums of {year}</h2>
      {loading ? <p>Loading album chart data...</p> : null}
      {error ? <p className="muted">{error}</p> : null}
      {!loading && !error && topAlbums.length === 0 ? <div className="placeholder-box">No album chart data available for {year}.</div> : null}
      {!loading && !error && topAlbums.length > 0 ? (
        <ol className="album-chart-list">
          {topAlbums.map((entry, index) => {
            const albumKey = getAlbumKey(entry)
            const artistMatches = songsByArtist.get(normalizeArtist(entry.artist)) ?? []
            const isExpanded = expandedAlbumKey === albumKey

            return (
              <li key={`${albumKey}-${index}`} className="album-chart-entry">
                <button
                  type="button"
                  className={`album-chart-item album-chart-trigger${isExpanded ? ' is-expanded' : ''}`}
                  onClick={() => onAlbumClick(entry)}
                  aria-expanded={isExpanded}
                  aria-controls={`album-song-panel-${year}-${index}`}
                >
                  <span className="album-chart-rank-badge">#{index + 1}</span>
                  <div className="album-chart-copy">
                    <p className="album-chart-title">
                      {entry.album}
                      <span className="album-chart-separator"> — </span>
                      <span className="album-chart-artist">{entry.artist}</span>
                    </p>
                    <p className="album-chart-meta">Peak #{entry.peak} • Weeks {entry.weeks}</p>
                  </div>
                  <span className="album-chart-toggle">{isExpanded ? 'Hide' : 'Show'}</span>
                </button>
                <div
                  id={`album-song-panel-${year}-${index}`}
                  className={`album-song-panel${isExpanded ? ' is-open' : ''}`}
                  hidden={!isExpanded}
                >
                  {songsLoading ? <p className="album-song-status">Loading Hot 100 songs...</p> : null}
                  {!songsLoading && songsError ? <p className="album-song-status muted">{songsError}</p> : null}
                  {!songsLoading && !songsError && isExpanded && artistMatches.length > 0 ? (
                    <>
                      <p className="album-song-heading">Hot 100 Songs:</p>
                      <ul className="album-song-list">
                        {artistMatches.map((song, songIndex) => {
                          const videoMatch = videoLookup.get(makeSongLookupKey(song.artist, song.title))
                          return (
                            <li key={`${song.title}-${song.artist}-${song.peak ?? 'na'}-${songIndex}`} className="album-song-item">
                              <span className="album-song-line">{song.title} — Peak #{song.peak ?? '—'}</span>
                              {videoMatch ? (
                                <button type="button" className="album-song-video-button" onClick={() => openVideoMatch(videoMatch)}>
                                  Play Video
                                </button>
                              ) : null}
                            </li>
                          )
                        })}
                      </ul>
                    </>
                  ) : null}
                  {!songsLoading && !songsError && isExpanded && videoIndexLoading ? (
                    <p className="album-song-status muted">Checking video index...</p>
                  ) : null}
                  {!songsLoading && !songsError && isExpanded && videoIndexError ? (
                    <p className="album-song-status muted">{videoIndexError}</p>
                  ) : null}
                  {!songsLoading && !songsError && isExpanded && artistMatches.length === 0 ? (
                    <p className="album-song-status">No Hot 100 songs matched artist {entry.artist} for {year}.</p>
                  ) : null}
                </div>
              </li>
            )
          })}
        </ol>
      ) : null}
    </div>
  )
}
