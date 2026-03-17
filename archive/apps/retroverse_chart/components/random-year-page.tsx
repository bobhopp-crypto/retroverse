'use client'

import { useMemo } from 'react'
import { ArrowLeft, Shuffle } from 'lucide-react'
import { Song, RandomYearData } from '@/lib/types'
import { cn } from '@/lib/utils'

interface RandomYearPageProps {
  year: number
  songs: Song[]
  onBack: () => void
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
  onNewRandomYear: () => void
}

function SectionCard({ 
  title, 
  children,
  className,
}: { 
  title: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn("bg-card rounded-2xl p-4 shadow-md border border-border/50", className)}>
      <h3 className="font-bold text-card-foreground mb-3 text-sm uppercase tracking-wide">
        {title}
      </h3>
      {children}
    </div>
  )
}

function CompactSongRow({
  song,
  extra,
  onClick,
}: {
  song: Song
  extra?: string
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="flex items-center gap-3 py-2 px-2 rounded-lg cursor-pointer hover:bg-muted/60 active:bg-muted transition-colors"
    >
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-foreground truncate">{song.title}</p>
        <p className="text-xs text-muted-foreground truncate">{song.artist}</p>
      </div>
      {extra && (
        <span className="text-xs font-medium text-primary tabular-nums flex-shrink-0">
          {extra}
        </span>
      )}
    </div>
  )
}

function calculateRandomYearData(songs: Song[], year: number): RandomYearData {
  const yearSongs = songs.filter(song => song.year === year)

  // Top songs (by peak position)
  const topSongs = yearSongs
    .slice()
    .sort((a, b) => {
      if (a.peak !== b.peak) return a.peak - b.peak
      return b.weeks - a.weeks
    })
    .slice(0, 10)

  // Biggest hits (by weeks on chart)
  const biggestHits = yearSongs
    .slice()
    .sort((a, b) => b.weeks - a.weeks)
    .slice(0, 10)

  // Artists with multiple hits
  const artistSongsMap = new Map<string, Song[]>()
  yearSongs.forEach(song => {
    const existing = artistSongsMap.get(song.artist) || []
    existing.push(song)
    artistSongsMap.set(song.artist, existing)
  })
  const artistsWithMultipleHits = Array.from(artistSongsMap.entries())
    .filter(([, songs]) => songs.length >= 2)
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, 10)
    .map(([artist, songs]) => ({ artist, songs }))

  // Longest chart runs
  const longestChartRuns = yearSongs
    .slice()
    .sort((a, b) => b.weeks - a.weeks)
    .slice(0, 10)

  return {
    year,
    topSongs,
    biggestHits,
    artistsWithMultipleHits,
    longestChartRuns,
  }
}

export function RandomYearPage({
  year,
  songs,
  onBack,
  onSongSelect,
  onArtistClick,
  onNewRandomYear,
}: RandomYearPageProps) {
  const yearData = useMemo(() => calculateRandomYearData(songs, year), [songs, year])

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
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-foreground">Year: {year}</h2>
        </div>
        <button
          onClick={onNewRandomYear}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium",
            "bg-retro-coral text-foreground hover:opacity-90 active:scale-95 transition-all"
          )}
        >
          <Shuffle className="w-4 h-4" />
          <span>New Year</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto max-h-[calc(100vh-140px)] space-y-4 pb-4">
        {/* Top Songs */}
        <SectionCard title="Top Songs">
          <div className="space-y-0.5">
            {yearData.topSongs.map((song, index) => (
              <div key={`${song.title}-${song.artist}-${index}`} className="flex items-center gap-2">
                <span className={cn(
                  "w-6 text-right font-bold tabular-nums text-sm",
                  index === 0 ? "text-badge-gold" : "text-muted-foreground"
                )}>
                  {index + 1}
                </span>
                <div className="flex-1">
                  <CompactSongRow
                    song={song}
                    extra={song.peak === 1 ? '#1' : `#${song.peak}`}
                    onClick={() => onSongSelect(song)}
                  />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        {/* Biggest Hits (by weeks) */}
        <SectionCard title="Biggest Hits">
          <div className="space-y-0.5">
            {yearData.biggestHits.map((song, index) => (
              <CompactSongRow
                key={`${song.title}-${song.artist}-${index}`}
                song={song}
                extra={`${song.weeks} wks`}
                onClick={() => onSongSelect(song)}
              />
            ))}
          </div>
        </SectionCard>

        {/* Artists with Multiple Hits */}
        {yearData.artistsWithMultipleHits.length > 0 && (
          <SectionCard title="Artists with Multiple Hits">
            <div className="space-y-3">
              {yearData.artistsWithMultipleHits.map(({ artist, songs: artistSongs }) => (
                <div key={artist}>
                  <button
                    onClick={() => onArtistClick(artist)}
                    className="font-semibold text-sm text-primary hover:underline mb-1"
                  >
                    {artist} ({artistSongs.length} songs)
                  </button>
                  <div className="pl-3 border-l-2 border-muted space-y-0.5">
                    {artistSongs.slice(0, 5).map((song, index) => (
                      <CompactSongRow
                        key={`${song.title}-${index}`}
                        song={song}
                        extra={`#${song.peak}`}
                        onClick={() => onSongSelect(song)}
                      />
                    ))}
                    {artistSongs.length > 5 && (
                      <p className="text-xs text-muted-foreground px-2 py-1">
                        +{artistSongs.length - 5} more songs
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        )}

        {/* Songs with Long Chart Runs */}
        <SectionCard title="Songs with Long Chart Runs">
          <div className="space-y-0.5">
            {yearData.longestChartRuns.map((song, index) => (
              <CompactSongRow
                key={`${song.title}-${song.artist}-${index}`}
                song={song}
                extra={`${song.weeks} wks`}
                onClick={() => onSongSelect(song)}
              />
            ))}
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
