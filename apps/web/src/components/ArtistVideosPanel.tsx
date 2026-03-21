import { useEffect, useMemo, useState } from 'react'
import { normalizeArtist } from '../lib/normalize'
import { loadVideoIndex, type VideoRecord } from '../lib/videoIndex'
import './ArtistVideosPanel.css'

type ArtistVideosPanelProps = {
  artistName: string
  decadeHints?: string[]
}

type VideoEntry = {
  title: string
  artist: string
  playUrl: string | null
}

const toVideoEntry = (row: VideoRecord): VideoEntry | null => {
  const title = row.title.trim()
  const artist = row.artist.trim()
  if (!title || !artist) return null
  return {
    title,
    artist,
    playUrl: row.videoUrl ?? null,
  }
}

export default function ArtistVideosPanel({ artistName, decadeHints = [] }: ArtistVideosPanelProps) {
  const [rows, setRows] = useState<VideoEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const decades = [...new Set(decadeHints.map((entry) => entry.trim()).filter((entry) => entry.length > 0))]
    const loadPromise =
      decades.length > 0 ? Promise.all(decades.map((decade) => loadVideoIndex(decade))).then((chunks) => chunks.flat()) : loadVideoIndex()

    loadPromise
      .then((videoRows) => {
        return videoRows
          .map(toVideoEntry)
          .filter((entry): entry is VideoEntry => entry !== null)
      })
      .then((parsed) => {
        if (cancelled) return
        setRows(parsed)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setRows([])
        setError(err instanceof Error ? err.message : 'Unable to load artist videos.')
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [decadeHints])

  const normalizedTarget = useMemo(() => normalizeArtist(artistName), [artistName])

  const filtered = useMemo(
    () =>
      rows
        .filter((row) => normalizeArtist(row.artist) === normalizedTarget)
        .sort((a, b) => a.title.localeCompare(b.title)),
    [rows, normalizedTarget],
  )

  const onPlay = (entry: VideoEntry) => {
    if (entry.playUrl) {
      window.open(entry.playUrl, '_blank', 'noopener,noreferrer')
      return
    }
    window.location.assign('/video-library')
  }

  return (
    <div className="section">
      <h2 className="section-title section-badge-video">Artist Videos</h2>
      {loading ? <p>Loading artist videos...</p> : null}
      {error ? <p className="muted">{error}</p> : null}
      {!loading && filtered.length === 0 ? <p className="muted">No videos available for this artist.</p> : null}
      {!loading && filtered.length > 0 ? (
        <ul className="artist-videos-list">
          {filtered.map((entry, index) => (
            <li key={`${entry.artist}-${entry.title}-${index}`} className="artist-videos-item">
              <p className="artist-videos-title">{entry.title}</p>
              <button type="button" className="artist-videos-play-btn" onClick={() => onPlay(entry)}>
                Play Video
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
