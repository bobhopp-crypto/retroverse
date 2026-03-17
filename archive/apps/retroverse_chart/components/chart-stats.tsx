'use client'

import { useMemo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Song, ChartStats } from '@/lib/types'
import { cn } from '@/lib/utils'

interface ChartStatsPageProps {
  songs: Song[]
  onBack: () => void
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
}

function StatSection({ 
  title, 
  children 
}: { 
  title: string
  children: React.ReactNode 
}) {
  return (
    <div className="bg-card rounded-2xl p-4 shadow-md border border-border/50 mb-4">
      <h3 className="font-bold text-card-foreground mb-3 text-sm uppercase tracking-wide">
        {title}
      </h3>
      <div className="space-y-0.5">{children}</div>
    </div>
  )
}

function StatRow({
  rank,
  primary,
  secondary,
  value,
  onClick,
  highlight = false,
}: {
  rank: number
  primary: string
  secondary?: string
  value: string | number
  onClick?: () => void
  highlight?: boolean
}) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 py-2 px-2 rounded-lg transition-colors",
        onClick && "cursor-pointer hover:bg-muted/60 active:bg-muted",
        highlight && "bg-badge-gold/10"
      )}
    >
      <span className="w-6 text-right font-bold tabular-nums text-muted-foreground text-sm">
        {rank}
      </span>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-foreground truncate">{primary}</p>
        {secondary && (
          <p className="text-xs text-muted-foreground truncate">{secondary}</p>
        )}
      </div>
      <span className="font-bold text-sm text-primary tabular-nums">{value}</span>
    </div>
  )
}

function calculateChartStats(songs: Song[]): ChartStats {
  // Most weeks on chart (Top 20)
  const mostWeeksOnChart = songs
    .slice()
    .sort((a, b) => b.weeks - a.weeks)
    .slice(0, 20)
    .map(song => ({ song, weeks: song.weeks }))

  // Biggest climbs (largest jumps in position)
  const biggestClimbs = songs
    .filter(song => song.run.length >= 2)
    .map(song => {
      let maxJump = 0
      let fromPos = 0
      let toPos = 0
      for (let i = 1; i < song.run.length; i++) {
        const jump = song.run[i - 1] - song.run[i] // Positive jump = moving up
        if (jump > maxJump) {
          maxJump = jump
          fromPos = song.run[i - 1]
          toPos = song.run[i]
        }
      }
      return { song, jump: maxJump, from: fromPos, to: toPos }
    })
    .filter(item => item.jump > 0)
    .sort((a, b) => b.jump - a.jump)
    .slice(0, 20)

  // Longest #1 runs
  const longestNumberOneRuns = songs
    .filter(song => song.peak === 1)
    .map(song => {
      let maxConsecutive = 0
      let currentStreak = 0
      for (const position of song.run) {
        if (position === 1) {
          currentStreak++
          maxConsecutive = Math.max(maxConsecutive, currentStreak)
        } else {
          currentStreak = 0
        }
      }
      return { song, consecutiveWeeks: maxConsecutive }
    })
    .filter(item => item.consecutiveWeeks > 0)
    .sort((a, b) => b.consecutiveWeeks - a.consecutiveWeeks)
    .slice(0, 20)

  // Artists with most Top 10 hits
  const artistTop10Map = new Map<string, number>()
  songs.forEach(song => {
    if (song.peak <= 10) {
      artistTop10Map.set(song.artist, (artistTop10Map.get(song.artist) || 0) + 1)
    }
  })
  const artistsWithMostTop10 = Array.from(artistTop10Map.entries())
    .map(([artist, count]) => ({ artist, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20)

  // Artists with most #1 hits
  const artistNumberOneMap = new Map<string, number>()
  songs.forEach(song => {
    if (song.peak === 1) {
      artistNumberOneMap.set(song.artist, (artistNumberOneMap.get(song.artist) || 0) + 1)
    }
  })
  const artistsWithMostNumberOnes = Array.from(artistNumberOneMap.entries())
    .map(([artist, count]) => ({ artist, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20)

  return {
    mostWeeksOnChart,
    biggestClimbs,
    longestNumberOneRuns,
    artistsWithMostTop10,
    artistsWithMostNumberOnes,
  }
}

export function ChartStatsPage({
  songs,
  onBack,
  onSongSelect,
  onArtistClick,
}: ChartStatsPageProps) {
  const stats = useMemo(() => calculateChartStats(songs), [songs])

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="p-2 -ml-2 rounded-xl hover:bg-muted active:scale-95 transition-all"
          aria-label="Go back"
        >
          <ArrowLeft className="w-6 h-6 text-foreground" />
        </button>
        <h2 className="text-xl font-bold text-foreground">Chart Stats</h2>
      </div>

      <div className="flex-1 overflow-y-auto max-h-[calc(100vh-140px)] space-y-4 pb-4">
        {/* Most Weeks on Chart */}
        <StatSection title="Most Weeks on Chart">
          {stats.mostWeeksOnChart.map((item, index) => (
            <StatRow
              key={`${item.song.title}-${item.song.artist}`}
              rank={index + 1}
              primary={item.song.title}
              secondary={item.song.artist}
              value={`${item.weeks} wks`}
              onClick={() => onSongSelect(item.song)}
              highlight={index === 0}
            />
          ))}
        </StatSection>

        {/* Biggest Climbs */}
        <StatSection title="Biggest Chart Climbs">
          {stats.biggestClimbs.map((item, index) => (
            <StatRow
              key={`${item.song.title}-${item.song.artist}`}
              rank={index + 1}
              primary={item.song.title}
              secondary={`${item.song.artist} (${item.from} to ${item.to})`}
              value={`+${item.jump}`}
              onClick={() => onSongSelect(item.song)}
              highlight={index === 0}
            />
          ))}
        </StatSection>

        {/* Longest #1 Runs */}
        <StatSection title="Longest #1 Runs">
          {stats.longestNumberOneRuns.map((item, index) => (
            <StatRow
              key={`${item.song.title}-${item.song.artist}`}
              rank={index + 1}
              primary={item.song.title}
              secondary={item.song.artist}
              value={`${item.consecutiveWeeks} wks`}
              onClick={() => onSongSelect(item.song)}
              highlight={index === 0}
            />
          ))}
        </StatSection>

        {/* Artists with Most Top 10 Hits */}
        <StatSection title="Artists with Most Top 10 Hits">
          {stats.artistsWithMostTop10.map((item, index) => (
            <StatRow
              key={item.artist}
              rank={index + 1}
              primary={item.artist}
              value={item.count}
              onClick={() => onArtistClick(item.artist)}
              highlight={index === 0}
            />
          ))}
        </StatSection>

        {/* Artists with Most #1 Hits */}
        <StatSection title="Artists with Most #1 Hits">
          {stats.artistsWithMostNumberOnes.map((item, index) => (
            <StatRow
              key={item.artist}
              rank={index + 1}
              primary={item.artist}
              value={item.count}
              onClick={() => onArtistClick(item.artist)}
              highlight={index === 0}
            />
          ))}
        </StatSection>
      </div>
    </div>
  )
}
