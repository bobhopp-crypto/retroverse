/**
 * RetroVerse Navigation Config
 * Single source of truth for nav items.
 */

export interface NavItem {
  to: string
  label: string
  /** Shorter label for mobile nav; falls back to label */
  mobileLabel?: string
  reloadDocument?: boolean
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Explore' },
  { to: '/surprise', label: 'Surprise' },
  { to: '/charts', label: 'Charts' },
  { to: '/video-library', label: 'Library' },
  { to: '/magazine', label: 'Magazine' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/setbuilder', label: 'SetBuilder' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/matching', label: 'Matching' },
  { to: '/games', label: 'Games' },
  { to: '/tools', label: 'Tools' },
]

export const desktopNavItems: NavItem[] = [
  { to: '/', label: 'Explore' },
  { to: '/surprise', label: 'Surprise' },
  { to: '/charts', label: 'Charts' },
  { to: '/video-library', label: 'Library' },
  { to: '/magazine', label: 'Magazine' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/setbuilder', label: 'SetBuilder' },
  { to: '/analytics', label: 'Analytics' },
]

export const mobilePrimaryNavItems: NavItem[] = [
  { to: '/', label: 'Explore' },
  { to: '/surprise', label: 'Surprise' },
  { to: '/charts', label: 'Charts' },
  { to: '/video-library', label: 'Library' },
]

export const mobileSecondaryNavItems: NavItem[] = [
  { to: '/magazine', label: 'Magazine' },
  { to: '/games', label: 'Games' },
  { to: '/playlists', label: 'Playlists' },
  { to: '/setbuilder', label: 'SetBuilder' },
  { to: '/analytics', label: 'Analytics' },
]
