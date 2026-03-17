'use client'

import { useMemo } from 'react'
import { ChevronRight } from 'lucide-react'
import { Song } from '@/lib/types'

const DECADE_CONFIG = [
  { id: '1950s', label: '1950s', start: 1950, end: 1960, bg: '#f7efe2' },
  { id: '1960s', label: '1960s', start: 1960, end: 1970, bg: '#d8f3f1' },
  { id: '1970s', label: '1970s', start: 1970, end: 1980, bg: '#f7e6c4' },
  { id: '1980s', label: '1980s', start: 1980, end: 1990, bg: '#f4d7ff' },
  { id: '1990s', label: '1990s', start: 1990, end: 2000, bg: '#e6ddff' },
  { id: '2000s', label: '2000s', start: 2000, end: 2010, bg: '#e6edf3' },
] as const

interface DecadeExplorerProps {
  songs: Song[]
  onDecadeSelect: (title: string, songs: Song[]) => void
}

export function DecadeExplorer({ songs, onDecadeSelect }: DecadeExplorerProps) {
  const songsByDecade = useMemo(() => {
    const map: Record<string, Song[]> = {}
    for (const { start, end } of DECADE_CONFIG) {
      map[`${start}-${end}`] = songs
        .filter(s => s.year >= start && s.year < end)
        .sort((a, b) => a.peak - b.peak || b.weeks - a.weeks)
    }
    return map
  }, [songs])

  return (
    <div className="space-y-0">
      {DECADE_CONFIG.map(({ id, label, start, end, bg }) => {
        const decadeSongs = songsByDecade[`${start}-${end}`] ?? []
        const previewSongs = decadeSongs.slice(0, 3)

        return (
          <button
            key={id}
            onClick={() => onDecadeSelect(`${label} Hits`, decadeSongs)}
            className="decade-card w-full text-left rounded-2xl p-[18px] mb-3.5 last:mb-0 border border-border/30 active:scale-[0.99] transition-all"
            style={{ backgroundColor: bg }}
          >
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <h3 className="text-lg font-black text-foreground tracking-tight">
                  {label}
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Explore chart hits from the {label.toLowerCase()}
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0 ml-2" />
            </div>

            {previewSongs.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border/20 space-y-1.5">
                {previewSongs.map((song, i) => (
                  <div
                    key={`${song.title}-${song.artist}-${song.year}`}
                    className="flex items-center gap-2 text-sm min-w-0 overflow-hidden"
                  >
                    <span className="text-xs font-bold text-muted-foreground tabular-nums w-4 flex-shrink-0">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="song-title font-medium text-foreground block truncate">
                        {song.title}
                      </span>
                      <span className="text-xs text-muted-foreground block truncate">
                        {song.artist}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {decadeSongs.length > 0 && (
              <p className="text-[10px] text-muted-foreground mt-2">
                {decadeSongs.length.toLocaleString()} songs
              </p>
            )}
          </button>
        )
      })}
    </div>
  )
}
