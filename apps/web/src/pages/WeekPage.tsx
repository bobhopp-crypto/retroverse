import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { PIPELINE_API_BASE } from '../lib/pipelineApi'
import './WeekPage.css'

type Movement = 'new_entry' | 'rising' | 'falling' | 're_entry' | 'steady'

type BillboardWeekEntry = {
  songId: string
  rank: number
  movement: Movement
  title: string
  artist: string
  lastWeek: number | null
  peakPosition: number | null
  weeksOnChart: number | null
}

type BillboardWeekPayload = {
  chartDate: string
  chartName: string
  totalEntries: number
  entries: BillboardWeekEntry[]
  source: string
}

type BillboardError = {
  error?: string
}

const CHART_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/

const safeDecode = (value: string): string => {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

const getArtistPath = (artist: string) => `/artist/${encodeURIComponent(artist)}`

const fetchBillboardWeek = async (chartDate: string): Promise<BillboardWeekPayload> => {
  const response = await fetch(`${PIPELINE_API_BASE}/charts/billboard/week/${encodeURIComponent(chartDate)}`)
  const payload = (await response.json().catch(() => ({}))) as BillboardWeekPayload | BillboardError

  if (!response.ok) {
    const maybeError = (payload as BillboardError).error
    const message = typeof maybeError === 'string' ? maybeError : `Failed to load week chart (${response.status})`
    throw new Error(message)
  }

  return payload as BillboardWeekPayload
}

const MOVEMENT_META: Record<Movement, { label: string; short: string; className: string }> = {
  new_entry: { label: 'New entry', short: 'NEW', className: 'movement-new' },
  re_entry: { label: 'Re-entry', short: 'RE', className: 'movement-reentry' },
  rising: { label: 'Rising', short: 'UP', className: 'movement-up' },
  falling: { label: 'Falling', short: 'DOWN', className: 'movement-down' },
  steady: { label: 'Steady', short: 'SAME', className: 'movement-steady' },
}

const toDisplayNumber = (value: number | null) => (value === null ? '--' : String(value))

export default function WeekPage() {
  const { date } = useParams<{ date: string }>()
  const routeDate = date ? safeDecode(date).trim() : ''
  const [week, setWeek] = useState<BillboardWeekPayload | null>(null)
  const [weekError, setWeekError] = useState<{ date: string; message: string } | null>(null)

  const isValidDate = CHART_DATE_PATTERN.test(routeDate)
  const routeError = !routeDate ? 'Missing date parameter in route.' : !isValidDate ? 'Invalid date parameter in route. Expected YYYY-MM-DD.' : null
  const weekData = routeError ? null : week?.chartDate === routeDate ? week : null
  const fetchError = weekError?.date === routeDate ? weekError.message : null
  const error = routeError ?? fetchError
  const isLoading = routeError === null && fetchError === null && weekData === null

  useEffect(() => {
    if (!routeDate || !isValidDate) {
      return
    }

    let cancelled = false

    fetchBillboardWeek(routeDate)
      .then((data) => {
        if (cancelled) return
        setWeek(data)
        setWeekError((current) => (current?.date === routeDate ? null : current))
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setWeekError({
          date: routeDate,
          message: err instanceof Error ? err.message : 'Unable to load chart data.',
        })
      })

    return () => {
      cancelled = true
    }
  }, [isValidDate, routeDate])

  const numberOneSong = useMemo(() => weekData?.entries.find((entry) => entry.rank === 1) ?? null, [weekData])
  const top10Songs = useMemo(
    () =>
      weekData
        ? weekData.entries
            .filter((entry) => entry.rank >= 1 && entry.rank <= 10)
            .sort((a, b) => a.rank - b.rank)
        : [],
    [weekData],
  )
  const pageDate = weekData?.chartDate ?? (routeDate || 'YYYY-MM-DD')

  return (
    <section className="stack week-page">
      <div className="page-heading">
        <h1 className="page-title">Week {pageDate}</h1>
      </div>

      <div className="week-summary-grid">
        <article className="section week-summary-card">
          <h2 className="section-title section-badge-chart">Chart Date</h2>
          <p className="week-summary-value">{pageDate}</p>
          {weekData ? <p className="muted week-summary-meta">{weekData.chartName}</p> : null}
        </article>

        <article className="section week-summary-card">
          <h2 className="section-title section-badge-chart">#1 Song</h2>
          {isLoading ? <p className="muted">Loading week chart...</p> : null}
          {!isLoading && error ? <p className="muted">{error}</p> : null}
          {!isLoading && !error && numberOneSong ? (
            <>
              <p className="week-summary-value">{numberOneSong.title}</p>
              <p className="muted week-summary-meta">
                <Link className="link-plain" to={getArtistPath(numberOneSong.artist)}>
                  {numberOneSong.artist}
                </Link>
              </p>
              <div className="week-summary-movement">
                <span className={`movement-pill ${MOVEMENT_META[numberOneSong.movement].className}`}>
                  {MOVEMENT_META[numberOneSong.movement].short}
                </span>
                <span className="muted">{MOVEMENT_META[numberOneSong.movement].label}</span>
              </div>
            </>
          ) : null}
        </article>
      </div>

      <article className="section">
        <h2 className="section-title section-badge-chart">Top 10 Songs</h2>
        {isLoading ? <p className="muted">Loading Top 10...</p> : null}
        {!isLoading && error ? <p className="muted">{error}</p> : null}
        {!isLoading && !error && top10Songs.length === 0 ? <div className="placeholder-box">No chart rows found for this week.</div> : null}
        {!isLoading && !error && top10Songs.length > 0 ? (
          <ol className="week-top10-list">
            {top10Songs.map((entry) => (
              <li key={entry.songId} className="week-top10-item">
                <div className="week-top10-main">
                  <span className="week-rank-badge">#{entry.rank}</span>
                  <span className="week-song">{entry.title}</span>
                  <span className="week-artist">
                    <Link className="link-plain" to={getArtistPath(entry.artist)}>
                      {entry.artist}
                    </Link>
                  </span>
                </div>
                <span className={`movement-pill ${MOVEMENT_META[entry.movement].className}`} title={MOVEMENT_META[entry.movement].label}>
                  {MOVEMENT_META[entry.movement].short}
                </span>
              </li>
            ))}
          </ol>
        ) : null}
      </article>

      <article className="section">
        <h2 className="section-title section-badge-chart">Full Hot 100 Table</h2>
        {isLoading ? <p className="muted">Loading Hot 100 table...</p> : null}
        {!isLoading && !error && weekData ? <p className="muted">Total entries: {weekData.totalEntries}</p> : null}
        {!isLoading && error ? <p className="muted">{error}</p> : null}
        {!isLoading && !error && weekData && weekData.entries.length > 0 ? (
          <div className="week-table-wrap">
            <table className="simple-table week-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Movement</th>
                  <th>Song</th>
                  <th>Artist</th>
                  <th>Last Week</th>
                  <th>Peak</th>
                  <th>Weeks</th>
                </tr>
              </thead>
              <tbody>
                {weekData.entries.map((entry) => (
                  <tr key={`${entry.songId}-${entry.rank}`}>
                    <td>{entry.rank}</td>
                    <td>
                      <span className={`movement-pill ${MOVEMENT_META[entry.movement].className}`} title={MOVEMENT_META[entry.movement].label}>
                        {MOVEMENT_META[entry.movement].short}
                      </span>
                    </td>
                    <td>{entry.title}</td>
                    <td>
                      <Link className="link-plain" to={getArtistPath(entry.artist)}>
                        {entry.artist}
                      </Link>
                    </td>
                    <td>{toDisplayNumber(entry.lastWeek)}</td>
                    <td>{toDisplayNumber(entry.peakPosition)}</td>
                    <td>{toDisplayNumber(entry.weeksOnChart)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </article>
    </section>
  )
}
