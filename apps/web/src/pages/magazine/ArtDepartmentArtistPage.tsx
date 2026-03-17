import { Link, useParams } from 'react-router-dom'
import ArtDepartmentMedia from '../../components/ArtDepartmentMedia'
import { Panel } from '../../components/ui/Card'
import { artistPrimaryMedia, useArtDepartmentRegistry } from '../../lib/artDepartmentClient'
import './ArtDepartment.css'

export default function ArtDepartmentArtistPage() {
  const { artistId = '' } = useParams<{ artistId: string }>()
  const { registry, loading, error } = useArtDepartmentRegistry()
  const artist = registry?.artists.find((item) => item.id === artistId) ?? null

  if (loading) {
    return (
      <section className="hub-page art-page bg-[var(--rv4)]">
        <Panel className="art-panel">
          <p className="art-panel-copy">Loading artist profile...</p>
        </Panel>
      </section>
    )
  }

  if (error || !artist) {
    return (
      <section className="hub-page art-page bg-[var(--rv4)]">
        <header className="page-heading">
          <h1 className="page-title">Artist Not Found</h1>
        </header>
        <Panel className="art-panel">
          <p className="art-panel-copy">{error ?? 'No matching art department profile was found.'}</p>
          <div className="art-actions">
            <Link to="/art-department" className="art-action-link">
              Back to Directory
            </Link>
          </div>
        </Panel>
      </section>
    )
  }

  const media = artistPrimaryMedia(artist)

  return (
    <section className="hub-page art-page bg-[var(--rv4)]">
      <header className="page-heading">
        <p className="art-kicker">RetroVerse Art Department</p>
        <h1 className="page-title">{artist.public_credit}</h1>
        <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">{artist.bio}</p>
        <div className="art-actions">
          <Link to="/art-department" className="art-action-link">
            Back to Directory
          </Link>
          <Link to="/art-director" className="art-action-link">
            Open Art Director
          </Link>
        </div>
      </header>

      <div className="art-profile-grid">
        <Panel className="art-profile-media">
          <ArtDepartmentMedia src={media} alt={artist.display_name} fallbackLabel={artist.display_name} />
        </Panel>

        <div className="art-profile-main">
          <Panel className="art-panel">
            <h2>Profile</h2>
            <p className="art-panel-copy">{artist.personality}</p>
            <div className="art-meta-row">
              <div className="art-meta-item">
                <p className="art-meta-label">Department</p>
                <p className="art-meta-value">{artist.department}</p>
              </div>
              <div className="art-meta-item">
                <p className="art-meta-label">Origin Region</p>
                <p className="art-meta-value">{artist.origin_region}</p>
              </div>
              <div className="art-meta-item">
                <p className="art-meta-label">Era Fit</p>
                <p className="art-meta-value">{artist.era_fit.join(', ')}</p>
              </div>
            </div>
          </Panel>

          <Panel className="art-panel">
            <h2>Style Traits</h2>
            <div className="art-chip-row">
              {artist.style_traits.map((trait) => (
                <span key={trait} className="art-chip">
                  {trait}
                </span>
              ))}
            </div>
            <p className="art-panel-copy mt-3">{artist.signature_notes}</p>
          </Panel>

          <div className="art-grid-two">
            <Panel className="art-panel">
              <h3>Best Use</h3>
              <ul className="art-list">
                {artist.best_use.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Panel>
            <Panel className="art-panel">
              <h3>Avoid Use</h3>
              <ul className="art-list">
                {artist.avoid_use.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </Panel>
          </div>

          <Panel className="art-panel">
            <h2>Internal Influence</h2>
            <p className="art-panel-copy">{artist.internal_influence}</p>
          </Panel>
        </div>
      </div>

      <section className="art-section">
        <h2>Reference Gallery</h2>
        {artist.reference_images.length > 0 ? (
          <div className="art-gallery">
            {artist.reference_images.map((imagePath, index) => (
              <Panel key={imagePath} className="art-gallery-card">
                <ArtDepartmentMedia src={imagePath} alt={`${artist.display_name} reference ${index + 1}`} fallbackLabel={`Ref ${index + 1}`} />
                <div className="art-gallery-card-body">
                  <h3>Reference {index + 1}</h3>
                  <p className="art-muted">Generated from the canonical artist registry.</p>
                </div>
              </Panel>
            ))}
          </div>
        ) : (
          <Panel className="art-panel">
            <p className="art-panel-copy">No generated reference work is attached yet.</p>
          </Panel>
        )}
      </section>

      {artist.type_samples && artist.type_samples.length > 0 ? (
        <section className="art-section">
          <h2>Type Samples</h2>
          <div className="art-type-samples">
            {artist.type_samples.map((imagePath, index) => (
              <Panel key={imagePath} className="art-type-card">
                <ArtDepartmentMedia src={imagePath} alt={`${artist.display_name} type sample ${index + 1}`} fallbackLabel={`Sample ${index + 1}`} />
                <div className="art-type-card-body">
                  <h3>Sample {index + 1}</h3>
                  <p className="art-muted">Placeholder departmental sample.</p>
                </div>
              </Panel>
            ))}
          </div>
        </section>
      ) : null}

      <section className="art-section">
        <h2>Published Works</h2>
        {artist.published_examples.length > 0 ? (
          <div className="art-gallery">
            {artist.published_examples.map((item, index) => (
              <Panel key={`${artist.id}-published-${index}`} className="art-gallery-card">
                <div className="art-gallery-card-body">
                  <h3>{String(item.title ?? `Published Work ${index + 1}`)}</h3>
                  <p className="art-muted">{String(item.note ?? 'Published example metadata is attached in the canonical registry.')}</p>
                </div>
              </Panel>
            ))}
          </div>
        ) : (
          <Panel className="art-panel">
            <p className="art-panel-copy">No published magazine pages are attached yet.</p>
          </Panel>
        )}
      </section>
    </section>
  )
}
