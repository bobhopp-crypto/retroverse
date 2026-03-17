'use client'

import { memo, useState, useMemo, useRef, useEffect, useCallback } from 'react'
import { Song } from '@/lib/types'
import { SongCard } from './song-card'

interface SongListProps {
  songs: Song[]
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
}

const MemoizedSongCard = memo(SongCard)

const ITEM_HEIGHT = 112 // Approximate height of each card with gap
const BUFFER_SIZE = 5 // Number of extra items to render above/below viewport

export function SongList({ songs, onSongSelect, onArtistClick }: SongListProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [containerHeight, setContainerHeight] = useState(600)

  // Update container height on mount and resize
  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.clientHeight || 600)
      }
    }
    updateHeight()
    window.addEventListener('resize', updateHeight)
    return () => window.removeEventListener('resize', updateHeight)
  }, [])

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  // Calculate visible range
  const { startIndex, endIndex, visibleSongs, offsetY } = useMemo(() => {
    // For small lists, don't virtualize
    if (songs.length <= 50) {
      return {
        startIndex: 0,
        endIndex: songs.length,
        visibleSongs: songs,
        offsetY: 0,
      }
    }

    const start = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_SIZE)
    const visibleCount = Math.ceil(containerHeight / ITEM_HEIGHT) + BUFFER_SIZE * 2
    const end = Math.min(songs.length, start + visibleCount)

    return {
      startIndex: start,
      endIndex: end,
      visibleSongs: songs.slice(start, end),
      offsetY: start * ITEM_HEIGHT,
    }
  }, [songs, scrollTop, containerHeight])

  if (songs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
          <span className="text-2xl" aria-hidden="true">🎵</span>
        </div>
        <p className="text-muted-foreground text-lg">No songs found</p>
        <p className="text-muted-foreground text-sm mt-1">Try a different search or filter</p>
      </div>
    )
  }

  // For small lists, render normally
  if (songs.length <= 50) {
    return (
      <div className="song-list-container flex flex-col gap-3 max-w-full overflow-hidden">
        {songs.map((song, index) => (
          <MemoizedSongCard
            key={`${song.title}-${song.artist}-${song.year}-${index}`}
            song={song}
            onSelect={onSongSelect}
            onArtistClick={onArtistClick}
            rank={index + 1}
          />
        ))}
      </div>
    )
  }

  // For large lists, use virtualization
  const totalHeight = songs.length * ITEM_HEIGHT

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="overflow-y-auto max-h-[calc(100vh-320px)]"
      style={{ WebkitOverflowScrolling: 'touch' }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            position: 'absolute',
            top: offsetY,
            left: 0,
            right: 0,
          }}
          className="song-list-container flex flex-col gap-3 max-w-full overflow-hidden"
        >
          {visibleSongs.map((song, index) => (
            <MemoizedSongCard
              key={`${song.title}-${song.artist}-${song.year}-${startIndex + index}`}
              song={song}
              onSelect={onSongSelect}
              onArtistClick={onArtistClick}
              rank={startIndex + index + 1}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
