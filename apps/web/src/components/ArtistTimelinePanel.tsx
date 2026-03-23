import { useEffect, useMemo, useState } from 'react'
import { dataUrl } from '../config/dataSources'
import { normalizeArtist } from '../lib/normalize'
import './ArtistTimelinePanel.css'

type TimelineYearEntry = {
  year: number
  rank: number
  score: number
}

type TimelineArtistEntry = {
  artist: string
  years: TimelineYearEntry[]
}

type ArtistTimelinePanelProps = {
  artistName: string
}

const toNumber = (value: unknown): number | null => {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const parseTimelineYearEntry = (value: unknown): TimelineYearEntry | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const year = toNumber(row.year)
  const rank = toNumber(row.rank)
  const score = toNumber(row.score)
  if (year === null || rank === null || score === null) return null

  return {
    year,
    rank,
    score,
  }
}

const parseTimelineArtistEntry = (value: unknown): TimelineArtistEntry | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const artist = typeof row.artist === 'string' ? row.artist.trim() : ''
  const yearsPayload = Array.isArray(row.years) ? row.years : []
  if (!artist) return null

  const years = yearsPayload
    .map(parseTimelineYearEntry)
    .filter((entry): entry is TimelineYearEntry => entry !== null)

  return {
    artist,
    years,
  }
}

export default function ArtistTimelinePanel({ artistName }: ArtistTimelinePanelProps) {
  const [entries, setEntries] = useState<TimelineArtistEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const normalizedTarget = useMemo(() => normalizeArtist(artistName), [artistName])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const url = dataUrl('artist-timelines.json')
    fetch(url)
      .then(async (response) => {
        if (!response.ok) throw new Error(`Failed to load artist timelines (${response.status}).`)

        const payload = (await response.json()) as unknown
        if (!Array.isArray(payload)) throw new Error('Artist timelines payload was not an array.')

        return payload
          .map(parseTimelineArtistEntry)
          .filter((entry): entry is TimelineArtistEntry => entry !== null)
      })
      .then((parsed) => {
        if (cancelled) return
        setEntries(parsed)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setEntries([])
        setError(err instanceof Error ? err.message : 'Unable to load timeline data.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const match = useMemo(
    () => entries.find((entry) => normalizeArtist(entry.artist) === normalizedTarget) ?? null,
    [entries, normalizedTarget],
  )

  const sortedYears = useMemo(
    () => (match ? [...match.years].sort((a, b) => a.year - b.year || a.rank - b.rank) : []),
    [match],
  )

  return (
    <div className="artist-timeline-panel">
      <p className="artist-timeline-artist">{artistName || 'Artist'}</p>
      <p className="artist-timeline-subtitle">Influence Timeline</p>
      {loading ? <p>Loading timeline...</p> : null}
      {error ? <p className="muted">{error}</p> : null}
      {!loading && !error && sortedYears.length === 0 ? <p className="muted">No timeline data available.</p> : null}
      {!loading && !error && sortedYears.length > 0 ? (
        <ul className="artist-timeline-list">
          {sortedYears.map((entry) => (
            <li key={`${entry.year}-${entry.rank}`} className="artist-timeline-item">
              <span className="artist-timeline-year">{entry.year}</span>
              <span className="artist-timeline-rank">#{entry.rank}</span>
              <span className="artist-timeline-score">{entry.score.toFixed(1)}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
