import { useEffect, useMemo, useState } from 'react'
import { dataUrl } from '../config/dataSources'
import './ArtistGravityPanel.css'

type ArtistGravityRow = {
  artist: string
  score: number
}

type ArtistGravityPanelProps = {
  year: number
}

const toNumber = (value: unknown): number | null => {
  const parsed = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const parseArtistGravityRow = (value: unknown): ArtistGravityRow | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>

  const artist = typeof row.artist === 'string' ? row.artist.trim() : ''
  const score = toNumber(row.score)
  if (!artist || score === null) return null

  return {
    artist,
    score,
  }
}

export default function ArtistGravityPanel({ year }: ArtistGravityPanelProps) {
  const [rows, setRows] = useState<ArtistGravityRow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFullRanking, setShowFullRanking] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setShowFullRanking(false)

    const url = dataUrl(`artist-gravity/${year}.json`)

    fetch(url)
      .then(async (response) => {
        if (response.status === 404) return []
        if (!response.ok) throw new Error(`Failed to load artist gravity data (${response.status}).`)

        const payload = (await response.json()) as unknown
        if (!Array.isArray(payload)) throw new Error('Artist gravity payload was not an array.')

        return payload
          .map(parseArtistGravityRow)
          .filter((entry): entry is ArtistGravityRow => entry !== null)
      })
      .then((entries) => {
        if (cancelled) return
        setRows(entries)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setRows([])
        setError(err instanceof Error ? err.message : 'Unable to load artist gravity data.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [year])

  const sortedRows = useMemo(
    () => [...rows].sort((a, b) => b.score - a.score || a.artist.localeCompare(b.artist)),
    [rows],
  )

  const visibleRows = showFullRanking ? sortedRows : sortedRows.slice(0, 5)

  return (
    <div className="section">
      <h2 className="section-title section-badge-artist">Dominant Artists of {year}</h2>
      {loading ? <p>Loading artist rankings...</p> : null}
      {error ? <p className="muted">{error}</p> : null}
      {!loading && !error && visibleRows.length === 0 ? <div className="placeholder-box">No artist gravity data available for {year}.</div> : null}
      {!loading && !error && visibleRows.length > 0 ? (
        <>
          <ol className="artist-gravity-list">
            {visibleRows.map((entry, index) => (
              <li key={`${entry.artist}-${entry.score}-${index}`} className="artist-gravity-item">
                <span className="artist-gravity-rank">{index + 1}.</span>
                <span className="artist-gravity-name">{entry.artist}</span>
              </li>
            ))}
          </ol>
          {!showFullRanking && sortedRows.length > 5 ? (
            <button type="button" className="artist-gravity-link" onClick={() => setShowFullRanking(true)}>
              View Full Ranking
            </button>
          ) : null}
        </>
      ) : null}
    </div>
  )
}
