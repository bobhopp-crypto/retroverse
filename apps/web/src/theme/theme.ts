/**
 * RetroVerse Theme System
 * Theme switching and persistence.
 */

export type ThemeId = 'retroverse' | 'light' | 'dark'

const STORAGE_KEY = 'retroverse.theme'

export function getTheme(): ThemeId {
  if (typeof document === 'undefined') return 'retroverse'
  const stored = localStorage.getItem(STORAGE_KEY) as ThemeId | null
  if (stored && ['retroverse', 'light', 'dark'].includes(stored)) return stored
  return 'retroverse'
}

export function setTheme(theme: ThemeId): void {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem(STORAGE_KEY, theme)
}

export function initTheme(): void {
  const theme = getTheme()
  document.documentElement.setAttribute('data-theme', theme)
}
