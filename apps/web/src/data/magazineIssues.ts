export type MagazinePageContent = {
  title: string
  subtitle?: string
  body: string
  image?: string
}

export type MagazineIssue = {
  year: number
  title: string
  pages: string[]
  content: Record<string, MagazinePageContent>
}

export const MAGAZINE_MIN_YEAR = 1958
export const MAGAZINE_MAX_YEAR = 2025

export const MAGAZINE_ISSUES: Record<string, MagazineIssue> = {
  '1978': {
    year: 1978,
    title: 'RetroVerse 1978 Annual',
    pages: ['cover', 'contents', 'intro', 'chart-history', 'feature-a', 'feature-b', 'culture-note', 'playlist', 'deep-cut', 'back-cover'],
    content: {
      cover: {
        title: '1978 Annual Issue',
        subtitle: 'RetroVerse Magazine',
        body: 'A yearly look at music charts, studio moments, and culture snapshots from 1978.',
        image: '/images/1978_raw_R1.png',
      },
      contents: {
        title: 'Contents',
        body: 'Intro • Chart History • Features • Culture Notes • Playlist Deck • Deep Cuts',
        image: '/images/1978_raw_02.png',
      },
      intro: {
        title: 'Editor Intro',
        body: '1978 marked a wide-open year in music with crossover sounds, bold production, and new chart narratives.',
        image: '/images/1978_raw_03.png',
      },
      'chart-history': {
        title: 'Chart History',
        body: 'Week-by-week movement highlights how records climbed, stalled, and surged across the year.',
        image: '/images/1978_raw_04.png',
      },
      'feature-a': {
        title: 'Feature Story',
        body: 'Studio decisions and radio momentum shaped the biggest records of the season.',
        image: '/images/1978_raw_05.png',
      },
      'feature-b': {
        title: 'Behind the Sound',
        body: 'Arrangements, rhythm sections, and vocal textures created signature chart moments.',
        image: '/images/1978_raw_06.png',
      },
      'culture-note': {
        title: 'Culture Notes',
        body: 'Touring, television, and fashion intersected with chart stories all year long.',
        image: '/images/1978_raw_07.png',
      },
      playlist: {
        title: 'Issue Playlist',
        body: 'A curated run of era-defining tracks selected for replay and rediscovery.',
        image: '/images/1978_raw_08.png',
      },
      'deep-cut': {
        title: 'Deep Cut',
        body: 'Beyond the obvious hits, this issue highlights songs that quietly shaped the year.',
        image: '/images/1978_raw_09.png',
      },
      'back-cover': {
        title: 'Back Cover',
        body: 'Thanks for reading the 1978 issue of RetroVerse Magazine.',
        image: '/images/1978_raw_10.png',
      },
    },
  },
}

export const MAGAZINE_AVAILABLE_ISSUES = Object.keys(MAGAZINE_ISSUES)
  .map((year) => Number(year))
  .sort((a, b) => b - a)

export const MAGAZINE_YEAR_INDEX = Array.from({ length: MAGAZINE_MAX_YEAR - MAGAZINE_MIN_YEAR + 1 }, (_, offset) => MAGAZINE_MIN_YEAR + offset)

export const MAGAZINE_YEARS = MAGAZINE_YEAR_INDEX

export function isMagazineYear(year: string | number): boolean {
  const value = Number(year)
  return Number.isInteger(value) && value >= MAGAZINE_MIN_YEAR && value <= MAGAZINE_MAX_YEAR
}

export function getMagazineIssue(year: string | number): MagazineIssue | undefined {
  return MAGAZINE_ISSUES[String(year)]
}
