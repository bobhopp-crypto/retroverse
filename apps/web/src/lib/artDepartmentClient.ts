import { useEffect, useState } from 'react'

export type ArtDepartmentArtist = {
  id: string
  display_name: string
  public_credit: string
  internal_influence: string
  department: string
  era_fit: string[]
  origin_region: string
  bio: string
  personality: string
  style_traits: string[]
  best_use: string[]
  avoid_use: string[]
  signature_notes: string
  self_portrait_prompt: string
  reference_scene_prompts: string[]
  self_portrait_path: string
  reference_images: string[]
  published_examples: Array<Record<string, unknown>>
  project_type_fit?: string[]
  tone_fit?: string[]
  type_samples?: string[]
}

export type ArtDepartmentRegistry = {
  version: number
  built_at?: string
  artists: ArtDepartmentArtist[]
}

export type ArtDirectorSelections = {
  projectType: string
  era: string
  tone: string
}

export type RankedArtDepartmentArtist = {
  artist: ArtDepartmentArtist
  score: number
  reasons: string[]
}

export const ART_DIRECTOR_PROJECT_TYPES = ['Magazine Feature', 'Poster', 'Comic Panel', 'Infographic', 'Card Illustration', 'Cover Art'] as const
export const ART_DIRECTOR_TONES = ['serious', 'playful', 'psychedelic', 'glamorous', 'documentary', 'surreal'] as const
export const ART_DIRECTOR_ERAS = ['Late 1960s', '1970s', 'Early 1980s', 'Cross-era'] as const

const REGISTRY_URL = `${import.meta.env.BASE_URL}art-department/registry.json`

const PROJECT_KEYWORDS: Record<string, string[]> = {
  'Magazine Feature': ['magazine feature', 'feature', 'editorial', 'profile', 'department'],
  Poster: ['poster', 'promo', 'one-sheet'],
  'Comic Panel': ['comic', 'panel', 'sequential'],
  Infographic: ['infographic', 'chart', 'timeline', 'data'],
  'Card Illustration': ['card', 'compact'],
  'Cover Art': ['cover', 'masthead', 'newsstand'],
}

const TONE_KEYWORDS: Record<string, string[]> = {
  serious: ['serious', 'quiet', 'narrative', 'gravitas'],
  playful: ['playful', 'comic', 'witty', 'bright'],
  psychedelic: ['psychedelic', 'ornamental', 'dream', 'hallucinatory'],
  glamorous: ['glamorous', 'fashion', 'luxury', 'celebrity'],
  documentary: ['documentary', 'reportage', 'observed', 'social'],
  surreal: ['surreal', 'symbolic', 'strange', 'dream'],
}

const ERA_KEYWORDS: Record<string, string[]> = {
  'Late 1960s': ['late-1960s', '1960s'],
  '1970s': ['1970s'],
  'Early 1980s': ['early-1980s', '1980s'],
  'Cross-era': [],
}

function includesToken(values: string[], tokens: string[]): boolean {
  const haystack = values.join(' ').toLowerCase()
  return tokens.some((token) => haystack.includes(token.toLowerCase()))
}

export async function fetchArtDepartmentRegistry(): Promise<ArtDepartmentRegistry> {
  const response = await fetch(REGISTRY_URL)
  if (!response.ok) {
    throw new Error(`Failed to load Art Department registry (${response.status}).`)
  }

  const payload = (await response.json()) as ArtDepartmentRegistry
  if (!payload || !Array.isArray(payload.artists)) {
    throw new Error('Art Department registry payload is invalid.')
  }
  return payload
}

export function useArtDepartmentRegistry() {
  const [registry, setRegistry] = useState<ArtDepartmentRegistry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetchArtDepartmentRegistry()
      .then((payload) => {
        if (cancelled) return
        setRegistry(payload)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setRegistry(null)
        setLoading(false)
        setError(err instanceof Error ? err.message : 'Unable to load Art Department registry.')
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { registry, loading, error }
}

export function artistPrimaryMedia(artist: ArtDepartmentArtist): string | null {
  if (artist.self_portrait_path) return artist.self_portrait_path
  if (artist.type_samples && artist.type_samples.length > 0) return artist.type_samples[0]
  if (artist.reference_images.length > 0) return artist.reference_images[0]
  return null
}

export function rankArtDepartmentArtists(artists: ArtDepartmentArtist[], selections: ArtDirectorSelections): RankedArtDepartmentArtist[] {
  return artists
    .map((artist) => {
      let score = 0
      const reasons: string[] = []
      const projectFits = artist.project_type_fit ?? []
      const toneFits = artist.tone_fit ?? []
      const searchableFields = [
        artist.department,
        ...artist.style_traits,
        ...artist.best_use,
        ...artist.avoid_use,
        ...artist.era_fit,
      ]

      if (projectFits.includes(selections.projectType)) {
        score += 5
        reasons.push(`${selections.projectType} is a direct fit.`)
      } else if (includesToken(searchableFields, PROJECT_KEYWORDS[selections.projectType] ?? [])) {
        score += 2
        reasons.push(`Best-use metadata overlaps ${selections.projectType.toLowerCase()} work.`)
      }

      if (toneFits.includes(selections.tone)) {
        score += 4
        reasons.push(`Tone fit is explicitly ${selections.tone}.`)
      } else if (includesToken(searchableFields, TONE_KEYWORDS[selections.tone] ?? [])) {
        score += 2
        reasons.push(`Style traits lean ${selections.tone}.`)
      }

      const eraTokens = ERA_KEYWORDS[selections.era] ?? []
      if (eraTokens.length === 0 || includesToken(artist.era_fit, eraTokens)) {
        score += eraTokens.length === 0 ? 1 : 3
        reasons.push(eraTokens.length === 0 ? 'Works across multiple eras.' : `Era fit includes ${selections.era}.`)
      }

      if (artist.department === 'Type & Lettering') {
        score += selections.projectType === 'Infographic' || selections.projectType === 'Cover Art' ? 1 : 0
      } else {
        score += 1
      }

      if (reasons.length === 0) {
        reasons.push('General style compatibility.')
      }

      return {
        artist,
        score,
        reasons: reasons.slice(0, 3),
      }
    })
    .sort((a, b) => b.score - a.score || a.artist.display_name.localeCompare(b.artist.display_name))
}
