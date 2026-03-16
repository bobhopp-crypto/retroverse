import type { ChartClimberRound } from '../types/gameData.js'
import { getChartClimbers } from '../data/playablePools.js'

const SLICE_LENGTH = 5

const randomInt = (maxExclusive: number) => Math.floor(Math.random() * maxExclusive)

export const generateChartClimberRound = async (): Promise<ChartClimberRound | null> => {
  const candidates = await getChartClimbers()
  if (candidates.length === 0) return null

  const song = candidates[randomInt(candidates.length)]!
  const maxStart = song.chart_run.length - SLICE_LENGTH
  if (maxStart < 0) return null
  const start = randomInt(maxStart + 1)
  const positions = song.chart_run.slice(start, start + SLICE_LENGTH)

  if (positions.length !== SLICE_LENGTH) return null

  return {
    artist: song.artist,
    title: song.title,
    year: song.year,
    positions,
  }
}
