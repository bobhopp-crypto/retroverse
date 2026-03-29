import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

const tools = [
  { name: 'Metadata viewer', status: 'planned' },
  { name: 'Playlist maintenance', status: 'planned' },
  { name: 'Match review helper', status: 'planned' },
  { name: 'Export packager', status: 'planned' },
  { name: 'Analytics dashboard', status: 'active' },
  { name: 'Data updater (legacy)', status: 'deprecated' },
]

type AlbumGridRecord = {
  album: string
  artist: string
  year: string | number
  album_type: string
  top_tracks?: string | string[] | null
  tracks?: string | string[] | null
}

type ToolsProps = {
  albums: AlbumGridRecord[]
  albumsLoading: boolean
  albumsError: string | null
}

const albumKey = (album: AlbumGridRecord): string => `${album.artist}::${album.album}::${album.year}`

const toTrackList = (trackSource: string | string[] | null | undefined): string[] => {
  if (Array.isArray(trackSource)) {
    return trackSource.map((track) => String(track).trim()).filter(Boolean)
  }
  if (typeof trackSource === 'string') {
    return trackSource
      .split('|')
      .map((track) => track.trim())
      .filter(Boolean)
  }
  return []
}

export default function Tools({ albums, albumsLoading, albumsError }: ToolsProps) {
  const [selectedAlbum, setSelectedAlbum] = useState<AlbumGridRecord | null>(null)

  const selectedTracks = useMemo(
    () => (selectedAlbum ? toTrackList(selectedAlbum.tracks ?? selectedAlbum.top_tracks) : []),
    [selectedAlbum],
  )

  // Temporary debug while validating click -> state -> render flow.
  console.log(selectedAlbum)

  return (
    <section className="stack">
      <div className="page-heading">
        <h1 className="page-title">Tools</h1>
        <span className="phase-flag">Phase 0 – structure only</span>
      </div>
      <p>
        <Link to="/analytics">Open Analytics</Link>
      </p>
      <p className="muted">List of intended utilities. Nothing executes in this phase.</p>

      <div className="section stack">
        <h2 className="section-title section-badge-album">Album Data Check</h2>
        {albumsLoading ? <p>Loading albums data...</p> : null}
        {albumsError ? <p className="muted">{albumsError}</p> : null}
        {!albumsLoading && !albumsError ? (
          <>
            <p className="muted">Rows loaded: {albums.length}</p>
            <div style={{ overflowX: 'auto' }}>
              <table className="simple-table">
                <thead>
                  <tr>
                    <th>album</th>
                    <th>artist</th>
                    <th>year</th>
                    <th>album_type</th>
                  </tr>
                </thead>
                <tbody>
                  {albums.map((album, index) => {
                    const key = albumKey(album)
                    const isSelected = selectedAlbum ? key === albumKey(selectedAlbum) : false
                    return (
                      <tr key={`${key}-${index}`} style={isSelected ? { background: 'var(--rv-surface)' } : undefined}>
                        <td>
                          <button
                            type="button"
                            className="toggle-btn"
                            style={{ padding: '4px 8px' }}
                            onClick={() => setSelectedAlbum(album)}
                          >
                            {album.album}
                          </button>
                        </td>
                        <td>{album.artist}</td>
                        <td>{album.year}</td>
                        <td>{album.album_type}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </>
        ) : null}
        {!albumsLoading && !albumsError && selectedAlbum ? (
          <div className="section">
            <h3 className="section-title section-badge-album">Top Tracks</h3>
            <p>
              <strong>{selectedAlbum.album}</strong> — {selectedAlbum.artist}
            </p>
            {selectedTracks.length > 0 ? (
              <ol>
                {selectedTracks.map((track, index) => (
                  <li key={`${track}-${index}`}>{track}</li>
                ))}
              </ol>
            ) : (
              <p className="muted">No top tracks available for this row.</p>
            )}
          </div>
        ) : null}
      </div>

      <div className="section" style={{ padding: 0 }}>
        <table className="simple-table">
          <thead>
            <tr>
              <th>Tool</th>
              <th>Status</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {tools.map((tool) => (
              <tr key={tool.name}>
                <td>{tool.name}</td>
                <td>{tool.status === 'deprecated' ? 'deprecated' : tool.status === 'active' ? 'active' : 'planned'}</td>
                <td className="muted">
                  {tool.status === 'deprecated'
                    ? 'Do not use. Replaced by future pipeline.'
                    : tool.status === 'active'
                      ? 'Live page available under Analytics.'
                      : 'Structure only; execution disabled.'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
