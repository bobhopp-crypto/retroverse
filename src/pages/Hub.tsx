import { Link } from 'react-router-dom'
import './Hub.css'

const pages = [
  { to: '/video-library', label: 'Video Library', desc: 'Browse the RetroVerse video collection and featured clips.' },
  { to: '/charts', label: 'Charts', desc: 'Explore Billboard chart history, rankings, and trend snapshots.', reloadDocument: true },
  {
    to: '/magazine/1978.html',
    label: 'Magazine',
    desc: 'Explore RetroVerse issues built from chart history, pop culture, and AI storytelling.',
    reloadDocument: true,
  },
  { to: '/playlists', label: 'Playlists', desc: 'Build custom lineups and manage your saved sets.' },
  { to: '/random', label: 'SetBuilder', desc: 'Generate random combinations for quick curation sessions.' },
  { to: '/matching', label: 'Matching', desc: 'Audit and align metadata with matching tools.' },
  { to: '/games', label: 'Games', desc: 'Play RetroVerse challenges, quizzes, and rapid picks.' },
  { to: '/tools', label: 'Tools', desc: 'Use utility workflows that support the RetroVerse pipeline.' },
  { to: '/analytics', label: 'Analytics', desc: 'Review usage, output, and performance insights.' },
]

export default function Hub() {
  return (
    <section className="hub-page">
      <div className="page-heading">
        <h1 className="page-title">Hub</h1>
        <span className="phase-flag">RetroVerse Navigation</span>
      </div>
      <p className="hub-intro">Choose a destination to jump directly into the RetroVerse experience.</p>

      <div className="hub-card-grid">
        {pages.map((page) => (
          <Link key={page.to} to={page.to} className="hub-card" reloadDocument={page.reloadDocument}>
            <h2 className="hub-card-title">{page.label}</h2>
            <p className="hub-card-desc">{page.desc}</p>
            <span className="hub-card-cta">Open section</span>
          </Link>
        ))}
      </div>
    </section>
  )
}
