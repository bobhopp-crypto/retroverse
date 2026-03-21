'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import useSWR from 'swr'
import type { Song, FilterType, ArtistData, ViewMode } from '@/lib/types'
import { searchMatch } from '@/lib/search'

const SEARCH_DEBOUNCE_MS = 200
const DATA_URL = `${process.env.NEXT_PUBLIC_BASE_PATH || ''}/data/billboard_hot_100.json`

const fetcher = async (url: string): Promise<Song[]> => {
  const res = await fetch(url)
  if (!res.ok) return []
  try {
    return await res.json()
  } catch {
    return []
  }
}

export function useChartData() {
  const { data: songs = [], isLoading } = useSWR<Song[]>(DATA_URL, fetcher)
  
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
  const [activeFilters, setActiveFilters] = useState<FilterType[]>([])

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearchQuery(searchQuery), SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(t)
  }, [searchQuery])
  const [selectedSong, setSelectedSong] = useState<Song | null>(null)
  const [selectedArtist, setSelectedArtist] = useState<string | null>(null)
  const [randomYear, setRandomYear] = useState<number | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('main')
  const [selectedWeek, setSelectedWeek] = useState<string | null>(null)
  const [expandedSection, setExpandedSection] = useState<{ title: string; songs: Song[] } | null>(null)

  const filteredSongs = useMemo(() => {
    let result = songs

    // Apply search filter (normalized + fuzzy: P!nk → Pink, case-insensitive)
    if (debouncedSearchQuery) {
      result = result.filter(song =>
        searchMatch(debouncedSearchQuery, song.artist, song.title)
      )
    }

    // Apply random year filter
    if (randomYear !== null) {
      result = result.filter(song => song.year === randomYear)
    }

    // Apply chart position and decade filters
    if (activeFilters.length > 0) {
      result = result.filter(song => {
        return activeFilters.some(filter => {
          switch (filter) {
            case '#1':
              return song.peak === 1
            case 'Top10':
              return song.peak <= 10
            case 'Top40':
              return song.peak <= 40
            case '60s':
              return song.year >= 1960 && song.year < 1970
            case '70s':
              return song.year >= 1970 && song.year < 1980
            case '80s':
              return song.year >= 1980 && song.year < 1990
            case '90s':
              return song.year >= 1990 && song.year < 2000
            default:
              return true
          }
        })
      })
    }

    return result
  }, [songs, debouncedSearchQuery, activeFilters, randomYear])

  const artistData = useMemo<ArtistData | null>(() => {
    if (!selectedArtist) return null

    const artistSongs = songs.filter(song => song.artist === selectedArtist)
    
    const songsByDecade = artistSongs.reduce((acc, song) => {
      const decade = `${Math.floor(song.year / 10) * 10}s`
      acc[decade] = (acc[decade] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const longestChartRun = artistSongs.reduce((max, song) => Math.max(max, song.weeks), 0)
    const averagePeak = artistSongs.length > 0
      ? artistSongs.reduce((sum, song) => sum + song.peak, 0) / artistSongs.length
      : 0

    return {
      name: selectedArtist,
      totalSongs: artistSongs.length,
      top10Hits: artistSongs.filter(s => s.peak <= 10).length,
      numberOneHits: artistSongs.filter(s => s.peak === 1).length,
      longestChartRun,
      averagePeak,
      songsByDecade,
      songs: artistSongs.sort((a, b) => a.year - b.year),
    }
  }, [selectedArtist, songs])

  const availableYears = useMemo(() => {
    return [...new Set(songs.map(s => s.year))].sort((a, b) => a - b)
  }, [songs])

  const handleFilterToggle = useCallback((filter: FilterType) => {
    setRandomYear(null)
    setActiveFilters(prev =>
      prev.includes(filter)
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    )
  }, [])

  const handleRandomYear = useCallback(() => {
    if (availableYears.length > 0) {
      const year = availableYears[Math.floor(Math.random() * availableYears.length)]
      setRandomYear(year)
      setActiveFilters([])
      setViewMode('randomYear')
    }
  }, [availableYears])

  const clearRandomYear = useCallback(() => {
    setRandomYear(null)
    setViewMode('main')
  }, [])

  const openWeeklyChart = useCallback((weekDate: string) => {
    setSelectedWeek(weekDate)
    setViewMode('weeklyChart')
  }, [])

  const pickRandomChart = useCallback(() => {
    // Generate a random date between 1958-08-04 and 2024-12-28
    const startDate = new Date('1958-08-04')
    const endDate = new Date('2024-12-28')
    const timeDiff = endDate.getTime() - startDate.getTime()
    const randomTime = Math.random() * timeDiff
    const randomDate = new Date(startDate.getTime() + randomTime)
    
    // Format as YYYY-MM-DD
    const year = randomDate.getFullYear()
    const month = String(randomDate.getMonth() + 1).padStart(2, '0')
    const day = String(randomDate.getDate()).padStart(2, '0')
    const dateString = `${year}-${month}-${day}`
    
    setSelectedWeek(dateString)
    setViewMode('weeklyChart')
  }, [])

  const openChartStats = useCallback(() => {
    setViewMode('chartStats')
  }, [])

  const openAbout = useCallback(() => {
    setViewMode('about')
  }, [])

  const openSectionList = useCallback((title: string, songs: Song[]) => {
    setExpandedSection({ title, songs })
    setViewMode('sectionList')
  }, [])

  const goToMain = useCallback(() => {
    setViewMode('main')
    setSelectedSong(null)
    setSelectedArtist(null)
    setSelectedWeek(null)
    setExpandedSection(null)
  }, [])

  const selectSong = useCallback((song: Song) => {
    setSelectedSong(song)
    setViewMode('songDetail')
  }, [])

  const selectArtist = useCallback((artist: string) => {
    setSelectedArtist(artist)
    setViewMode('artist')
  }, [])

  return {
    songs: filteredSongs,
    allSongs: songs,
    isLoading,
    searchQuery,
    setSearchQuery,
    activeFilters,
    handleFilterToggle,
    selectedSong,
    setSelectedSong,
    selectSong,
    selectedArtist,
    setSelectedArtist,
    selectArtist,
    artistData,
    randomYear,
    handleRandomYear,
    clearRandomYear,
    viewMode,
    setViewMode,
    selectedWeek,
    openWeeklyChart,
    pickRandomChart,
    openChartStats,
    openAbout,
    openSectionList,
    expandedSection,
    goToMain,
    availableYears,
  }
}
