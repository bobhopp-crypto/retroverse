'use client'

import { useMemo, useState, memo } from 'react'
import { Song } from '@/lib/types'
import { cn } from '@/lib/utils'

interface EditorialBrowseProps {
  songs: Song[]
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
  onSectionExpand: (section: string, songs: Song[]) => void
}

interface SectionData {
  id: string
  title: string
  songs: Song[]
}

function SectionTitle({ 
  title, 
  count,
  onExpand 
}: { 
  title: string
  count: number
  onExpand: () => void 
}) {
  return (
    <button
      onClick={onExpand}
      className="section-header w-full flex items-center justify-between mb-3 group text-left"
    >
      <h2 className="section-header-title text-[0.85rem] font-semibold tracking-[0.08em] text-muted-foreground group-hover:text-foreground transition-colors">
        {title}
      </h2>
      <span className="text-xs text-muted-foreground group-hover:text-primary transition-colors">
        {count} ›
      </span>
    </button>
  )
}

function HorizontalSongCard({
  song,
  rank,
  onSelect,
  onArtistClick,
}: {
  song: Song
  rank?: number
  onSelect: () => void
  onArtistClick: (artist: string) => void
}) {
  return (
    <div
      onClick={onSelect}
      className="section-card horizontal-song-card flex-[0_0_75%] min-w-0 bg-card rounded-xl p-3 pt-4 shadow-sm border border-border/50 cursor-pointer hover:shadow-md active:scale-[0.98] transition-all relative"
    >
      {rank !== undefined && (
        <span className={cn(
          "rank-badge absolute top-2 left-2.5 font-bold text-[0.9rem] tabular-nums",
          rank === 1 ? "text-badge-gold" : rank <= 3 ? "text-foreground" : "text-muted-foreground/50"
        )}>
          {rank}
        </span>
      )}
      <p className="song-title font-semibold text-[1.05rem] text-foreground leading-tight pr-6">
        {song.title}
      </p>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onArtistClick(song.artist)
        }}
        className="artist-name text-xs text-muted-foreground hover:text-primary hover:underline mt-0.5 block text-left w-full"
      >
        {song.artist}
      </button>
      <div className="song-meta mt-2 text-[10px] text-muted-foreground">
        Peak #{song.peak} • {song.weeks} wks
      </div>
    </div>
  )
}

const MemoizedHorizontalSongCard = memo(HorizontalSongCard)

function HorizontalScrollSection({
  title,
  songs,
  onSongSelect,
  onArtistClick,
  onExpand,
  showRank = false,
}: {
  title: string
  songs: Song[]
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
  onExpand: () => void
  showRank?: boolean
}) {
  return (
    <section className="section">
      <SectionTitle title={title} count={songs.length} onExpand={onExpand} />
      <div className="horizontal-scroll-section flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 pr-6 scrollbar-hide">
        {songs.slice(0, 6).map((song, index) => (
          <MemoizedHorizontalSongCard
            key={`${song.title}-${song.artist}-${song.year}`}
            song={song}
            rank={showRank ? index + 1 : undefined}
            onSelect={() => onSongSelect(song)}
            onArtistClick={onArtistClick}
          />
        ))}
      </div>
    </section>
  )
}

function ArtistSpotlightCard({
  artist,
  songCount,
  topSong,
  onClick,
}: {
  artist: string
  songCount: number
  topSong: Song
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="flex-shrink-0 w-[180px] bg-card rounded-xl p-3 shadow-sm border border-border/50 cursor-pointer hover:shadow-md active:scale-[0.98] transition-all"
    >
      <p className="font-bold text-sm text-foreground truncate">{artist}</p>
      <p className="text-xs text-muted-foreground mt-0.5">{songCount} chart entries</p>
      <div className="mt-2 pt-2 border-t border-border/30">
        <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Top Hit</p>
        <p className="text-xs font-medium text-foreground truncate mt-0.5">{topSong.title}</p>
      </div>
    </div>
  )
}

function DecadeSection({
  decade,
  songs,
  onSongSelect,
  onArtistClick,
  onExpand,
}: {
  decade: string
  songs: Song[]
  onSongSelect: (song: Song) => void
  onArtistClick: (artist: string) => void
  onExpand: () => void
}) {
  const topSongs = songs.slice(0, 4)
  
  return (
    <div className="bg-card rounded-xl p-3 shadow-sm border border-border/50">
      <button
        onClick={onExpand}
        className="section-header flex items-center justify-between w-full mb-2 group text-left"
      >
        <span className="text-lg font-black text-foreground">{decade}</span>
        <span className="text-xs text-muted-foreground group-hover:text-primary">
          {songs.length} ›
        </span>
      </button>
      <div className="space-y-1.5">
        {topSongs.map((song, index) => (
          <div
            key={`${song.title}-${song.artist}`}
            onClick={() => onSongSelect(song)}
            className="flex items-center gap-2 py-1 cursor-pointer hover:bg-muted/60 rounded px-1 -mx-1"
          >
            <span className="w-5 text-xs font-bold text-muted-foreground tabular-nums">
              {index + 1}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-foreground truncate">{song.title}</p>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onArtistClick(song.artist)
                }}
                className="text-[10px] text-muted-foreground hover:text-primary hover:underline truncate block text-left"
              >
                {song.artist}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function EditorialBrowse({
  songs,
  onSongSelect,
  onArtistClick,
  onSectionExpand,
}: EditorialBrowseProps) {
  const sections = useMemo(() => {
    const usedIds = new Set<string>()
    const id = (s: Song) => `${s.title}|${s.artist}|${s.year}`

    const pickUnique = (candidates: Song[], n: number) => {
      const out: Song[] = []
      for (const s of candidates) {
        if (out.length >= n) break
        if (!usedIds.has(id(s))) {
          usedIds.add(id(s))
          out.push(s)
        }
      }
      return out
    }

    // Trending Songs - sort by weeks (descending)
    const trendingCandidates = songs.slice().sort((a, b) => b.weeks - a.weeks)
    const trendingSongs = pickUnique(trendingCandidates, 20)

    // Biggest #1 Hits - sort by weeks_at_peak (descending), fallback to weeks
    const numberOneCandidates = songs
      .filter(s => s.peak === 1)
      .sort((a, b) => (b.weeks_at_peak ?? 0) - (a.weeks_at_peak ?? 0) || b.weeks - a.weeks)
    const numberOneHits = pickUnique(numberOneCandidates, 20)

    // Longest Chart Runs - sort by weeks (descending)
    const longestCandidates = songs.slice().sort((a, b) => b.weeks - a.weeks)
    const longestRuns = pickUnique(longestCandidates, 20)

    // Decades - random sample per decade, exclude already used
    const decadeRanges = [
      ['60s', 1960, 1970],
      ['70s', 1970, 1980],
      ['80s', 1980, 1990],
      ['90s', 1990, 2000],
    ] as const
    const songsByDecade: Record<string, Song[]> = {}
    for (const [decade, start, end] of decadeRanges) {
      const pool = songs
        .filter(s => s.year >= start && s.year < end)
        .filter(s => !usedIds.has(id(s)))
      const shuffled = [...pool].sort(() => Math.random() - 0.5)
      const sampled = pickUnique(
        shuffled.length ? shuffled : songs.filter(s => s.year >= start && s.year < end),
        20
      )
      songsByDecade[decade] = sampled.sort((a, b) => a.peak - b.peak || b.weeks - a.weeks)
    }

    // Artist Spotlights - artists with most chart entries
    const artistMap = new Map<string, Song[]>()
    songs.forEach(song => {
      const existing = artistMap.get(song.artist) || []
      artistMap.set(song.artist, [...existing, song])
    })
    const topArtists = Array.from(artistMap.entries())
      .map(([artist, songs]) => ({
        artist,
        songs: songs.sort((a, b) => a.peak - b.peak),
        count: songs.length,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)

    return {
      trendingSongs,
      numberOneHits,
      longestRuns,
      songsByDecade,
      topArtists,
    }
  }, [songs])

  return (
    <div>
      {/* Trending Songs */}
      <HorizontalScrollSection
        title="Trending Songs"
        songs={sections.trendingSongs}
        onSongSelect={onSongSelect}
        onArtistClick={onArtistClick}
        onExpand={() => onSectionExpand('Trending Songs', sections.trendingSongs)}
        showRank
      />

      {/* Biggest #1 Hits */}
      <HorizontalScrollSection
        title="Biggest #1 Hits"
        songs={sections.numberOneHits}
        onSongSelect={onSongSelect}
        onArtistClick={onArtistClick}
        onExpand={() => onSectionExpand('Biggest #1 Hits', sections.numberOneHits)}
        showRank
      />

      {/* Longest Chart Runs */}
      <HorizontalScrollSection
        title="Longest Chart Runs"
        songs={sections.longestRuns}
        onSongSelect={onSongSelect}
        onArtistClick={onArtistClick}
        onExpand={() => onSectionExpand('Longest Chart Runs', sections.longestRuns)}
      />

      {/* Classic Hits by Decade */}
      <section className="section">
        <h2 className="section-header text-[0.85rem] font-semibold tracking-[0.08em] text-muted-foreground mb-3">
          Classic Hits by Decade
        </h2>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(sections.songsByDecade).map(([decade, songs]) => (
            <DecadeSection
              key={decade}
              decade={decade}
              songs={songs}
              onSongSelect={onSongSelect}
              onArtistClick={onArtistClick}
              onExpand={() => onSectionExpand(`${decade} Hits`, songs)}
            />
          ))}
        </div>
      </section>

      {/* Artist Spotlights */}
      <section className="section">
        <h2 className="section-header text-[0.85rem] font-semibold tracking-[0.08em] text-muted-foreground mb-3">
          Artist Spotlights
        </h2>
        <div className="horizontal-scroll-section flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 pr-6 scrollbar-hide">
          {sections.topArtists.map(({ artist, songs, count }) => (
            <ArtistSpotlightCard
              key={artist}
              artist={artist}
              songCount={count}
              topSong={songs[0]}
              onClick={() => onArtistClick(artist)}
            />
          ))}
        </div>
      </section>
    </div>
  )
}
