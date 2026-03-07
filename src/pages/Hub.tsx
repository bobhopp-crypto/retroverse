import { Link } from 'react-router-dom'
import './Hub.css'

const pages = [
  { to: '/video-library', label: 'Video Library', desc: 'Browse the RetroVerse video collection' },
  { to: '/charts', label: 'Charts', desc: 'Explore Billboard Hot 100 chart history' },
  { to: '/playlists', label: 'Playlists', desc: 'Create and manage music sets' },
  { to: '/random', label: 'Random', desc: 'Jump into a random RetroVerse experience' },
  { to: '/matching', label: 'Matching', desc: 'Review metadata and tag matching tools' },
  { to: '/games', label: 'Games', desc: 'Interactive RetroVerse trivia and challenges' },
  { to: '/tools', label: 'Tools', desc: 'Utilities and data tools for RetroVerse' },
]

export default function Hub() {
  return (
    <section>
      <div className="page-heading">
        <h1 className="page-title">Hub</h1>
        <span className="phase-flag">Phase 0 – structure only</span>
      </div>
      <p className="muted">Choose a section to view its skeleton. Nothing is wired or interactive yet.</p>

      <div className="hub-card-grid">
        {pages.map((page) => (
          <Link key={page.to} to={page.to} className="hub-card" reloadDocument={page.to === '/charts'}>
            <h2 className="hub-card-title">{page.label}</h2>
            <p className="hub-card-desc">{page.desc}</p>
          </Link>
        ))}
      </div>
    </section>
  )
}
