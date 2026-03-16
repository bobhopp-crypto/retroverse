import type { ChartClimberRound, GuessPeakRound, VideoMetadataRecord, YearShuffleRound } from '../../lib/arcadeClient'

export const chartClimberDemoRounds: ChartClimberRound[] = [
  {
    artist: 'A-ha',
    title: 'Take On Me',
    year: 1985,
    positions: [34, 20, 11, 6, 2],
  },
  {
    artist: 'Madonna',
    title: 'Into The Groove',
    year: 1985,
    positions: [28, 21, 16, 10, 7],
  },
  {
    artist: 'TLC',
    title: 'Waterfalls',
    year: 1995,
    positions: [15, 8, 5, 3, 1],
  },
]

export const yearShuffleDemoRounds: YearShuffleRound[] = [
  {
    entries: [
      { artist: 'The Police', title: 'Every Breath You Take', year: 1983 },
      { artist: 'Cyndi Lauper', title: 'Girls Just Want To Have Fun', year: 1984 },
      { artist: 'Tears For Fears', title: 'Everybody Wants To Rule The World', year: 1985 },
      { artist: 'Peter Gabriel', title: 'Sledgehammer', year: 1986 },
    ],
  },
  {
    entries: [
      { artist: 'Marvin Gaye', title: 'I Heard It Through The Grapevine', year: 1968 },
      { artist: 'The Jackson 5', title: 'I Want You Back', year: 1969 },
      { artist: 'The Temptations', title: 'Ball Of Confusion', year: 1970 },
      { artist: 'Don McLean', title: 'American Pie', year: 1971 },
    ],
  },
]

export const videoTimeMachineDemoRounds: VideoMetadataRecord[] = [
  {
    artist: 'Paula Abdul',
    title: 'Straight Up',
    year: 1989,
    thumbnail: '',
  },
  {
    artist: 'George Michael',
    title: 'Faith',
    year: 1987,
    thumbnail: '',
  },
  {
    artist: 'Whitney Houston',
    title: 'How Will I Know',
    year: 1986,
    thumbnail: '',
  },
]

export const guessPeakDemoRounds: GuessPeakRound[] = [
  {
    artist: 'Toto',
    title: 'Africa',
    year: 1983,
    choices: [1, 2, 4, 6],
    correct: 1,
  },
  {
    artist: 'The Human League',
    title: 'Don’t You Want Me',
    year: 1982,
    choices: [1, 3, 5, 8],
    correct: 1,
  },
  {
    artist: 'Janet Jackson',
    title: 'Escapade',
    year: 1990,
    choices: [1, 2, 4, 7],
    correct: 1,
  },
]

