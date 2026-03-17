'use client'

import { ArrowLeft } from 'lucide-react'
import { ArtistData, Song } from '@/lib/types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from 'recharts'
import { cn } from '@/lib/utils'

interface ArtistPageProps {
  artist: ArtistData
  onBack: () => void
  onSongSelect: (song: Song) => void
}

const barColors = [
  'var(--retro-teal)',
  'var(--retro-coral)',
  'var(--retro-mustard)',
  'var(--retro-mint)',
  'var(--retro-aqua)',
]

function StatBox({
  value,
  label,
  highlight = false,
}: {
  value: string | number
  label: string
  highlight?: boolean
}) {
  return (
    <div className={cn(
      "rounded-xl p-3 text-center",
      highlight ? "bg-badge-gold/20" : "bg-muted"
    )}>
      <p className="text-xl font-bold text-card-foreground">{value}</p>
      <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
    </div>
  )
}

function CompactSongRow({
  song,
  onClick,
}: {
  song: Song
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="flex items-center gap-3 py-2 px-2 rounded-lg cursor-pointer hover:bg-muted/60 active:bg-muted transition-colors border-b border-border/20 last:border-b-0"
    >
      <div className="w-8 text-center">
        <span className={cn(
          "font-bold text-sm",
          song.peak === 1 ? "text-badge-gold" : song.peak <= 10 ? "text-foreground" : "text-muted-foreground"
        )}>
          #{song.peak}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-foreground truncate">{song.title}</p>
        <p className="text-xs text-muted-foreground">{song.year}</p>
      </div>
      <span className="text-xs text-muted-foreground tabular-nums flex-shrink-0">
        {song.weeks} wks
      </span>
    </div>
  )
}

export function ArtistPage({ artist, onBack, onSongSelect }: ArtistPageProps) {
  const decadeData = Object.entries(artist.songsByDecade)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([decade, count]) => ({
      decade,
      songs: count,
    }))

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
        <h2 className="text-lg font-semibold text-foreground">Artist</h2>
      </div>

      {/* Artist Info Card */}
      <div className="bg-card rounded-2xl p-5 shadow-md border border-border/50 mb-4">
        <h1 className="text-xl font-bold text-card-foreground leading-tight text-balance mb-4">
          {artist.name}
        </h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          <StatBox value={artist.totalSongs} label="Total Entries" />
          <StatBox value={artist.top10Hits} label="Top 10 Hits" />
          <StatBox value={artist.numberOneHits} label="#1 Hits" highlight={artist.numberOneHits > 0} />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <StatBox 
            value={`${artist.longestChartRun} wks`} 
            label="Longest Run" 
          />
          <StatBox 
            value={artist.averagePeak > 0 ? `#${artist.averagePeak.toFixed(0)}` : '-'} 
            label="Avg Peak" 
          />
        </div>
      </div>

      {/* Songs by Decade Chart */}
      {decadeData.length > 0 && (
        <div className="bg-card rounded-2xl p-4 shadow-md border border-border/50 mb-4">
          <h3 className="text-sm font-bold text-card-foreground mb-3 uppercase tracking-wide">
            Decade Breakdown
          </h3>
          
          {/* Visual Bar Representation */}
          <div className="space-y-2 mb-3">
            {decadeData.map((item, index) => {
              const maxCount = Math.max(...decadeData.map(d => d.songs))
              const widthPercent = (item.songs / maxCount) * 100
              return (
                <div key={item.decade} className="flex items-center gap-2">
                  <span className="w-10 text-xs font-medium text-muted-foreground">
                    {item.decade}
                  </span>
                  <div className="flex-1 h-5 bg-muted rounded overflow-hidden">
                    <div
                      className="h-full rounded transition-all"
                      style={{
                        width: `${widthPercent}%`,
                        backgroundColor: barColors[index % barColors.length],
                      }}
                    />
                  </div>
                  <span className="w-6 text-xs font-bold text-foreground tabular-nums text-right">
                    {item.songs}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Small chart for larger datasets */}
          {decadeData.length > 3 && (
            <div className="h-[120px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={decadeData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                  <XAxis
                    dataKey="decade"
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--border)' }}
                    className="fill-muted-foreground"
                  />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={{ stroke: 'var(--border)' }}
                    className="fill-muted-foreground"
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--card)',
                      border: '1px solid var(--border)',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                    formatter={(value: number) => [value, 'Songs']}
                  />
                  <Bar dataKey="songs" radius={[4, 4, 0, 0]}>
                    {decadeData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={barColors[index % barColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Artist's Songs */}
      <div className="bg-card rounded-2xl shadow-md border border-border/50 flex-1 overflow-hidden">
        <div className="p-4 pb-2 border-b border-border/30">
          <h3 className="text-sm font-bold text-foreground uppercase tracking-wide">
            Chart History ({artist.songs.length})
          </h3>
        </div>
        <div className="max-h-[300px] overflow-y-auto px-2 py-1">
          {artist.songs.map((song, index) => (
            <CompactSongRow
              key={`${song.title}-${song.year}-${index}`}
              song={song}
              onClick={() => onSongSelect(song)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
