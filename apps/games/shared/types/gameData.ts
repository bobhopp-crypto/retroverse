export type BillboardSongRecord = {
  artist: string
  title: string
  year: number
  chart_run: number[]
  peak: number
}

export type VideoMetadataRecord = {
  artist: string
  title: string
  year: number
  thumbnail: string
}

export type ChartClimberRound = {
  artist: string
  title: string
  year: number
  positions: number[]
}

export type YearShuffleEntry = {
  artist: string
  title: string
  year: number
}

export type YearShuffleRound = {
  entries: YearShuffleEntry[]
}

export type GuessPeakRound = {
  artist: string
  title: string
  year: number
  choices: number[]
  correct: number
}
