import type {
  ChartClimberRound,
  GuessPeakRound,
  VideoMetadataRecord,
  YearShuffleRound,
} from '../../../games/shared/types/gameData.ts'
import { PIPELINE_API_BASE } from './pipelineApi'

type ArcadeRoundsPayload<T> = {
  rounds?: T[]
  error?: string
}

const normalizePath = (path: string) => (path.startsWith('/') ? path : `/${path}`)

export type { ChartClimberRound, GuessPeakRound, VideoMetadataRecord, YearShuffleRound }

export const fetchArcadeRounds = async <T>(path: string, count: number): Promise<T[]> => {
  const url = new URL(`${PIPELINE_API_BASE}${normalizePath(path)}`, window.location.origin)
  url.searchParams.set('count', String(count))

  const response = await fetch(url.toString())
  const payload = (await response.json().catch(() => ({}))) as ArcadeRoundsPayload<T>

  if (!response.ok) {
    const message = typeof payload.error === 'string' ? payload.error : `Failed to load arcade rounds (${response.status})`
    throw new Error(message)
  }

  return Array.isArray(payload.rounds) ? payload.rounds : []
}

