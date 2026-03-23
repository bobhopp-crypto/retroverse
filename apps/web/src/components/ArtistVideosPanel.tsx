import { useEffect, useMemo, useState } from 'react'
import { VIDEO_INDEX_URL } from '../config/dataSources'
import { MEDIA_BASE } from '../config/media'
import { normalizeArtist } from '../lib/normalize'
import './ArtistVideosPanel.css'

type ArtistVideosPanelProps = {
  artistName: string
}

type VideoEntry = {
  title: string
  artist: string
  playUrl: string | null
}

const toStringValue = (value: unknown): string => (typeof value === 'string' ? value.trim() : '')

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

const parseVideoEntry = (value: unknown): VideoEntry | null => {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>
  const tags = row.tags && typeof row.tags === 'object' ? (row.tags as Record<string, unknown>) : null

  const title = toStringValue(row.title ?? tags?.title)
  const artist = toStringValue(row.artist ?? row.author ?? tags?.author)
  if (!title || !artist) return null

  const explicitUrl = toStringValue(row.videoUrl ?? row.video_url)
  const filePath = toStringValue(row.filePath ?? row.filepath ?? row.relative_media_path)

  return {
    title,
    artist,
    playUrl: explicitUrl || buildVideoUrlFromPath(filePath) || null,
  }
}

export default function ArtistVideosPanel({ artistName }: ArtistVideosPanelProps) {
  const [rows, setRows] = useState<VideoEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const url = VIDEO_INDEX_URL
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

        return rawRows
          .map(parseVideoEntry)
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
  }, [])

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
