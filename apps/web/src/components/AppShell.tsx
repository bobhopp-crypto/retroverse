import { BarChart3, Library } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import type { PropsWithChildren } from 'react'
import { usePlaylistContext } from '../context/PlaylistContext'
import VideoPlayerModal from './VideoPlayerModal'
import ThemeToggle from './ThemeToggle'
import { desktopNavItems, mobilePrimaryNavItems } from '../theme/navConfig'

const iconByRoute = (route: string) => {
  switch (route) {
    case '/charts':
      return BarChart3
    case '/video-library':
      return Library
    default:
      return Library
  }
}

export default function AppShell({ children }: PropsWithChildren) {
  const { nowPlaying, closePlayer, onPlayerEnded } = usePlaylistContext()

  return (
    <div className="app-shell">
      <div className="rv-frame">
        <header className="topbar">
          <div className="brand">RetroVerse</div>
          <nav className="nav" aria-label="Primary navigation">
            {desktopNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                reloadDocument={item.reloadDocument}
                className={({ isActive }) => ['nav-link', isActive ? 'nav-link--active' : ''].join(' ')}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <ThemeToggle />
        </header>

        <div className="content-scroll">
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
        </nav>
      </div>

      <VideoPlayerModal video={nowPlaying} onClose={closePlayer} onEnded={onPlayerEnded} />
    </div>
  )
}
