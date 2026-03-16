import { useEffect, useMemo, useState, type PropsWithChildren } from 'react'
import {
  Activity,
  BarChart3,
  BookOpen,
  Compass,
  Gamepad2,
  Library,
  ListMusic,
  Menu,
  Sparkles,
  Wrench,
  X,
} from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'
import { usePlaylistContext } from '../context/PlaylistContext'
import VideoPlayerModal from './VideoPlayerModal'
import ThemeToggle from './ThemeToggle'
import { desktopNavItems, mobilePrimaryNavItems, mobileSecondaryNavItems } from '../theme/navConfig'

const secondaryPaths = new Set(mobileSecondaryNavItems.map((item) => item.to))

const iconByRoute = (route: string) => {
  switch (route) {
    case '/':
      return Compass
    case '/surprise':
      return Sparkles
    case '/charts':
      return BarChart3
    case '/video-library':
      return Library
    case '/magazine':
      return BookOpen
    case '/games':
      return Gamepad2
    case '/playlists':
      return ListMusic
    case '/setbuilder':
      return Wrench
    case '/analytics':
      return Activity
    default:
      return Compass
  }
}

export default function AppShell({ children }: PropsWithChildren) {
  const { pathname } = useLocation()
  const { queue, nowPlaying, closePlayer, onPlayerEnded } = usePlaylistContext()
  const [isMoreOpen, setIsMoreOpen] = useState(false)

  const isSecondaryActive = useMemo(() => {
    if (secondaryPaths.has(pathname)) return true
    for (const route of secondaryPaths) {
      if (pathname.startsWith(`${route}/`)) {
        return true
      }
    }
    return false
  }, [pathname])
  const isMagazineReader = useMemo(() => /^\/magazine\/\d{4}(?:\/page\/\d+)?$/.test(pathname), [pathname])

  useEffect(() => {
    setIsMoreOpen(false)
  }, [pathname])

  useEffect(() => {
    if (!isMoreOpen) return

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsMoreOpen(false)
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [isMoreOpen])

  return (
    <div className="app-shell">
      <div className="rv-frame">
        <header className="topbar">
          <div className="brand">RetroVerse</div>
          <nav className="nav">
            {desktopNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                reloadDocument={item.reloadDocument}
                className={({ isActive }) => ['nav-link', isActive ? 'nav-link--active' : ''].join(' ')}
              >
                {item.to === '/playlists' ? `Playlists (${queue.length})` : item.label}
              </NavLink>
            ))}
          </nav>
          <ThemeToggle />
        </header>

        <div className={`content-scroll ${isMagazineReader ? 'content-scroll--locked' : ''}`}>
          <main className="main-panel">{children}</main>
        </div>

        <nav className="bottom-nav" aria-label="Mobile navigation">
          {mobilePrimaryNavItems.map((item) => {
            const Icon = iconByRoute(item.to)
            const label = item.mobileLabel ?? item.label
            return (
              <NavLink
                key={item.to}
                to={item.to}
                reloadDocument={item.reloadDocument}
                className={({ isActive }) => ['tab', isActive ? 'active' : ''].join(' ')}
              >
                <Icon size={17} aria-hidden />
                <span>{label}</span>
              </NavLink>
            )
          })}

          <button
            type="button"
            className={`tab tab-button ${isMoreOpen || isSecondaryActive ? 'active' : ''}`}
            aria-expanded={isMoreOpen}
            aria-controls="rv-more-sheet"
            onClick={() => setIsMoreOpen((open) => !open)}
          >
            <Menu size={17} aria-hidden />
            <span>More</span>
          </button>
        </nav>
      </div>

      <div
        className={`more-sheet-scrim ${isMoreOpen ? 'is-open' : ''}`}
        aria-hidden={!isMoreOpen}
        onClick={() => setIsMoreOpen(false)}
      >
        <section
          id="rv-more-sheet"
          className={`more-sheet ${isMoreOpen ? 'is-open' : ''}`}
          role="dialog"
          aria-label="More navigation"
          onClick={(event) => event.stopPropagation()}
        >
          <div className="more-sheet-handle" aria-hidden />
          <header className="more-sheet-head">
            <p>More</p>
            <button type="button" onClick={() => setIsMoreOpen(false)} aria-label="Close more menu">
              <X size={16} aria-hidden />
            </button>
          </header>
          <div className="more-sheet-links">
            {mobileSecondaryNavItems.map((item) => {
              const Icon = iconByRoute(item.to)
              const label = item.to === '/playlists' ? `Playlists (${queue.length})` : item.label
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  reloadDocument={item.reloadDocument}
                  className={({ isActive }) => ['more-sheet-link', isActive ? 'active' : ''].join(' ')}
                >
                  <Icon size={18} aria-hidden />
                  <span>{label}</span>
                </NavLink>
              )
            })}
          </div>
        </section>
      </div>

      <VideoPlayerModal video={nowPlaying} onClose={closePlayer} onEnded={onPlayerEnded} />
    </div>
  )
}
