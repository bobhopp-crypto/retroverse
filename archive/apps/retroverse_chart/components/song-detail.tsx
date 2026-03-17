'use client'

import { useMemo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Song } from '@/lib/types'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  ReferenceLine,
  ReferenceDot,
} from 'recharts'
import { cn } from '@/lib/utils'

interface SongDetailProps {
  song: Song
  onBack: () => void
  onArtistClick: (artist: string) => void
}

export function SongDetail({ song, onBack, onArtistClick }: SongDetailProps) {
  const chartData = useMemo(() => {
    return song.run.map((position, week) => ({
      week: week + 1,
      position,
    }))
  }, [song.run])

  const peakWeek = useMemo(() => {
    const peakIndex = song.run.indexOf(song.peak)
    return peakIndex >= 0 ? peakIndex + 1 : 1
  }, [song.run, song.peak])

  const entryPosition = song.run[0] || 100
  const exitPosition = song.run[song.run.length - 1] || 100

  // Use weeks_at_peak from data if available, else compute consecutive weeks at peak
  const weeksAtPeak = useMemo(() => {
    if (song.weeks_at_peak != null) return song.weeks_at_peak
    let maxConsecutive = 0
    let currentStreak = 0
    for (const position of song.run) {
      if (position === song.peak) {
        currentStreak++
        maxConsecutive = Math.max(maxConsecutive, currentStreak)
      } else {
        currentStreak = 0
      }
    }
    return maxConsecutive
  }, [song.run, song.peak, song.weeks_at_peak])

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={onBack}
          className="p-2 -ml-2 rounded-xl hover:bg-muted active:scale-95 transition-all"
          aria-label="Go back"
        >
          <ArrowLeft className="w-6 h-6 text-foreground" />
        </button>
        <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
          Song Details
        </span>
      </div>

      {/* Editorial Title Block */}
      <div className="mb-4 min-w-0">
        <h1 className="song-title text-2xl font-black text-foreground leading-tight text-balance">
          {song.title}
        </h1>
        <div className="flex items-center gap-1.5 mt-1">
          <button
            onClick={() => onArtistClick(song.artist)}
            className="text-base font-medium text-primary hover:underline"
          >
            {song.artist}
          </button>
          <span className="text-muted-foreground">•</span>
          <span className="text-base text-muted-foreground">{song.year}</span>
        </div>
      </div>

      {/* Chart Summary Line */}
      <div className="bg-muted/50 rounded-lg px-3 py-2 mb-3">
        <p className="text-sm text-foreground">
          <span className={cn(
            "font-bold",
            song.peak === 1 && "text-badge-gold"
          )}>
            Peak #{song.peak}
          </span>
          <span className="text-muted-foreground mx-1.5">•</span>
          <span className="font-medium">{song.weeks} Weeks on Chart</span>
          {weeksAtPeak > 0 && song.peak <= 10 && (
            <>
              <span className="text-muted-foreground mx-1.5">•</span>
              <span className="font-medium">{weeksAtPeak} {weeksAtPeak === 1 ? 'Week' : 'Weeks'} at Peak</span>
            </>
          )}
        </p>
      </div>

      {/* Chart Story Line */}
      <div className="text-sm text-muted-foreground mb-4 px-1">
        Entered #{entryPosition} → Peaked Week {song.peak_week ?? peakWeek} → Exited #{exitPosition}
      </div>

      {/* Chart Graph */}
      <div className="bg-card rounded-xl p-4 shadow-sm border border-border/50 flex-1 min-h-[260px]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
            Chart Performance
          </h3>
          {song.peak === 1 && (
            <span className="text-xs font-bold text-badge-gold uppercase tracking-wide">
              #1 Hit
            </span>
          )}
        </div>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
              <XAxis
                dataKey="week"
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={{ stroke: 'var(--border)' }}
                className="fill-muted-foreground"
                label={{ 
                  value: 'Week on Chart', 
                  position: 'bottom', 
                  offset: 0,
                  fontSize: 10,
                  className: 'fill-muted-foreground'
                }}
              />
              <YAxis
                reversed
                domain={[1, 'dataMax']}
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={{ stroke: 'var(--border)' }}
                className="fill-muted-foreground"
                tickFormatter={(value) => `#${value}`}
                width={35}
                label={{ 
                  value: 'Chart Position', 
                  angle: -90, 
                  position: 'insideLeft',
                  offset: 10,
                  fontSize: 10,
                  className: 'fill-muted-foreground'
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                formatter={(value: number) => [`#${value}`, 'Position']}
                labelFormatter={(label) => `Week ${label}`}
              />
              {/* Peak line */}
              <ReferenceLine
                y={song.peak}
                stroke="var(--badge-gold)"
                strokeDasharray="4 4"
                strokeWidth={1.5}
              />
              {/* Peak dot highlight */}
              <ReferenceDot
                x={peakWeek}
                y={song.peak}
                r={7}
                fill="var(--badge-gold)"
                stroke="var(--card)"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="position"
                stroke="var(--primary)"
                strokeWidth={2.5}
                dot={{ fill: 'var(--primary)', strokeWidth: 0, r: 2 }}
                activeDot={{ r: 5, fill: 'var(--primary)' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
