import { ArrowRight, Wand2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import ArtDepartmentMedia from '../../components/ArtDepartmentMedia'
import { CardLink, Panel } from '../../components/ui/Card'
import { artistPrimaryMedia, useArtDepartmentRegistry } from '../../lib/artDepartmentClient'
import './ArtDepartment.css'

export default function ArtDepartmentPage() {
  const { registry, loading, error } = useArtDepartmentRegistry()
  const artists = registry?.artists ?? []
  const illustrationCount = artists.filter((artist) => artist.department !== 'Type & Lettering').length
  const typeCount = artists.filter((artist) => artist.department === 'Type & Lettering').length

  return (
    <section className="hub-page art-page bg-[var(--rv4)]">
      <header className="page-heading">
        <p className="art-kicker">RetroVerse Magazine</p>
        <h1 className="page-title">Art Department</h1>
        <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">
          Directory of RetroVerse illustrators and lettering specialists. Portraits, reference work, and matching all read from the canonical
          magazine registry.
        </p>
        <div className="art-actions">
          <Link to="/art-director" className="art-action-link">
            <Wand2 size={15} />
            Open Art Director
          </Link>
          <Link to="/magazine" className="art-action-link">
            Back to Magazine
          </Link>
        </div>
      </header>

      <div className="art-stat-grid">
        <Panel className="art-stat-card">
          <p className="art-stat-label">Staff Profiles</p>
          <p className="art-stat-value">{artists.length}</p>
        </Panel>
        <Panel className="art-stat-card">
          <p className="art-stat-label">Illustration Staff</p>
          <p className="art-stat-value">{illustrationCount}</p>
        </Panel>
        <Panel className="art-stat-card">
          <p className="art-stat-label">Type Specialists</p>
          <p className="art-stat-value">{typeCount}</p>
        </Panel>
      </div>

      {loading ? <Panel className="art-panel mt-6"><p className="art-panel-copy">Loading art department registry...</p></Panel> : null}
      {!loading && error ? <Panel className="art-panel mt-6"><p className="art-panel-copy">{error}</p></Panel> : null}

      {!loading && !error ? (
        <div className="art-directory-grid">
          {artists.map((artist) => {
            const media = artistPrimaryMedia(artist)
            return (
              <CardLink key={artist.id} to={`/art-department/${artist.id}`} className="art-card">
                <div className="art-card-media">
                  <ArtDepartmentMedia src={media} alt={artist.display_name} fallbackLabel={artist.display_name} />
                </div>
                <div className="art-card-body">
                  <div className="art-card-head">
                    <div>
                      <h2 className="art-card-title">{artist.display_name}</h2>
                      <p className="art-card-subtitle">{artist.department}</p>
                    </div>
                    <ArrowRight size={18} className="text-[var(--rv5)]" />
                  </div>
                  <p className="art-card-copy">{artist.bio}</p>
                  <div className="art-chip-row">
                    {artist.style_traits.slice(0, 4).map((trait) => (
                      <span key={trait} className="art-chip">
                        {trait}
                      </span>
                    ))}
                  </div>
                </div>
              </CardLink>
            )
          })}
        </div>
      ) : null}
    </section>
  )
}
