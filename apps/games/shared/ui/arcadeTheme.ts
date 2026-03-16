import type { CSSProperties } from 'react'

export type ArcadeTone = 'default' | 'accent' | 'good' | 'warning' | 'danger'

export const joinArcadeClasses = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ')

export const arcadeThemeStyle = {
  '--arcade-bg-0': '#08111d',
  '--arcade-bg-1': '#0d1727',
  '--arcade-bg-2': '#13213a',
  '--arcade-panel': 'rgba(13, 23, 39, 0.78)',
  '--arcade-panel-strong': 'rgba(18, 31, 54, 0.94)',
  '--arcade-panel-soft': 'rgba(255, 255, 255, 0.04)',
  '--arcade-border': 'rgba(141, 170, 219, 0.24)',
  '--arcade-text': '#f3f6fb',
  '--arcade-muted': '#9caecf',
  '--arcade-accent': '#58c9ff',
  '--arcade-accent-soft': 'rgba(88, 201, 255, 0.16)',
  '--arcade-success': '#72f0b8',
  '--arcade-warning': '#f7cc7a',
  '--arcade-danger': '#ff8d97',
  '--arcade-shadow': '0 24px 56px rgba(0, 0, 0, 0.34)',
} as CSSProperties

