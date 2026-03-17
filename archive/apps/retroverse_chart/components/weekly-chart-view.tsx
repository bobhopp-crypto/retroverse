'use client'

import { useState, useMemo, memo } from 'react'
import { ArrowLeft, TrendingUp, Sparkles } from 'lucide-react'
import { Song, WeeklyChartEntry } from '@/lib/types'
import { ChartRow } from './chart-row'
import { cn } from '@/lib/utils'

interface WeeklyChartViewProps {
  weekOf: string
  songs: Song[]
  onBack: () => void
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
}

type ChartFilter = 'top10' | 'top40' | 'full'

interface WeekSummary {
  numberOne: WeeklyChartEntry | null
  biggestJump: { entry: WeeklyChartEntry; jump: number } | null
  newEntries: number
}

function generateWeeklyChart(songs: Song[], weekOf: string): WeeklyChartEntry[] {
  // Simulate a weekly chart based on the songs in our dataset
  // We'll create a chart by sampling songs from the same year and nearby years
  const weekDate = new Date(weekOf)
  const weekYear = weekDate.getFullYear()
  
  // Filter songs that could plausibly be on the chart for this week
  const eligibleSongs = songs.filter(song => {
    // Songs from this year and last year are eligible
    return song.year === weekYear || song.year === weekYear - 1 || song.year === weekYear + 1
  })

  // If not enough songs, include songs from nearby years
  let chartSongs = eligibleSongs
  if (chartSongs.length < 100) {
    chartSongs = songs.filter(song => 
      Math.abs(song.year - weekYear) <= 3
    )
  }

  // Sort by peak position (better peak = higher priority) and weeks on chart
  chartSongs = chartSongs
    .slice()
    .sort((a, b) => {
      // Primary: peak position (lower is better)
      if (a.peak !== b.peak) return a.peak - b.peak
      // Secondary: weeks on chart (more weeks = more established)
      return b.weeks - a.weeks
    })
    .slice(0, 100)

  // Create chart entries with simulated positions
  return chartSongs.map((song, index): WeeklyChartEntry => {
    const position = index + 1
    
    // Simulate last week position based on chart run
    const weekIndex = Math.floor(song.run.length / 2)
    const currentPos = song.run[weekIndex] || position
    const lastWeekPos = song.run[Math.max(0, weekIndex - 1)] || null
    
    // Determine movement
    let movement: WeeklyChartEntry['movement'] = 'same'
    if (lastWeekPos === null || weekIndex === 0) {
      movement = 'new'
    } else if (position < lastWeekPos) {
      movement = 'up'
    } else if (position > lastWeekPos) {
      movement = 'down'
    }

    // Simulate re-entries for songs that had gaps
    if (song.run.length > 10 && Math.random() > 0.9) {
      movement = 're'
    }

    return {
      position,
      song,
      lastWeek: movement === 'new' || movement === 're' ? null : lastWeekPos,
      weeksOnChart: Math.min(song.weeks, weekIndex + 1),
      peak: Math.min(position, song.peak),
      movement,
    }
  })
}

const MemoizedChartRow = memo(ChartRow)

function SummaryCard({ 
  icon, 
  label, 
  value, 
  subValue,
  highlight = false 
}: { 
  icon: React.ReactNode
  label: string 
  value: string 
  subValue?: string
  highlight?: boolean 
}) {
  return (
    <div className={cn(
      "flex items-center gap-2 px-3 py-2 rounded-xl",
      highlight ? "bg-badge-gold/20" : "bg-muted/60"
    )}>
      <div className="text-muted-foreground">{icon}</div>
      <div className="min-w-0 flex-1">
        <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
        <p className="font-bold text-sm text-foreground truncate">{value}</p>
        {subValue && <p className="text-xs text-muted-foreground truncate">{subValue}</p>}
      </div>
    </div>
  )
}

export function WeeklyChartView({
  weekOf,
  songs,
  onBack,
  onSongSelect,
  onArtistClick,
}: WeeklyChartViewProps) {
  const [filter, setFilter] = useState<ChartFilter>('full')

  const chartEntries = useMemo(() => {
    return generateWeeklyChart(songs, weekOf)
  }, [songs, weekOf])

  const weekSummary = useMemo<WeekSummary>(() => {
    const numberOne = chartEntries[0] || null
    
    // Find biggest jump
    let biggestJump: WeekSummary['biggestJump'] = null
    for (const entry of chartEntries) {
      if (entry.lastWeek !== null && entry.movement === 'up') {
        const jump = entry.lastWeek - entry.position
        if (!biggestJump || jump > biggestJump.jump) {
          biggestJump = { entry, jump }
        }
      }
    }

    // Count new entries
    const newEntries = chartEntries.filter(e => e.movement === 'new' || e.movement === 're').length

    return { numberOne, biggestJump, newEntries }
  }, [chartEntries])

  const filteredEntries = useMemo(() => {
    switch (filter) {
      case 'top10':
        return chartEntries.slice(0, 10)
      case 'top40':
        return chartEntries.slice(0, 40)
      default:
        return chartEntries
    }
  }, [chartEntries, filter])

  const formatWeekDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <button
          onClick={onBack}
          className="p-2 -ml-2 rounded-xl hover:bg-muted active:scale-95 transition-all"
          aria-label="Go back"
        >
          <ArrowLeft className="w-6 h-6 text-foreground" />
        </button>
        <div>
          <h2 className="text-lg font-bold text-foreground">Billboard Hot 100</h2>
          <p className="text-sm text-muted-foreground">
            Week of {formatWeekDate(weekOf)}
          </p>
        </div>
      </div>

      {/* Summary Panel */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {weekSummary.numberOne && (
          <SummaryCard
            icon={<span className="text-badge-gold font-black text-sm">#1</span>}
            label="#1 Song"
            value={weekSummary.numberOne.song.title}
            subValue={weekSummary.numberOne.song.artist}
            highlight
          />
        )}
        {weekSummary.biggestJump && (
          <SummaryCard
            icon={<TrendingUp className="w-4 h-4 text-green-600" />}
            label="Biggest Jump"
            value={`+${weekSummary.biggestJump.jump}`}
            subValue={weekSummary.biggestJump.entry.song.title}
          />
        )}
        <SummaryCard
          icon={<Sparkles className="w-4 h-4 text-retro-teal" />}
          label="New Entries"
          value={String(weekSummary.newEntries)}
        />
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-3">
        {(['top10', 'top40', 'full'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-3 py-1.5 rounded-full text-sm font-medium transition-all",
              "active:scale-95",
              filter === f
                ? "bg-primary text-primary-foreground shadow-md"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            )}
          >
            {f === 'top10' && 'Top 10'}
            {f === 'top40' && 'Top 40'}
            {f === 'full' && 'Hot 100'}
          </button>
        ))}
      </div>

      {/* Chart - Magazine Style */}
      <div className="bg-card rounded-xl shadow-md border border-border overflow-hidden flex-1">
        {/* Chart Header */}
        <div className="flex items-center px-2 py-1.5 bg-primary/10 border-b border-border text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
          <div className="w-9 text-center">TW</div>
          <div className="w-7 text-center"></div>
          <div className="flex-1">Title - Artist</div>
          <div className="w-8 text-center">LW</div>
          <div className="w-8 text-center">PK</div>
          <div className="w-8 text-center">WK</div>
        </div>
        <div className="max-h-[calc(100vh-380px)] overflow-y-auto">
          {filteredEntries.map((entry) => (
            <MemoizedChartRow
              key={`${entry.song.title}-${entry.song.artist}-${entry.position}`}
              position={entry.position}
              song={entry.song}
              lastWeek={entry.lastWeek}
              weeksOnChart={entry.weeksOnChart}
              peak={entry.peak}
              movement={entry.movement}
              onSelect={onSongSelect}
              onArtistClick={onArtistClick}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
