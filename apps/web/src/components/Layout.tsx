import { NavLink } from 'react-router-dom'
import type { PropsWithChildren } from 'react'
import { usePlaylistContext } from '../context/PlaylistContext'
import VideoPlayerModal from './VideoPlayerModal'
import ThemeToggle from './ThemeToggle'
import { desktopNavItems, mobilePrimaryNavItems } from '../theme/navConfig'

export default function Layout({ children }: PropsWithChildren) {
  const { queue, nowPlaying, closePlayer, onPlayerEnded } = usePlaylistContext()

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

        <div className="content-scroll">
          <main className="main-panel">{children}</main>
        </div>

        <nav className="bottom-nav" aria-label="Mobile navigation">
          {mobilePrimaryNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              reloadDocument={item.reloadDocument}
              className={({ isActive }) => ['tab', isActive ? 'active' : ''].join(' ')}
            >
              <span>{item.to === '/playlists' ? `Playlists (${queue.length})` : (item.mobileLabel ?? item.label)}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <VideoPlayerModal video={nowPlaying} onClose={closePlayer} onEnded={onPlayerEnded} />
    </div>
  )
}
