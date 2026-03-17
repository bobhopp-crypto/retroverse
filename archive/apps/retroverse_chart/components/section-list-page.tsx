'use client'

import { memo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Song } from '@/lib/types'
import { cn } from '@/lib/utils'

interface SectionListPageProps {
  title: string
  songs: Song[]
  onBack: () => void
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
}

function CompactSongRow({
  song,
  rank,
  onClick,
  onArtistClick,
}: {
  song: Song
  rank: number
  onClick: () => void
  onArtistClick: (artist: string) => void
}) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 py-2.5 px-3 cursor-pointer transition-colors",
        "hover:bg-muted/60 active:bg-muted",
        rank % 2 === 0 ? "bg-muted/20" : "bg-transparent",
        rank <= 3 && "bg-badge-gold/5"
      )}
    >
      <span className={cn(
        "rank-number w-6 flex-shrink-0 text-center font-black tabular-nums",
        rank === 1 ? "text-badge-gold text-lg" : rank <= 3 ? "text-foreground" : "text-muted-foreground"
      )}>
        {rank}
      </span>
      <div className="flex-1 min-w-0 overflow-hidden">
        <p className="song-title font-semibold text-sm text-foreground">{song.title}</p>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onArtistClick(song.artist)
          }}
          className="artist-name text-xs text-muted-foreground hover:text-primary hover:underline block text-left w-full"
        >
          {song.artist}
        </button>
      </div>
      <div className="flex-shrink-0 text-right">
        <p className={cn(
          "text-sm font-bold tabular-nums",
          song.peak === 1 ? "text-badge-gold" : "text-foreground"
        )}>
          #{song.peak}
        </p>
        <p className="text-[10px] text-muted-foreground">{song.weeks} wks</p>
      </div>
    </div>
  )
}

const MemoizedCompactSongRow = memo(CompactSongRow)

export function SectionListPage({
  title,
  songs,
  onBack,
  onSongSelect,
  onArtistClick,
}: SectionListPageProps) {
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
        <div>
          <h2 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
            {title}
          </h2>
          <p className="text-sm text-muted-foreground">{songs.length} songs</p>
        </div>
      </div>

      {/* Song List */}
      <div className="bg-card rounded-xl shadow-md border border-border overflow-hidden flex-1">
        <div className="max-h-[calc(100vh-180px)] overflow-y-auto">
          {songs.map((song, index) => (
            <MemoizedCompactSongRow
              key={`${song.title}-${song.artist}-${song.year}-${index}`}
              song={song}
              rank={index + 1}
              onClick={() => onSongSelect(song)}
              onArtistClick={onArtistClick}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
