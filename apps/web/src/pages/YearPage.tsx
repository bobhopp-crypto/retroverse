import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AlbumChartPanel from '../components/AlbumChartPanel'
import ArtistGravityPanel from '../components/ArtistGravityPanel'
import { fetchBillboardYearStats, type BillboardYearStats } from '../lib/billboardClient'
import { normalizeArtist, normalizeTitle } from '../lib/normalize'
import { loadVideoIndex } from '../lib/videoIndex'

const getArtistPath = (artist: string) => `/artist/${encodeURIComponent(artist)}`

type YearChartSong = {
  artist: string
  title: string
  peak: number
}

type VideoMatch = {
  playUrl: string | null
  pageUrl: string
}

type PlayableYearSong = YearChartSong & VideoMatch

const toStringValue = (value: unknown): string => (typeof value === 'string' ? value.trim() : '')

const toFiniteNumber = (value: unknown): number | null => {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const makeSongLookupKey = (artist: string, title: string): string =>
  `${normalizeArtist(artist)}::${normalizeTitle(title)}`

const parseYearChartSong = (value: unknown): YearChartSong | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const artist = toStringValue(row.artist)
  const title = toStringValue(row.title ?? row.song ?? row.track)
  const peak = toFiniteNumber(row.peak ?? row.bestRank ?? row.best_rank ?? row.position)

  if (!artist || !title || peak === null) return null

  return {
    artist,
    title,
    peak,
  }
}

export default function YearPage() {
  const { year } = useParams<{ year: string }>()
  const [stats, setStats] = useState<BillboardYearStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPlaylist, setShowPlaylist] = useState(false)
  const [playlist, setPlaylist] = useState<PlayableYearSong[]>([])
  const [playlistLoading, setPlaylistLoading] = useState(false)
  const [playlistError, setPlaylistError] = useState<string | null>(null)
  const [playlistYearLoaded, setPlaylistYearLoaded] = useState<number | null>(null)
  const playlistRequestSeq = useRef(0)

  const parsedYear = useMemo(() => {
    const yearNumber = Number(year)
    if (!Number.isInteger(yearNumber)) return null
    return yearNumber
  }, [year])

  useEffect(() => {
    if (parsedYear === null) {
      setStats(null)
      setError('Invalid year parameter in route.')
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    fetchBillboardYearStats(parsedYear)
      .then((data) => {
        if (cancelled) return
        setStats(data)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setStats(null)
        setError(err instanceof Error ? err.message : 'Unable to load chart data.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [parsedYear])

  useEffect(() => {
    playlistRequestSeq.current += 1
    setShowPlaylist(false)
    setPlaylist([])
    setPlaylistLoading(false)
    setPlaylistError(null)
    setPlaylistYearLoaded(null)
  }, [parsedYear])

  const loadPlayableYearPlaylist = useCallback(
    async (targetYear: number) => {
      if (playlistLoading || playlistYearLoaded === targetYear) return

      const requestId = ++playlistRequestSeq.current
      setPlaylistLoading(true)
      setPlaylistError(null)

      try {
        const chartsUrl = `${import.meta.env.BASE_URL}data/charts/${targetYear}.json`
        const decadeLabel = `${Math.floor(targetYear / 10) * 10}s`
        const [chartResponse, videoRows] = await Promise.all([fetch(chartsUrl), loadVideoIndex(decadeLabel)])

        if (!chartResponse.ok) {
          throw new Error(
            chartResponse.status === 404
              ? `No chart summary file found for ${targetYear} at /data/charts/${targetYear}.json.`
              : `Failed to load chart summary (${chartResponse.status}).`,
          )
        }

        const chartPayload = (await chartResponse.json()) as unknown

        const chartRows = (Array.isArray(chartPayload) ? chartPayload : [])
          .map(parseYearChartSong)
          .filter((entry): entry is YearChartSong => entry !== null)

        const videoLookup = new Map<string, VideoMatch>()
        for (const row of videoRows) {
          if (row.year !== targetYear) continue
          const artist = toStringValue(row.artist)
          const title = toStringValue(row.title)
          if (!artist || !title) continue

          const playUrl = row.videoUrl ?? null
          const key = makeSongLookupKey(artist, title)
          const existing = videoLookup.get(key)

          if (!existing || (!existing.playUrl && playUrl)) {
            videoLookup.set(key, {
              playUrl,
              pageUrl: '/video-library',
            })
          }
        }

        const playableRows = chartRows
          .map((song) => {
            const match = videoLookup.get(makeSongLookupKey(song.artist, song.title))
            if (!match) return null
            return {
              ...song,
              ...match,
            }
          })
          .filter((entry): entry is PlayableYearSong => entry !== null)
          .sort((a, b) => a.peak - b.peak || a.title.localeCompare(b.title) || a.artist.localeCompare(b.artist))
          .slice(0, 20)

        if (requestId !== playlistRequestSeq.current) return
        setPlaylist(playableRows)
        setPlaylistYearLoaded(targetYear)
      } catch (err: unknown) {
        if (requestId !== playlistRequestSeq.current) return
        setPlaylist([])
        setPlaylistError(err instanceof Error ? err.message : 'Unable to load playlist data.')
      } finally {
        if (requestId !== playlistRequestSeq.current) return
        setPlaylistLoading(false)
      }
    },
    [playlistLoading, playlistYearLoaded],
  )

  const onTogglePlayYear = useCallback(() => {
    if (parsedYear === null) return

    setShowPlaylist((prev) => !prev)
    if (playlistYearLoaded !== parsedYear) {
      void loadPlayableYearPlaylist(parsedYear)
    }
  }, [loadPlayableYearPlaylist, parsedYear, playlistYearLoaded])

  const onPlayVideo = useCallback((entry: PlayableYearSong) => {
    if (entry.playUrl) {
      window.open(entry.playUrl, '_blank', 'noopener,noreferrer')
      return
    }
    window.location.assign(entry.pageUrl)
  }, [])

  const headingYear = parsedYear !== null ? String(parsedYear) : (year ?? 'Unknown')

  return (
    <section className="stack">
      <div className="page-heading">
        <h1 className="page-title">Year {headingYear}</h1>
        <div className="inline-actions">
          {parsedYear !== null ? (
            <button type="button" className="toggle-btn" onClick={onTogglePlayYear} disabled={playlistLoading}>
              {showPlaylist ? `Hide ${parsedYear} Playlist` : `▶ Play ${parsedYear}`}
            </button>
          ) : null}
        </div>
      </div>

      {showPlaylist && parsedYear !== null ? (
        <div className="section">
          <h2 className="section-title section-badge-chart">Play the Year {parsedYear}</h2>
          {playlistLoading ? <p>Loading playable songs...</p> : null}
          {playlistError ? <p className="muted">{playlistError}</p> : null}
          {!playlistLoading && !playlistError && playlist.length === 0 ? (
            <div className="placeholder-box">No playable video matches found for {parsedYear}.</div>
          ) : null}
          {!playlistLoading && !playlistError && playlist.length > 0 ? (
            <ol className="year-playlist-list">
              {playlist.map((entry, index) => (
                <li key={`${entry.artist}-${entry.title}-${entry.peak}-${index}`} className="year-playlist-item">
                  <p className="year-playlist-title">
                    {index + 1}. {entry.title} — {entry.artist}
                  </p>
                  <p className="year-playlist-meta">Peak #{entry.peak}</p>
                  <button type="button" className="year-playlist-play-btn" onClick={() => onPlayVideo(entry)}>
                    Play Video
                  </button>
                </li>
              ))}
            </ol>
          ) : null}
        </div>
      ) : null}

      <div className="section">
        <h2 className="section-title section-badge-chart">Year Title</h2>
        {loading ? <p>Loading year stats...</p> : null}
        {error ? <p className="muted">{error}</p> : null}
        {stats ? (
          <>
            <p>{stats.year} Annual Summary</p>
            <p>Total songs that charted: <strong>{stats.totalSongsCharted}</strong></p>
            <p className="muted">Computed from year-scoped chart rows only.</p>
          </>
        ) : null}
      </div>

      <div className="section">
        <h2 className="section-title section-badge-chart">Top 10 Songs</h2>
        {stats ? (
          <table className="simple-table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Song</th>
                <th>Artist</th>
                <th>Best Rank</th>
                <th>Weeks At Best Rank</th>
                <th>Weeks Charted</th>
              </tr>
            </thead>
            <tbody>
                {stats.top10Songs.map((song, index) => (
                <tr key={song.songId}>
                  <td>{index + 1}</td>
                  <td>{song.title}</td>
                  <td>
                    <Link className="link-plain" to={getArtistPath(song.artist)}>
                      {song.artist}
                    </Link>
                  </td>
                  <td>{song.bestRank}</td>
                  <td>{song.weeksAtPeak}</td>
                  <td>{song.chartWeeks}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="placeholder-box">No data loaded.</div>
        )}
      </div>

      <div className="section">
        <h2 className="section-title section-badge-chart">Number #1 Songs</h2>
        {stats ? (
          <>
            <p>Total songs that reached #1: <strong>{stats.numberOneSongs.length}</strong></p>
            <table className="simple-table">
              <thead>
                <tr>
                  <th>Song</th>
                  <th>Artist</th>
                  <th>Weeks At #1</th>
                  <th>Weeks Charted</th>
                </tr>
              </thead>
              <tbody>
                {stats.numberOneSongs.map((song) => (
                  <tr key={song.songId}>
                    <td>{song.title}</td>
                    <td>
                      <Link className="link-plain" to={getArtistPath(song.artist)}>
                        {song.artist}
                      </Link>
                    </td>
                    <td>{song.weeksAtPeak}</td>
                    <td>{song.chartWeeks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        ) : (
          <div className="placeholder-box">No data loaded.</div>
        )}
      </div>

      <div className="section">
        <h2 className="section-title section-badge-chart">Songs with Longest Chart Runs</h2>
        {stats ? (
          <table className="simple-table">
            <thead>
              <tr>
                <th>Song</th>
                <th>Artist</th>
                <th>Weeks Charted</th>
                <th>Best Rank</th>
              </tr>
            </thead>
            <tbody>
                {stats.longestChartRuns.map((song) => (
                  <tr key={song.songId}>
                    <td>{song.title}</td>
                    <td>
                      <Link className="link-plain" to={getArtistPath(song.artist)}>
                        {song.artist}
                      </Link>
                    </td>
                    <td>{song.chartWeeks}</td>
                    <td>{song.bestRank}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        ) : (
          <div className="placeholder-box">No data loaded.</div>
        )}
      </div>

      {parsedYear !== null ? <AlbumChartPanel year={parsedYear} /> : null}
      {parsedYear !== null ? <ArtistGravityPanel year={parsedYear} /> : null}
    </section>
  )
}
