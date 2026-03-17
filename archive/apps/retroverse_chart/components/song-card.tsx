'use client'

import { Song } from '@/lib/types'

interface SongCardProps {
  song: Song
  onSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
  rank?: number
}

export function SongCard({ song, onSelect, onArtistClick, rank }: SongCardProps) {
  return (
    <div
      onClick={() => onSelect(song)}
      className="song-card relative bg-card rounded-2xl p-4 pt-5 shadow-md hover:shadow-lg transition-all cursor-pointer border border-border/50 active:scale-[0.98]"
    >
      {rank !== undefined && (
        <div className="rank-badge tabular-nums">
          {rank}
        </div>
      )}
      <div className="flex flex-col min-w-0">
        <h3 className="song-title font-semibold text-[1.05rem] text-card-foreground leading-tight pr-8">
          {song.title}
        </h3>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onArtistClick(song.artist)
          }}
          className="artist-name hover:text-primary hover:underline text-left block w-full mt-0.5"
        >
          {song.artist}
        </button>
      </div>
      <div className="song-meta mt-3 text-sm text-muted-foreground">
        Peak #{song.peak} • {song.weeks} weeks
      </div>
    </div>
  )
}
