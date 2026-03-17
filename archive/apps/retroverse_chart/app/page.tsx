'use client'

import { Music, Calendar, Shuffle, BarChart3, Info, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { SearchBar } from '@/components/search-bar'
import { FilterChips } from '@/components/filter-chips'
import { SongList } from '@/components/song-list'
import { SongDetail } from '@/components/song-detail'
import { ArtistPage } from '@/components/artist-page'
import { ChartStatsPage } from '@/components/chart-stats'
import { RandomYearPage } from '@/components/random-year-page'
import { WeeklyChartView } from '@/components/weekly-chart-view'
import { AboutPage } from '@/components/about-page'
import { DecadeExplorer } from '@/components/decade-explorer'
import { SectionListPage } from '@/components/section-list-page'
import { useChartData } from '@/hooks/use-chart-data'
import { cn } from '@/lib/utils'

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false)
  
  const {
    songs,
    allSongs,
    isLoading,
    searchQuery,
    setSearchQuery,
    activeFilters,
    handleFilterToggle,
    selectedSong,
    selectSong,
    setSelectedSong,
    selectedArtist,
    selectArtist,
    setSelectedArtist,
    artistData,
    randomYear,
    handleRandomYear,
    clearRandomYear,
    viewMode,
    selectedWeek,
    openWeeklyChart,
    pickRandomChart,
    openChartStats,
    openAbout,
    openSectionList,
    expandedSection,
    goToMain,
  } = useChartData()

  // Determine if we're in search/filter mode
  const isSearchMode = searchQuery.length > 0 || activeFilters.length > 0

  // Weekly Chart View
  if (viewMode === 'weeklyChart' && selectedWeek) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <WeeklyChartView
            weekOf={selectedWeek}
            songs={allSongs}
            onBack={goToMain}
            onSongSelect={selectSong}
            onArtistClick={selectArtist}
          />
        </div>
      </main>
    )
  }

  // Chart Stats View
  if (viewMode === 'chartStats') {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <ChartStatsPage
            songs={allSongs}
            onBack={goToMain}
            onSongSelect={selectSong}
            onArtistClick={selectArtist}
          />
        </div>
      </main>
    )
  }

  // Random Year View
  if (viewMode === 'randomYear' && randomYear !== null) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <RandomYearPage
            year={randomYear}
            songs={allSongs}
            onBack={() => {
              clearRandomYear()
              goToMain()
            }}
            onSongSelect={selectSong}
            onArtistClick={selectArtist}
            onNewRandomYear={handleRandomYear}
          />
        </div>
      </main>
    )
  }

  // Song Detail View
  if (viewMode === 'songDetail' && selectedSong) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <SongDetail
            song={selectedSong}
            onBack={() => {
              setSelectedSong(null)
              goToMain()
            }}
            onArtistClick={(artist) => {
              setSelectedSong(null)
              selectArtist(artist)
            }}
          />
        </div>
      </main>
    )
  }

  // Artist View
  if (viewMode === 'artist' && selectedArtist && artistData) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <ArtistPage
            artist={artistData}
            onBack={() => {
              setSelectedArtist(null)
              goToMain()
            }}
            onSongSelect={selectSong}
          />
        </div>
      </main>
    )
  }

  // About View
  if (viewMode === 'about') {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <AboutPage onBack={goToMain} />
        </div>
      </main>
    )
  }

  // Section List View
  if (viewMode === 'sectionList' && expandedSection) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-lg mx-auto px-4 py-6">
          <SectionListPage
            title={expandedSection.title}
            songs={expandedSection.songs}
            onBack={goToMain}
            onSongSelect={selectSong}
            onArtistClick={selectArtist}
          />
        </div>
      </main>
    )
  }

  // Main Screen
  return (
    <main className="min-h-screen bg-background">
      <div className="max-w-lg mx-auto px-4 py-6">
        {/* Header */}
        <header className="mb-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-black text-foreground tracking-tight">
                RetroVerse Charts
              </h1>
              <p className="text-xs text-muted-foreground">
                Music chart history since 1958
              </p>
            </div>
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-2 rounded-xl hover:bg-muted active:scale-95 transition-all"
                aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              >
                {menuOpen ? (
                  <X className="w-5 h-5 text-foreground" />
                ) : (
                  <Menu className="w-5 h-5 text-foreground" />
                )}
              </button>

              {/* Dropdown Menu */}
              {menuOpen && (
                <div className="absolute right-0 top-full mt-2 w-52 bg-card rounded-xl shadow-lg border border-border z-50 overflow-hidden">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        goToMain()
                        setMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      <Music className="w-4 h-4 text-retro-teal" />
                      <span>Browse Songs</span>
                    </button>
                    <button
                      onClick={() => {
                        pickRandomChart()
                        setMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      <Shuffle className="w-4 h-4 text-retro-mustard" />
                      <span>Random Chart</span>
                    </button>
                    <button
                      onClick={() => {
                        handleRandomYear()
                        setMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      <Calendar className="w-4 h-4 text-retro-coral" />
                      <span>Random Year</span>
                    </button>
                    <div className="border-t border-border my-1" />
                    <button
                      onClick={() => {
                        openChartStats()
                        setMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      <BarChart3 className="w-4 h-4 text-retro-aqua" />
                      <span>Chart Records</span>
                    </button>
                    <div className="border-t border-border my-1" />
                    <button
                      onClick={() => {
                        openAbout()
                        setMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      <Info className="w-4 h-4 text-muted-foreground" />
                      <span>About</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Search */}
        <div className="mb-3">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>

        {/* Filters */}
        <div className="mb-4">
          <FilterChips
            activeFilters={activeFilters}
            onFilterToggle={handleFilterToggle}
            onRandomYear={handleRandomYear}
            onPickWeek={openWeeklyChart}
            onRandomChart={pickRandomChart}
          />
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-pulse flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-muted rounded-full" />
              <div className="w-24 h-4 bg-muted rounded" />
            </div>
          </div>
        ) : isSearchMode ? (
          <>
            {/* Search Results Count */}
            <div className="mb-3">
              <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                {songs.length.toLocaleString()} {songs.length === 1 ? 'song' : 'songs'} found
              </p>
            </div>
            {/* Song List for Search/Filter Mode */}
            <SongList
              songs={songs}
              onSongSelect={selectSong}
              onArtistClick={selectArtist}
            />
          </>
        ) : (
          /* Decade Explorer */
          <DecadeExplorer
            songs={allSongs}
            onDecadeSelect={openSectionList}
          />
        )}
      </div>

      {/* Click outside to close menu */}
      {menuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setMenuOpen(false)}
        />
      )}
    </main>
  )
}
