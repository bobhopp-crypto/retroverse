import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ArtistTimelinePanel from '../components/ArtistTimelinePanel'
import ArtistVideosPanel from '../components/ArtistVideosPanel'
import { normalizeArtist, normalizeTitle } from '../lib/normalize'
import { PIPELINE_API_BASE } from '../lib/pipelineApi'
import { loadVideoIndex, stableVideoHash, type VideoRecord } from '../lib/videoIndex'
import './ArtistPage.css'

type BillboardArtistTimelineEntry = {
  songId: string
  title: string
  rank: number
  lastWeek: number | null
  peakPosition: number | null
  weeksOnChart: number | null
}

type BillboardArtistTimelineWeek = {
  chartDate: string
  bestRank: number
  entries: BillboardArtistTimelineEntry[]
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

type BillboardArtistPayload = {
  artist: string
  firstChartAppearance: string
  totalChartEntries: number
  totalWeeksOnChart: number
  distinctWeeksOnChart: number
  peakPosition: number
  songs: BillboardArtistSongStat[]
  timeline: BillboardArtistTimelineWeek[]
  source: string
}

type BillboardError = {
  error?: string
}

const TIMELINE_WIDTH = 960
const TIMELINE_HEIGHT = 260
const TIMELINE_PADDING = { top: 12, right: 12, bottom: 28, left: 36 }
const TIMELINE_TICKS = [1, 25, 50, 75, 100] as const

const safeDecode = (value: string): string => {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

const matchArtistName = (videoArtist: string, artistName: string): boolean => {
  return normalizeArtist(videoArtist) === normalizeArtist(artistName)
}

const matchSongTitle = (videoTitle: string, songTitleKeys: Set<string>): boolean => {
  if (songTitleKeys.size === 0) return true

  const normalizedVideoTitle = normalizeTitle(videoTitle)
  if (!normalizedVideoTitle) return false
  if (songTitleKeys.has(normalizedVideoTitle)) return true

  for (const key of songTitleKeys) {
    if (normalizedVideoTitle.includes(key) || key.includes(normalizedVideoTitle)) {
      return true
    }
  }

  return false
}

const toYearSortValue = (year: number | null): number => (typeof year === 'number' ? year : -1)

const toDecadeLabel = (year: number): string => `${Math.floor(year / 10) * 10}s`

const fetchBillboardArtist = async (artistName: string): Promise<BillboardArtistPayload> => {
  const response = await fetch(`${PIPELINE_API_BASE}/charts/billboard/artist/${encodeURIComponent(artistName)}`)
  const payload = (await response.json().catch(() => ({}))) as BillboardArtistPayload | BillboardError

  if (!response.ok) {
    const maybeError = (payload as BillboardError).error
    const message = typeof maybeError === 'string' ? maybeError : `Failed to load artist chart stats (${response.status})`
    throw new Error(message)
  }

  return payload as BillboardArtistPayload
}

export default function ArtistPage() {
  const { name: artist } = useParams<{ name: string }>()
  const routeName = artist ? safeDecode(artist).trim() : ''

  const [artistData, setArtistData] = useState<BillboardArtistPayload | null>(null)
  const [artistLoading, setArtistLoading] = useState(false)
  const [artistError, setArtistError] = useState<string | null>(null)

  const [videos, setVideos] = useState<VideoRecord[]>([])
  const [videoLoading, setVideoLoading] = useState(false)
  const [videoError, setVideoError] = useState<string | null>(null)

  useEffect(() => {
    if (!routeName) {
      setArtistData(null)
      setArtistLoading(false)
      setArtistError('Missing artist parameter in route.')
      return
    }

    let cancelled = false
    setArtistLoading(true)
    setArtistError(null)
    setArtistData(null)

    fetchBillboardArtist(routeName)
      .then((data) => {
        if (cancelled) return
        setArtistData(data)
        setArtistLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setArtistData(null)
        setArtistError(err instanceof Error ? err.message : 'Unable to load artist chart data.')
        setArtistLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [routeName])

  const chartDecades = useMemo(() => {
    if (!artistData) return [] as string[]

    const decades = new Set<string>()
    for (const week of artistData.timeline) {
      const year = Number(week.chartDate.slice(0, 4))
      if (Number.isInteger(year)) {
        decades.add(toDecadeLabel(year))
      }
    }

    return [...decades].sort((a, b) => Number(a.slice(0, 4)) - Number(b.slice(0, 4)))
  }, [artistData])

  useEffect(() => {
    if (!artistData || chartDecades.length === 0) {
      setVideos([])
      setVideoLoading(false)
      setVideoError(null)
      return
    }

    let cancelled = false
    setVideoLoading(true)
    setVideoError(null)

    Promise.all(chartDecades.map((decade) => loadVideoIndex(decade)))
      .then((chunks) => {
        if (cancelled) return

        const songTitleKeys = new Set(
          artistData.songs
            .map((song) => normalizeTitle(song.title))
            .filter((value) => value.length > 0),
        )

        const matched = chunks
          .flat()
          .filter((video) => matchArtistName(video.artist, artistData.artist) && matchSongTitle(video.title, songTitleKeys))

        const deduped = new Map<string, VideoRecord>()
        for (const video of matched) {
          const key = stableVideoHash(video)
          if (!deduped.has(key)) deduped.set(key, video)
        }

        const sorted = [...deduped.values()]
          .sort(
            (a, b) =>
              b.playcount - a.playcount ||
              toYearSortValue(b.year) - toYearSortValue(a.year) ||
              a.title.localeCompare(b.title),
          )
          .slice(0, 60)

        setVideos(sorted)
        setVideoLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setVideos([])
        setVideoError(err instanceof Error ? err.message : 'Unable to load matching videos.')
        setVideoLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [artistData, chartDecades])

  const timelinePoints = useMemo(() => {
    if (!artistData || artistData.timeline.length === 0) {
      return [] as Array<{ x: number; y: number; date: string; rank: number }>
    }

    const innerWidth = TIMELINE_WIDTH - TIMELINE_PADDING.left - TIMELINE_PADDING.right
    const innerHeight = TIMELINE_HEIGHT - TIMELINE_PADDING.top - TIMELINE_PADDING.bottom

    return artistData.timeline.map((week, index) => {
      const x =
        artistData.timeline.length === 1
          ? TIMELINE_PADDING.left + innerWidth / 2
          : TIMELINE_PADDING.left + (index / (artistData.timeline.length - 1)) * innerWidth
      const y = TIMELINE_PADDING.top + ((week.bestRank - 1) / 99) * innerHeight

      return {
        x,
        y,
        date: week.chartDate,
        rank: week.bestRank,
      }
    })
  }, [artistData])

  const timelinePath = useMemo(() => timelinePoints.map((point, index) => `${index === 0 ? 'M' : 'L'}${point.x} ${point.y}`).join(' '), [timelinePoints])

  const weeksDescending = useMemo(() => {
    if (!artistData) return [] as BillboardArtistTimelineWeek[]
    return [...artistData.timeline].sort((a, b) => b.chartDate.localeCompare(a.chartDate))
  }, [artistData])

  const displayName = (artistData?.artist ?? routeName) || 'Unknown Artist'

  return (
    <section className="stack artist-page">
      <div className="page-heading">
        <h1 className="page-title">Artist {displayName}</h1>
      </div>

      <article className="section artist-influence-panel-section">
        <h2 className="section-title section-badge-artist">Influence Timeline</h2>
        <ArtistTimelinePanel artistName={displayName} />
      </article>

      <article className="section artist-videos-panel-section">
        <h2 className="section-title section-badge-video">Artist Videos</h2>
        <ArtistVideosPanel artistName={displayName} decadeHints={chartDecades} />
      </article>

      <article className="section">
        <h2 className="section-title section-badge-chart">Artist Snapshot</h2>
        {artistLoading ? <p className="muted">Loading artist stats...</p> : null}
        {!artistLoading && artistError ? <p className="muted">{artistError}</p> : null}
        {artistData ? (
          <>
            <div className="artist-summary-grid">
              <div className="artist-stat-card">
                <p className="artist-stat-label">First chart appearance</p>
                <p className="artist-stat-value">{artistData.firstChartAppearance}</p>
              </div>
              <div className="artist-stat-card">
                <p className="artist-stat-label">Total chart entries</p>
                <p className="artist-stat-value">{artistData.totalChartEntries}</p>
              </div>
              <div className="artist-stat-card">
                <p className="artist-stat-label">Peak position</p>
                <p className="artist-stat-value">#{artistData.peakPosition}</p>
              </div>
              <div className="artist-stat-card">
                <p className="artist-stat-label">Weeks on chart</p>
                <p className="artist-stat-value">{artistData.totalWeeksOnChart}</p>
                <p className="artist-stat-sub">Across {artistData.distinctWeeksOnChart} distinct chart weeks</p>
              </div>
            </div>
            <p className="muted artist-source-note">Source: {artistData.source}</p>
          </>
        ) : null}
      </article>

      {artistData ? (
        <article className="section">
          <h2 className="section-title section-badge-chart">Timeline of Chart Positions</h2>
          {timelinePoints.length > 0 ? (
            <>
              <div className="artist-timeline-wrap">
                <svg className="artist-timeline-svg" viewBox={`0 0 ${TIMELINE_WIDTH} ${TIMELINE_HEIGHT}`} role="img" aria-label={`Chart timeline for ${artistData.artist}`}>
                  {TIMELINE_TICKS.map((tick) => {
                    const y = TIMELINE_PADDING.top + ((tick - 1) / 99) * (TIMELINE_HEIGHT - TIMELINE_PADDING.top - TIMELINE_PADDING.bottom)
                    return (
                      <g key={tick}>
                        <line
                          x1={TIMELINE_PADDING.left}
                          y1={y}
                          x2={TIMELINE_WIDTH - TIMELINE_PADDING.right}
                          y2={y}
                          className="artist-grid-line"
                        />
                        <text x={TIMELINE_PADDING.left - 8} y={y + 4} textAnchor="end" className="artist-grid-label">
                          {tick}
                        </text>
                      </g>
                    )
                  })}
                  {timelinePath ? <path d={timelinePath} className="artist-line-path" /> : null}
                  {timelinePoints.length <= 220
                    ? timelinePoints.map((point) => (
                        <circle key={point.date} cx={point.x} cy={point.y} r={2.5} className="artist-line-point">
                          <title>{`${point.date} · #${point.rank}`}</title>
                        </circle>
                      ))
                    : null}
                </svg>
              </div>
              <p className="muted artist-timeline-note">Weekly best rank for this artist. Lower rank is better, so #1 is at the top.</p>
            </>
          ) : (
            <div className="placeholder-box">No timeline points found.</div>
          )}
        </article>
      ) : null}

      {artistData ? (
        <article className="section">
          <h2 className="section-title section-badge-chart">Chart Entries</h2>
          <div className="artist-table-wrap">
            <table className="simple-table">
              <thead>
                <tr>
                  <th>Song</th>
                  <th>Peak</th>
                  <th>Weeks</th>
                  <th>Weeks At Peak</th>
                  <th>First Week</th>
                  <th>Last Week</th>
                </tr>
              </thead>
              <tbody>
                {artistData.songs.map((song) => (
                  <tr key={song.songId}>
                    <td>{song.title}</td>
                    <td>#{song.bestRank}</td>
                    <td>{song.chartWeeks}</td>
                    <td>{song.weeksAtPeak}</td>
                    <td>
                      <Link className="link-plain" to={`/week/${encodeURIComponent(song.firstAppearance)}`}>
                        {song.firstAppearance}
                      </Link>
                    </td>
                    <td>
                      <Link className="link-plain" to={`/week/${encodeURIComponent(song.lastAppearance)}`}>
                        {song.lastAppearance}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      ) : null}

      {artistData ? (
        <article className="section">
          <h2 className="section-title section-badge-chart">Week Pages Where Songs Appeared</h2>
          <div className="artist-table-wrap artist-week-table-wrap">
            <table className="simple-table">
              <thead>
                <tr>
                  <th>Week</th>
                  <th>Best Rank</th>
                  <th>Songs</th>
                </tr>
              </thead>
              <tbody>
                {weeksDescending.map((week) => (
                  <tr key={week.chartDate}>
                    <td>
                      <Link className="link-plain" to={`/week/${encodeURIComponent(week.chartDate)}`}>
                        {week.chartDate}
                      </Link>
                    </td>
                    <td>#{week.bestRank}</td>
                    <td className="artist-week-songs">
                      {week.entries.slice(0, 4).map((entry) => (
                        <p key={`${week.chartDate}-${entry.songId}-${entry.rank}`} className="artist-week-songline">
                          <strong>#{entry.rank}</strong> {entry.title}
                        </p>
                      ))}
                      {week.entries.length > 4 ? <p className="artist-week-songline muted">+{week.entries.length - 4} more</p> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      ) : null}

      {artistData ? (
        <article className="section">
          <h2 className="section-title section-badge-video">Music Videos From Video Library</h2>
          <p className="muted">Matched by artist name and chart-entry song titles.</p>
          {videoLoading ? <p className="muted">Loading video matches...</p> : null}
          {!videoLoading && videoError ? <p className="muted">{videoError}</p> : null}
          {!videoLoading && !videoError && videos.length === 0 ? <div className="placeholder-box">No video-library matches found for this artist.</div> : null}
          {!videoLoading && !videoError && videos.length > 0 ? (
            <div className="artist-video-grid">
              {videos.map((video) => (
                <article key={stableVideoHash(video)} className="artist-video-card">
                  {video.thumbnailUrl ? <img src={video.thumbnailUrl} alt={`${video.title} by ${video.artist}`} className="artist-video-thumb" loading="lazy" /> : null}
                  <h3 className="artist-video-title">{video.title}</h3>
                  <p className="artist-video-meta">{video.artist}</p>
                  <p className="artist-video-meta">
                    {typeof video.year === 'number' ? video.year : 'Year —'} · Plays {video.playcount}
                  </p>
                  {video.videoUrl ? (
                    <a className="link-plain" href={video.videoUrl} target="_blank" rel="noreferrer">
                      Open Video
                    </a>
                  ) : (
                    <span className="muted">Video URL unavailable</span>
                  )}
                </article>
              ))}
            </div>
          ) : null}
        </article>
      ) : null}
    </section>
  )
}
