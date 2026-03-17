'use client'

import { Song } from '@/lib/types'
import { cn } from '@/lib/utils'

interface ChartRowProps {
  position: number
  song: Song
  lastWeek: number | null
  weeksOnChart: number
  peak: number
  movement: 'up' | 'down' | 'same' | 'new' | 're'
  onSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
}

function MovementIndicator({ movement }: { movement: ChartRowProps['movement'] }) {
  if (movement === 'new') {
    return <span className="text-[10px] font-black tracking-tight text-retro-teal">NEW</span>
  }
  if (movement === 're') {
    return <span className="text-[10px] font-black tracking-tight text-retro-mustard">RE</span>
  }
  if (movement === 'up') {
    return <span className="text-sm font-black text-green-600">&#9650;</span>
  }
  if (movement === 'down') {
    return <span className="text-sm font-black text-retro-coral">&#9660;</span>
  }
  return <span className="text-sm text-muted-foreground/50">=</span>
}

export function ChartRow({
  position,
  song,
  lastWeek,
  weeksOnChart,
  peak,
  movement,
  onSelect,
  onArtistClick,
}: ChartRowProps) {
  return (
    <div
      onClick={() => onSelect(song)}
      className={cn(
        "flex items-center py-1.5 px-2 cursor-pointer transition-colors",
        "hover:bg-muted/60 active:bg-muted",
        position % 2 === 0 ? "bg-muted/20" : "bg-transparent",
        position === 1 && "bg-badge-gold/15"
      )}
    >
      {/* Position - Classic Billboard style */}
      <div className="w-9 flex-shrink-0 text-center">
        <span className={cn(
          "font-black tabular-nums",
          position === 1 && "text-badge-gold text-xl",
          position <= 10 && position > 1 && "text-foreground text-lg",
          position > 10 && position <= 40 && "text-foreground text-base",
          position > 40 && "text-muted-foreground text-base"
        )}>
          {position}
        </span>
      </div>

      {/* Movement Indicator */}
      <div className="w-7 flex-shrink-0 flex items-center justify-center">
        <MovementIndicator movement={movement} />
      </div>

      {/* Song & Artist - Magazine style inline */}
      <div className="flex-1 min-w-0 flex items-baseline gap-1.5 overflow-hidden">
        <span className="song-title font-bold text-sm text-foreground">
          {song.title}
        </span>
        <span className="text-muted-foreground text-sm flex-shrink-0">-</span>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onArtistClick(song.artist)
          }}
          className="artist-name text-sm text-muted-foreground hover:text-primary hover:underline min-w-0"
        >
          {song.artist}
        </button>
      </div>

      {/* Stats - Compact magazine style */}
      <div className="flex-shrink-0 flex items-center gap-3 text-[11px] tabular-nums">
        <div className="text-center w-8">
          <div className="text-muted-foreground/70 leading-tight">LW</div>
          <div className="font-semibold text-foreground">{lastWeek ?? '-'}</div>
        </div>
        <div className="text-center w-8">
          <div className="text-muted-foreground/70 leading-tight">PK</div>
          <div className={cn(
            "font-semibold",
            peak === 1 ? "text-badge-gold" : "text-foreground"
          )}>{peak}</div>
        </div>
        <div className="text-center w-8">
          <div className="text-muted-foreground/70 leading-tight">WK</div>
          <div className="font-semibold text-foreground">{weeksOnChart}</div>
        </div>
      </div>
    </div>
  )
}
