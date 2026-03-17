import { Link } from 'react-router-dom'
import { NAV_ITEMS } from '../theme/navConfig'
import './Hub.css'

const HUB_DESCRIPTIONS: Record<string, string> = {
  '/video-library': 'Browse the RetroVerse video collection and featured clips.',
  '/charts': 'Explore chart history, rankings, and trend snapshots.',
  '/magazine': 'Explore RetroVerse yearly issues and cultural storytelling.',
  '/playlists': 'Build custom lineups and manage your saved sets.',
  '/setbuilder': 'Generate random combinations for quick curation sessions.',
  '/matching': 'Audit and align metadata with matching tools.',
  '/games': 'Play RetroVerse challenges, quizzes, and rapid picks.',
  '/tools': 'Use utility workflows that support the RetroVerse pipeline.',
  '/analytics': 'Review usage, output, and performance insights.',
}

const pages = NAV_ITEMS.filter((item) => item.to !== '/hub').map((item) => ({
  ...item,
  desc: HUB_DESCRIPTIONS[item.to] ?? '',
}))

type HubPage = (typeof pages)[number]

const HUB_SECTIONS: Array<{ title: string; routes: string[] }> = [
  {
    title: 'Explore',
    routes: ['/video-library', '/charts', '/magazine'],
  },
  {
    title: 'Create',
    routes: ['/playlists', '/setbuilder', '/games'],
  },
  {
    title: 'Tools',
    routes: ['/matching', '/tools', '/analytics'],
  },
]

const pageByRoute = new Map<string, HubPage>(pages.map((page) => [page.to, page]))

const sectionedPages = HUB_SECTIONS.map((section) => ({
  ...section,
  pages: section.routes
    .map((route) => pageByRoute.get(route))
    .filter((page): page is HubPage => page !== undefined),
}))

export default function Hub() {
  return (
    <section className="hub-page">
      <div className="page-heading">
        <h1 className="page-title">Hub</h1>
        <span className="phase-flag">RetroVerse Navigation</span>
      </div>
      <p className="hub-intro">Choose a destination to jump directly into the RetroVerse experience.</p>

      {sectionedPages.map((section) => (
        <div key={section.title}>
          <h2>{section.title}</h2>
          <div className="hub-card-grid">
            {section.pages.map((page) => (
              <Link key={page.to} to={page.to} className="hub-card" reloadDocument={page.reloadDocument}>
                <h2 className="hub-card-title">{page.label}</h2>
                <p className="hub-card-desc">{page.desc}</p>
                <span className="hub-card-cta">Open section</span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </section>
  )
}
