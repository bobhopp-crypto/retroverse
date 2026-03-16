import { getYearIdentifiers } from '../data/playablePools.js'
import type { YearShuffleEntry, YearShuffleRound } from '../types/gameData.js'

const ROUND_SIZE = 4

const randomInt = (maxExclusive: number) => Math.floor(Math.random() * maxExclusive)

const shuffle = <T>(items: T[]) => {
  const copy = [...items]
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = randomInt(index + 1)
    ;[copy[index], copy[swapIndex]] = [copy[swapIndex]!, copy[index]!]
  }
  return copy
}

export const generateYearShuffleRound = async (): Promise<YearShuffleRound | null> => {
  const songs = await getYearIdentifiers()
  const songsByYear = new Map<number, YearShuffleEntry[]>()

  for (const song of songs) {
    const entry: YearShuffleEntry = {
      artist: song.artist,
      title: song.title,
      year: song.year,
    }
    const current = songsByYear.get(song.year) ?? []
    current.push(entry)
    songsByYear.set(song.year, current)
  }

  const years = shuffle(Array.from(songsByYear.keys()))
  if (years.length < ROUND_SIZE) return null

  const entries = years
    .slice(0, ROUND_SIZE)
    .map((year) => {
      const bucket = songsByYear.get(year) ?? []
      if (bucket.length === 0) return null
      return bucket[randomInt(bucket.length)]!
    })
    .filter((entry): entry is YearShuffleEntry => entry !== null)

  if (entries.length !== ROUND_SIZE) return null

  return {
    entries: shuffle(entries),
  }
}
