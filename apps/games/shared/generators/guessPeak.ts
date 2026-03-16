import { getHitSongs } from '../data/playablePools.js'
import type { BillboardSongRecord, GuessPeakRound } from '../types/gameData.js'

const CHOICE_COUNT = 4
const MIN_PEAK = 1
const MAX_PEAK = 100
const DISTRACTOR_OFFSETS = [-1, 1, -2, 2, -3, 3, -5, 5, -8, 8, -10, 10, -12, 12]

const randomInt = (maxExclusive: number) => Math.floor(Math.random() * maxExclusive)

const shuffle = <T>(items: T[]) => {
  const copy = [...items]
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = randomInt(index + 1)
    ;[copy[index], copy[swapIndex]] = [copy[swapIndex]!, copy[index]!]
  }
  return copy
}

const isValidPeak = (value: unknown): value is number => Number.isInteger(value) && value >= MIN_PEAK && value <= MAX_PEAK

const isPlayableSong = (song: BillboardSongRecord) => {
  if (typeof song.artist !== 'string' || song.artist.trim().length === 0) return false
  if (typeof song.title !== 'string' || song.title.trim().length === 0) return false
  if (!Number.isInteger(song.year)) return false
  return isValidPeak(song.peak)
}

const buildChoices = (correct: number) => {
  const choices = new Set<number>([correct])

  for (const offset of DISTRACTOR_OFFSETS) {
    const candidate = correct + offset
    if (candidate < MIN_PEAK || candidate > MAX_PEAK) continue
    choices.add(candidate)
    if (choices.size === CHOICE_COUNT) return shuffle(Array.from(choices))
  }

  for (let candidate = MIN_PEAK; candidate <= MAX_PEAK && choices.size < CHOICE_COUNT; candidate += 1) {
    if (candidate === correct) continue
    choices.add(candidate)
  }

  return choices.size === CHOICE_COUNT ? shuffle(Array.from(choices)) : null
}

export const generateGuessPeakRound = async (): Promise<GuessPeakRound | null> => {
  const songs = (await getHitSongs()).filter(isPlayableSong)
  if (songs.length === 0) return null

  const song = songs[randomInt(songs.length)]!
  const correct = song.peak
  const choices = buildChoices(correct)

  if (!choices) return null

  return {
    artist: song.artist,
    title: song.title,
    year: song.year,
    choices,
    correct,
  }
}
