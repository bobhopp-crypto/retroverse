import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchBillboardRows, type BillboardRowsPayload } from '../lib/billboardClient'

const PAGE_SIZE = 200

const getArtistPath = (artist: string) => `/artist/${encodeURIComponent(artist)}`

const toWeekLabel = (week: number) => `W${String(week).padStart(2, '0')}`

export default function ChartsPage() {
  const [year, setYear] = useState<number | null>(null)
  const [week, setWeek] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [payload, setPayload] = useState<BillboardRowsPayload | null>(null)

  useEffect(() => {
    if (year !== null) return

    let cancelled = false
    setLoading(true)
    setError(null)

    fetchBillboardRows({ limit: 1, offset: 0 })
      .then((data) => {
        if (cancelled) return
        setPayload(data)

        const nextYear = data.availableYears[0] ?? null
        if (nextYear === null) {
          setLoading(false)
          return
        }
        setYear(nextYear)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Unable to load chart filters.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [year])

  useEffect(() => {
    if (year === null) return

    let cancelled = false
    setLoading(true)
    setError(null)

    fetchBillboardRows({
      year,
      week,
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    })
      .then((data) => {
        if (cancelled) return
        setPayload(data)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Unable to load chart rows.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [page, week, year])

  const entries = payload?.entries ?? []
  const availableYears = payload?.availableYears ?? []
  const availableWeeks = payload?.availableWeeks ?? []

  const totalPages = useMemo(() => {
    if (!payload) return 1
    return Math.max(1, Math.ceil(payload.totalRows / payload.limit))
  }, [payload])

  const fromRow = payload ? payload.offset + 1 : 0
  const toRow = payload ? payload.offset + entries.length : 0
  const canPrev = page > 1
  const canNext = payload ? payload.offset + payload.limit < payload.totalRows : false

  return (
    <section className="stack">
      <div className="page-heading">
        <h1 className="page-title">Charts</h1>
      </div>

      <article className="section">
        <h2 className="section-title section-badge-chart">Chart Browser</h2>
        <p className="muted">Rows from Billboard SQLite. Fields: year, week, position, artist, title.</p>

        <div className="mt-3 flex flex-wrap items-end gap-2">
          <label className="inline-flex min-w-[140px] flex-col gap-1 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">
            Year
            <select
              value={year ?? ''}
              onChange={(event) => {
                const nextYear = Number(event.target.value)
                setYear(Number.isInteger(nextYear) ? nextYear : null)
                setWeek(null)
                setPage(1)
              }}
              className="rounded-lg border border-[var(--rv2)] bg-[var(--rv3)] px-3 py-2 text-sm normal-case tracking-normal text-[var(--rv1)] outline-none focus:border-[var(--rv5)]"
              disabled={availableYears.length === 0}
            >
              {availableYears.length === 0 ? <option value="">No years</option> : null}
              {availableYears.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>

          <label className="inline-flex min-w-[140px] flex-col gap-1 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">
            Week
            <select
              value={week ?? ''}
              onChange={(event) => {
                const nextWeek = Number(event.target.value)
                setWeek(Number.isInteger(nextWeek) && nextWeek > 0 ? nextWeek : null)
                setPage(1)
              }}
              className="rounded-lg border border-[var(--rv2)] bg-[var(--rv3)] px-3 py-2 text-sm normal-case tracking-normal text-[var(--rv1)] outline-none focus:border-[var(--rv5)]"
              disabled={year === null}
            >
              <option value="">All weeks</option>
              {availableWeeks.map((value) => (
                <option key={value} value={value}>
                  {toWeekLabel(value)}
                </option>
              ))}
            </select>
          </label>

          <button
            type="button"
            onClick={() => {
              setWeek(null)
              setPage(1)
            }}
            className="rounded-lg border border-[var(--rv2)] bg-[var(--rv4)] px-3 py-2 text-sm font-semibold text-[var(--rv1)]"
          >
            Reset Week
          </button>
        </div>
      </article>

      <article className="section">
        <h2 className="section-title section-badge-chart">Rows</h2>
        {loading ? <p className="muted">Loading chart rows...</p> : null}
        {!loading && error ? <p className="muted">{error}</p> : null}
        {!loading && !error && payload ? (
          <p className="muted">
            Showing {fromRow}-{toRow} of {payload.totalRows.toLocaleString()} rows.
          </p>
        ) : null}

        {!loading && !error && entries.length === 0 ? <div className="placeholder-box">No rows found for the selected filters.</div> : null}

        {!loading && !error && entries.length > 0 ? (
          <>
            <div className="mt-3 space-y-2 md:hidden">
              {entries.map((entry) => (
                <article key={`${entry.chartDate}-${entry.position}-${entry.title}`} className="rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] p-3">
                  <p className="m-0 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">
                    {entry.year} • {toWeekLabel(entry.week)} • #{entry.position}
                  </p>
                  <p className="m-0 mt-1 text-base font-bold text-[var(--rv1)]">{entry.title}</p>
                  <p className="m-0 mt-1 text-sm text-[var(--rv1)]">
                    <Link className="link-plain" to={getArtistPath(entry.artist)}>
                      {entry.artist}
                    </Link>
                  </p>
                </article>
              ))}
            </div>

            <div className="mt-3 hidden overflow-hidden rounded-xl border border-[var(--rv2)] md:block">
              <table className="simple-table">
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Week</th>
                    <th>Position</th>
                    <th>Artist</th>
                    <th>Title</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => (
                    <tr key={`${entry.chartDate}-${entry.position}-${entry.title}`}>
                      <td>{entry.year}</td>
                      <td>{toWeekLabel(entry.week)}</td>
                      <td>{entry.position}</td>
                      <td>
                        <Link className="link-plain" to={getArtistPath(entry.artist)}>
                          {entry.artist}
                        </Link>
                      </td>
                      <td>{entry.title}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : null}

        {!loading && !error && payload ? (
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={!canPrev}
              className="rounded-lg border border-[var(--rv2)] bg-[var(--rv3)] px-3 py-2 text-sm font-semibold text-[var(--rv1)] disabled:cursor-not-allowed disabled:opacity-55"
            >
              Previous
            </button>
            <p className="m-0 text-sm font-semibold text-[var(--rv1)]">
              Page {page} of {totalPages}
            </p>
            <button
              type="button"
              onClick={() => setPage((current) => current + 1)}
              disabled={!canNext}
              className="rounded-lg border border-[var(--rv2)] bg-[var(--rv5)] px-3 py-2 text-sm font-semibold text-[var(--rv3)] disabled:cursor-not-allowed disabled:opacity-55"
            >
              Next
            </button>
          </div>
        ) : null}
      </article>

      {payload ? (
        <article className="section">
          <h2 className="section-title section-badge-chart">Source</h2>
          <p className="muted">{payload.source}</p>
        </article>
      ) : null}
    </section>
  )
}
