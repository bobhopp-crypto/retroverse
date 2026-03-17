export interface Song {
  title: string
  artist: string
  year: number
  peak: number
  weeks: number
  run: number[]
  entry_week?: number
  peak_week?: number
  exit_week?: number
  weeks_at_peak?: number
  entryDate?: string // Week of entry (e.g., "1983-04-09")
  lastWeek?: number | null // Position last week, null for NEW or RE
  isNew?: boolean // NEW entry this week
  isReentry?: boolean // RE re-entry to chart
}

export interface ArtistData {
  name: string
  totalSongs: number
  top10Hits: number
  numberOneHits: number
  longestChartRun: number
  averagePeak: number
  songsByDecade: Record<string, number>
  songs: Song[]
}

export interface WeeklyChart {
  weekOf: string
  songs: WeeklyChartEntry[]
}

export interface WeeklyChartEntry {
  position: number
  song: Song
  lastWeek: number | null
  weeksOnChart: number
  peak: number
  movement: 'up' | 'down' | 'same' | 'new' | 're'
}

export interface ChartStats {
  mostWeeksOnChart: { song: Song; weeks: number }[]
  biggestClimbs: { song: Song; jump: number; from: number; to: number }[]
  longestNumberOneRuns: { song: Song; consecutiveWeeks: number }[]
  artistsWithMostTop10: { artist: string; count: number }[]
  artistsWithMostNumberOnes: { artist: string; count: number }[]
}

export interface RandomYearData {
  year: number
  topSongs: Song[]
  biggestHits: Song[]
  artistsWithMultipleHits: { artist: string; songs: Song[] }[]
  longestChartRuns: Song[]
}

export type FilterType = '#1' | 'Top10' | 'Top40' | '60s' | '70s' | '80s' | '90s' | 'random'
export type ViewMode = 'main' | 'songDetail' | 'artist' | 'chartStats' | 'randomYear' | 'weeklyChart' | 'about' | 'sectionList'
