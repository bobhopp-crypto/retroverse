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
  { to: '/charts', label: 'Charts App', reloadDocument: true },
  { to: '/video-library', label: 'Video Library' },
]

export const desktopNavItems: NavItem[] = [...NAV_ITEMS]

export const mobilePrimaryNavItems: NavItem[] = [...NAV_ITEMS]

export const mobileSecondaryNavItems: NavItem[] = []
