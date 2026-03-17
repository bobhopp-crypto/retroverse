import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ArtDepartmentMedia from '../../components/ArtDepartmentMedia'
import { Panel } from '../../components/ui/Card'
import {
  ART_DIRECTOR_ERAS,
  ART_DIRECTOR_PROJECT_TYPES,
  ART_DIRECTOR_TONES,
  artistPrimaryMedia,
  rankArtDepartmentArtists,
  useArtDepartmentRegistry,
} from '../../lib/artDepartmentClient'
import './ArtDepartment.css'

export default function ArtDirectorPage() {
  const { registry, loading, error } = useArtDepartmentRegistry()
  const [projectType, setProjectType] = useState<string>('Magazine Feature')
  const [era, setEra] = useState<string>('1970s')
  const [tone, setTone] = useState<string>('serious')

  const ranked = useMemo(() => {
    if (!registry) return []
    return rankArtDepartmentArtists(registry.artists, { projectType, era, tone })
  }, [era, projectType, registry, tone])

  return (
    <section className="hub-page art-page bg-[var(--rv4)]">
      <header className="page-heading">
        <p className="art-kicker">RetroVerse Art Director</p>
        <h1 className="page-title">Artist Matching</h1>
        <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">
          First-pass recommendation mode using direct metadata matches from the canonical artist registry. Scores are intentionally simple and explainable.
        </p>
      </header>

      <Panel className="art-panel">
        <h2>Controls</h2>
        <div className="art-director-controls">
          <div className="art-control">
            <label htmlFor="art-project-type">Project Type</label>
            <select id="art-project-type" value={projectType} onChange={(event) => setProjectType(event.target.value)}>
              {ART_DIRECTOR_PROJECT_TYPES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="art-control">
            <label htmlFor="art-era">Era</label>
            <select id="art-era" value={era} onChange={(event) => setEra(event.target.value)}>
              {ART_DIRECTOR_ERAS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="art-control">
            <label htmlFor="art-tone">Tone</label>
            <select id="art-tone" value={tone} onChange={(event) => setTone(event.target.value)}>
              {ART_DIRECTOR_TONES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Panel>

      <div className="art-actions">
        <Link to="/art-department" className="art-action-link">
          Back to Directory
        </Link>
      </div>

      {loading ? <Panel className="art-panel mt-6"><p className="art-panel-copy">Loading artist recommendations...</p></Panel> : null}
      {!loading && error ? <Panel className="art-panel mt-6"><p className="art-panel-copy">{error}</p></Panel> : null}

      {!loading && !error ? (
        <div className="art-director-results mt-6">
          {ranked.map(({ artist, score, reasons }) => {
            const media = artistPrimaryMedia(artist)
            return (
              <Panel key={artist.id} className="art-director-card">
                <div className="art-director-media">
                  <ArtDepartmentMedia src={media} alt={artist.display_name} fallbackLabel={artist.display_name} />
                </div>
                <div className="art-director-card-body">
                  <p className="art-card-subtitle">Score {score}</p>
                  <h3>{artist.display_name}</h3>
                  <p className="art-card-copy">{artist.department}</p>
                  <ul className="art-reason-list">
                    {reasons.map((reason) => (
                      <li key={`${artist.id}-${reason}`}>{reason}</li>
                    ))}
                  </ul>
                  <div className="art-chip-row mt-3">
                    {artist.style_traits.slice(0, 4).map((trait) => (
                      <span key={trait} className="art-chip">
                        {trait}
                      </span>
                    ))}
                  </div>
                  <div className="art-actions">
                    <Link to={`/art-department/${artist.id}`} className="art-action-link">
                      Open Profile
                    </Link>
                  </div>
                </div>
              </Panel>
            )
          })}
        </div>
      ) : null}
    </section>
  )
}
