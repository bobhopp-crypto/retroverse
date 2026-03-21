import { startTransition, useDeferredValue, useEffect, useMemo, useRef, useState, type TouchEvent as ReactTouchEvent } from 'react'
import VideoInfoModal from '../components/VideoInfoModal'
import type { RandomizerLabel, RandomizerTier, SpinResult } from '../components/RetroVerseRandomizer'
import VideoLibraryFilterRings from '../components/VideoLibraryFilterRings'
import { usePlaylistContext } from '../context/PlaylistContext'
import { useFastMode } from '../lib/useFastMode'
import { formatDuration, formatYear, loadVideoIndex, rowSearchText, stableVideoHash, type VideoRecord } from '../lib/videoIndex'
import './VideoLibrary.css'

const SWIPE_ACTION_WIDTH = 132
const SWIPE_REVEAL_THRESHOLD = 40
const SWIPE_LOCK_THRESHOLD = 14
const SORT_CYCLE = ['plays', 'year', 'title', 'artist'] as const
const DECADE_PILLS = ['60s', '70s', '80s', '90s', '00s', '10s'] as const
const NEWNESS_FILTERS = ['all', '30d', '90d', '1y'] as const
const TIER_FILTERS = ['promo', 'light', 'medium', 'heavy', 'power'] as const
const RETENTION_FILTERS = ['all', 'S', 'A', 'B', 'C'] as const
const RANDOMIZER_TIERS = ['Promo', 'Light', 'Medium', 'Heavy', 'Power'] as const
const YEAR_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] as const
const FILTER_STORAGE_KEY = 'retroverse.videoLibrary.filters.v1'
const FAST_MODE_INITIAL_DECADES = ['1980s'] as const

type SortMode = (typeof SORT_CYCLE)[number]
type DecadePill = (typeof DECADE_PILLS)[number]
type NewnessMode = (typeof NEWNESS_FILTERS)[number]
type TierFilter = (typeof TIER_FILTERS)[number]
type RetentionFilter = (typeof RETENTION_FILTERS)[number]
type YearDigit = number
type TouchState = {
  rowId: string | null
  startX: number
  startY: number
  baseOffset: number
  lock: 'undecided' | 'horizontal' | 'vertical'
  leftDistance: number
}

type SearchableRow = {
  row: VideoRecord
  textTokens: string[]
}

type ActiveFilterState = {
  query: ReturnType<typeof parseSearch>
  activeSpinYear: number | null
  activeDecades: DecadePill[]
  activeYearDigits: YearDigit[]
  activeTiers: TierFilter[]
  retentionFilter: RetentionFilter
  newnessMode: NewnessMode
}

const TIER_TO_RANDOMIZER: Record<TierFilter, RandomizerTier> = {
  promo: 'Promo',
  light: 'Light',
  medium: 'Medium',
  heavy: 'Heavy',
  power: 'Power',
}
const RANDOMIZER_TO_TIER: Record<RandomizerTier, TierFilter> = {
  Promo: 'promo',
  Light: 'light',
  Medium: 'medium',
  Heavy: 'heavy',
  Power: 'power',
}
const SORT_LABELS: Record<SortMode, string> = {
  plays: 'Plays',
  year: 'Year',
  title: 'Title',
  artist: 'Artist',
}

const DECADE_PILL_TO_DATA_DECADE: Record<DecadePill, string> = {
  '60s': '1960s',
  '70s': '1970s',
  '80s': '1980s',
  '90s': '1990s',
  '00s': '2000s',
  '10s': '2010s',
}

const decadeFromYear = (year: number): string => `${Math.floor(year / 10) * 10}s`

const normalizeSearchText = (value: string) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()

const tokenize = (value: string) => {
  const normalized = normalizeSearchText(value)
  return normalized ? normalized.split(/\s+/) : []
}

const parseYearToken = (value: string): number | null => {
  if (!/^\d{2,4}$/.test(value)) return null
  const num = Number(value)
  if (!Number.isFinite(num)) return null
  if (value.length === 2) return 1900 + num
  return num
}

const parseYearRangeToken = (value: string): { start: number; end: number } | null => {
  const match = value.match(/^(\d{2,4})-(\d{2,4})$/)
  if (!match) return null
  const left = parseYearToken(match[1])
  if (left === null) return null
  let right = parseYearToken(match[2])
  if (right === null) return null

  if (match[1].length === 4 && match[2].length === 2) {
    const century = Math.floor(left / 100) * 100
    right = century + Number(match[2])
  }

  return { start: Math.min(left, right), end: Math.max(left, right) }
}

const parseSearch = (query: string): { textTokens: string[]; yearValues: number[]; yearRanges: Array<{ start: number; end: number }> } => {
  const normalizedQuery = query.replace(/[–—]/g, '-')
  const rawTokens = normalizedQuery.toLowerCase().split(/\s+/).map((token) => token.trim()).filter(Boolean)
  const textParts: string[] = []
  const yearValues: number[] = []
  const yearRanges: Array<{ start: number; end: number }> = []

  for (const token of rawTokens) {
    const cleaned = token.replace(/[^0-9a-z-]/g, '')
    if (!cleaned) continue

    const yearRange = parseYearRangeToken(cleaned)
    if (yearRange) {
      yearRanges.push(yearRange)
      continue
    }

    const yearValue = parseYearToken(cleaned)
    if (yearValue !== null && cleaned.length === 4) {
      yearValues.push(yearValue)
      continue
    }

    textParts.push(cleaned)
  }

  return {
    textTokens: tokenize(textParts.join(' ')),
    yearValues,
    yearRanges,
  }
}

const matchesDecade = (year: number | null, pill: DecadePill) => {
  if (typeof year !== 'number') return false
  if (pill === '60s') return year >= 1960 && year <= 1969
  if (pill === '70s') return year >= 1970 && year <= 1979
  if (pill === '80s') return year >= 1980 && year <= 1989
  if (pill === '90s') return year >= 1990 && year <= 1999
  if (pill === '00s') return year >= 2000 && year <= 2009
  return year >= 2010
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))
const pickRandomValue = <T,>(items: readonly T[]): T => items[Math.floor(Math.random() * items.length)]!
const sampleRandom = <T,>(items: T[], count: number): T[] => {
  const copy = [...items]
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy.slice(0, count)
}

const recencyMatch = (row: VideoRecord, mode: NewnessMode, nowMs: number) => {
  if (mode === 'all') return true
  const windowDays = mode === '30d' ? 30 : mode === '90d' ? 90 : 365
  const threshold = nowMs - windowDays * 24 * 60 * 60 * 1000
  if (row.firstSeenMs) return row.firstSeenMs >= threshold
  if (row.addedAt) {
    const asMs = new Date(row.addedAt).getTime()
    if (Number.isFinite(asMs)) return asMs >= threshold
  }
  return false
}

const normalizeTierFilter = (value: VideoRecord['tier']): TierFilter | null => {
  if (!value) return null
  const normalized = value.toLowerCase()
  return TIER_FILTERS.includes(normalized as TierFilter) ? (normalized as TierFilter) : null
}

const EMPTY_VIDEO_ROWS: VideoRecord[] = []

const matchesActiveFilters = ({ row, textTokens }: SearchableRow, filters: ActiveFilterState, nowMs: number): boolean => {
  const { query, activeSpinYear, activeDecades, activeYearDigits, activeTiers, retentionFilter, newnessMode } = filters
  const numericYear = typeof row.year === 'number' ? row.year : null

  if (query.textTokens.length > 0) {
    const isTextMatch = query.textTokens.every((token) => textTokens.some((word) => word.startsWith(token)))
    if (!isTextMatch) return false
  }

  if (query.yearValues.length > 0) {
    if (numericYear === null) return false
    const isYearMatch = query.yearValues.every((year) => numericYear === year)
    if (!isYearMatch) return false
  }

  if (query.yearRanges.length > 0) {
    if (numericYear === null) return false
    const isRangeMatch = query.yearRanges.every((range) => numericYear >= range.start && numericYear <= range.end)
    if (!isRangeMatch) return false
  }

  if (activeSpinYear !== null && numericYear !== activeSpinYear) return false

  if (activeDecades.length > 0 && !activeDecades.some((pill) => matchesDecade(numericYear, pill))) return false

  if (activeYearDigits.length > 0) {
    if (numericYear === null) return false
    const digit = Math.abs(numericYear) % 10
    if (!activeYearDigits.includes(digit)) return false
  }

  if (retentionFilter !== 'all' && row.retentionGrade !== retentionFilter) return false

  if (activeTiers.length > 0) {
    const tier = normalizeTierFilter(row.tier)
    if (!tier || !activeTiers.includes(tier)) return false
  }

  return recencyMatch(row, newnessMode, nowMs)
}

const countMatchingRows = (searchableRows: SearchableRow[], filters: ActiveFilterState): number => {
  const nowMs = Date.now()
  let count = 0

  for (const entry of searchableRows) {
    if (matchesActiveFilters(entry, filters, nowMs)) count += 1
  }

  return count
}

const buildFilteredRows = (searchableRows: SearchableRow[], filters: ActiveFilterState, sortMode: SortMode): VideoRecord[] => {
  const nowMs = Date.now()
  const matches: VideoRecord[] = []

  for (const entry of searchableRows) {
    if (matchesActiveFilters(entry, filters, nowMs)) {
      matches.push(entry.row)
    }
  }

  matches.sort((a, b) => {
    if (sortMode === 'plays') {
      return b.playcount - a.playcount || a.title.localeCompare(b.title)
    }
    if (sortMode === 'year') {
      return (b.year ?? -1) - (a.year ?? -1) || a.title.localeCompare(b.title)
    }
    if (sortMode === 'artist') {
      return a.artist.localeCompare(b.artist) || a.title.localeCompare(b.title)
    }
    return a.title.localeCompare(b.title)
  })

  return matches
}

export default function VideoLibrary() {
  const { addToQueue, openPlayer } = usePlaylistContext()
  const isFastMode = useFastMode()

  const [rows, setRows] = useState<VideoRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [sortMode, setSortMode] = useState<SortMode>('plays')
  const [newnessMode, setNewnessMode] = useState<NewnessMode>('all')
  const [activeDecades, setActiveDecades] = useState<DecadePill[]>([])
  const [activeTiers, setActiveTiers] = useState<TierFilter[]>([])
  const [activeYearDigits, setActiveYearDigits] = useState<YearDigit[]>([])
  const [activeSpinYear, setActiveSpinYear] = useState<number | null>(null)
  const [retentionFilter, setRetentionFilter] = useState<RetentionFilter>('all')
  const [sortButtonPrimed, setSortButtonPrimed] = useState(false)
  const [isConsoleOpen, setIsConsoleOpen] = useState(false)
  const [allowFullCatalogInFastMode, setAllowFullCatalogInFastMode] = useState(false)
  const [spinFallbackDecade, setSpinFallbackDecade] = useState<DecadePill | 'all' | null>(null)
  const [fallbackRows, setFallbackRows] = useState<VideoRecord[] | null>(null)
  const [openSwipe, setOpenSwipe] = useState<string | null>(null)
  const [dragOffset, setDragOffset] = useState<{ id: string; offset: number } | null>(null)
  const [infoVideo, setInfoVideo] = useState<VideoRecord | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const touchRef = useRef<TouchState>({
    rowId: null,
    startX: 0,
    startY: 0,
    baseOffset: 0,
    lock: 'undecided',
    leftDistance: 0,
  })

  const requestedDecades = useMemo(() => {
    if (typeof activeSpinYear === 'number') return [decadeFromYear(activeSpinYear)]
    if (activeDecades.length === 0) {
      if (isFastMode && !allowFullCatalogInFastMode) return [...FAST_MODE_INITIAL_DECADES]
      return []
    }
    const mapped = activeDecades.map((pill) => DECADE_PILL_TO_DATA_DECADE[pill])
    return [...new Set(mapped)].sort((left, right) => Number(left.slice(0, 4)) - Number(right.slice(0, 4)))
  }, [activeDecades, activeSpinYear, allowFullCatalogInFastMode, isFastMode])

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const parsed =
          requestedDecades.length === 0
            ? await loadVideoIndex()
            : (await Promise.all(requestedDecades.map((decade) => loadVideoIndex(decade)))).flat()
        if (!cancelled) setRows(parsed)
      } catch (err) {
        if (!cancelled) setError((err as Error).message || 'Load error')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    run()
    return () => {
      cancelled = true
    }
  }, [requestedDecades])

  useEffect(() => {
    try {
      const raw = localStorage.getItem(FILTER_STORAGE_KEY)
      if (!raw) return
      const data = JSON.parse(raw) as {
        search?: string
        sortMode?: SortMode
        newnessMode?: NewnessMode
        activeDecades?: DecadePill[]
        activeTiers?: TierFilter[]
        activeYearDigits?: YearDigit[]
        activeSpinYear?: number | null
        retentionFilter?: RetentionFilter
      }
      if (typeof data.search === 'string') setSearch(data.search)
      if (data.sortMode && SORT_CYCLE.includes(data.sortMode)) setSortMode(data.sortMode)
      if (data.newnessMode && NEWNESS_FILTERS.includes(data.newnessMode)) setNewnessMode(data.newnessMode)
      if (Array.isArray(data.activeDecades)) {
        const filtered = data.activeDecades.filter((pill): pill is DecadePill => DECADE_PILLS.includes(pill))
        setActiveDecades(filtered)
      }
      if (Array.isArray(data.activeTiers)) {
        const filtered = data.activeTiers.filter((tier): tier is TierFilter => TIER_FILTERS.includes(tier))
        setActiveTiers(filtered)
      }
      if (Array.isArray(data.activeYearDigits)) {
        const filtered = data.activeYearDigits.filter((digit): digit is YearDigit => Number.isInteger(digit) && digit >= 0 && digit <= 9)
        setActiveYearDigits(filtered)
      }
      if (typeof data.activeSpinYear === 'number' && Number.isInteger(data.activeSpinYear)) {
        setActiveSpinYear(data.activeSpinYear)
      }
      if (data.retentionFilter && RETENTION_FILTERS.includes(data.retentionFilter)) {
        setRetentionFilter(data.retentionFilter)
      }
    } catch {
      // Ignore malformed persisted filter state.
    }
  }, [])

  useEffect(() => {
    const payload = {
      search,
      sortMode,
      newnessMode,
      activeDecades,
      activeTiers,
      activeYearDigits,
      activeSpinYear,
      retentionFilter,
    }
    localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(payload))
  }, [search, sortMode, newnessMode, activeDecades, activeTiers, activeYearDigits, activeSpinYear, retentionFilter])

  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(null), 1500)
    return () => window.clearTimeout(timer)
  }, [toast])

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search), 250)
    return () => window.clearTimeout(timer)
  }, [search])

  useEffect(() => {
    if (!isFastMode || allowFullCatalogInFastMode) return
    if (search.trim().length === 0) return
    setAllowFullCatalogInFastMode(true)
  }, [allowFullCatalogInFastMode, isFastMode, search])

  const query = useMemo(() => parseSearch(debouncedSearch), [debouncedSearch])
  const searchableRows = useMemo(
    () =>
      rows.map((row) => ({
        row,
        textTokens: tokenize(rowSearchText(row)),
      })),
    [rows],
  )
  const activeFilters = useMemo<ActiveFilterState>(
    () => ({
      query,
      activeSpinYear,
      activeDecades,
      activeYearDigits,
      activeTiers,
      retentionFilter,
      newnessMode,
    }),
    [query, activeSpinYear, activeDecades, activeYearDigits, activeTiers, retentionFilter, newnessMode],
  )
  const matchCount = useMemo(() => countMatchingRows(searchableRows, activeFilters), [searchableRows, activeFilters])
  const filteredVideos = useMemo(() => {
    if (isConsoleOpen) return EMPTY_VIDEO_ROWS
    return buildFilteredRows(searchableRows, activeFilters, sortMode)
  }, [isConsoleOpen, searchableRows, activeFilters, sortMode])
  const visibleRows = isConsoleOpen ? EMPTY_VIDEO_ROWS : fallbackRows ?? filteredVideos
  const deferredVisibleRows = useDeferredValue(visibleRows)

  useEffect(() => {
    if (isConsoleOpen) return
    if (!spinFallbackDecade) {
      setFallbackRows(null)
      return
    }
    if (matchCount > 0) {
      setFallbackRows(null)
      return
    }

    const candidates =
      typeof activeSpinYear === 'number'
        ? rows.filter((row) => row.year === activeSpinYear)
        : spinFallbackDecade === 'all'
          ? rows
          : rows.filter((row) => matchesDecade(row.year, spinFallbackDecade as DecadePill))
    setFallbackRows(sampleRandom(candidates, 5))
  }, [isConsoleOpen, spinFallbackDecade, activeSpinYear, matchCount, rows])

  const onRowTouchStart = (event: ReactTouchEvent<HTMLElement>, row: VideoRecord) => {
    if (event.touches.length !== 1) return
    const touch = event.touches[0]

    touchRef.current = {
      rowId: row.id,
      startX: touch.clientX,
      startY: touch.clientY,
      baseOffset: openSwipe === row.id ? -SWIPE_ACTION_WIDTH : 0,
      lock: 'undecided',
      leftDistance: openSwipe === row.id ? SWIPE_ACTION_WIDTH : 0,
    }

    if (openSwipe && openSwipe !== row.id) {
      setOpenSwipe(null)
    }
  }

  const onRowTouchMove = (event: ReactTouchEvent<HTMLElement>) => {
    if (!touchRef.current.rowId || event.touches.length !== 1) return
    const touch = event.touches[0]

    const dx = touch.clientX - touchRef.current.startX
    const dy = touch.clientY - touchRef.current.startY
    const absDx = Math.abs(dx)
    const absDy = Math.abs(dy)

    if (touchRef.current.lock === 'undecided' && (absDx > SWIPE_LOCK_THRESHOLD || absDy > SWIPE_LOCK_THRESHOLD)) {
      const horizontal = dx < 0 && absDx > absDy * 1.4
      touchRef.current.lock = horizontal ? 'horizontal' : 'vertical'
    }

    if (touchRef.current.lock !== 'horizontal') return

    const nextOffset = clamp(touchRef.current.baseOffset + dx, -SWIPE_ACTION_WIDTH, 0)
    touchRef.current.leftDistance = Math.max(0, -nextOffset)
    setDragOffset({ id: touchRef.current.rowId, offset: nextOffset })
    event.preventDefault()
  }

  const onRowTouchEnd = () => {
    if (!touchRef.current.rowId) return

    const id = touchRef.current.rowId
    if (touchRef.current.lock === 'horizontal' && touchRef.current.leftDistance >= SWIPE_REVEAL_THRESHOLD) {
      setOpenSwipe(id)
    } else {
      setOpenSwipe(null)
    }

    setDragOffset(null)
    touchRef.current = {
      rowId: null,
      startX: 0,
      startY: 0,
      baseOffset: 0,
      lock: 'undecided',
      leftDistance: 0,
    }
  }

  const onAddToQueue = (row: VideoRecord) => {
    addToQueue(row)
    setToast(`${row.title} added to playlist`)
    setOpenSwipe(null)
  }

  const openInfoModal = (entry: VideoRecord) => {
    setInfoVideo(entry)
  }

  const statusLabel = loading || error ? (loading ? 'Loading…' : 'Load failed') : `${matchCount}/${rows.length}`
  const isFastModeSampling = isFastMode && !allowFullCatalogInFastMode && activeDecades.length === 0 && activeSpinYear === null
  const openFilterConsole = () => {
    setIsConsoleOpen(true)
  }
  const closeFilterConsole = () => {
    setIsConsoleOpen(false)
  }
  const clearAllFilters = () => {
    setSortButtonPrimed(false)
    localStorage.removeItem(FILTER_STORAGE_KEY)
    startTransition(() => {
      setSpinFallbackDecade(null)
      setFallbackRows(null)
      setSearch('')
      setSortMode('plays')
      setActiveDecades([])
      setActiveTiers([])
      setActiveYearDigits([])
      setActiveSpinYear(null)
      setRetentionFilter('all')
      setNewnessMode('all')
      setAllowFullCatalogInFastMode(false)
    })
  }
  const cycleSortMode = () => {
    setSortButtonPrimed(true)
    startTransition(() => {
      setSortMode((current) => {
        const currentIndex = SORT_CYCLE.indexOf(current)
        const nextIndex = (currentIndex + 1) % SORT_CYCLE.length
        return SORT_CYCLE[nextIndex]
      })
    })
  }
  const onRandomizerSpinComplete = (result: SpinResult) => {
    const decade = result.decade as DecadePill
    startTransition(() => {
      setFallbackRows(null)
      setSpinFallbackDecade(decade)
      setActiveDecades([decade])
      setActiveSpinYear(result.year)
      setActiveYearDigits([])
      setActiveTiers([result.tier.toLowerCase() as TierFilter])
    })
  }
  const onRandomizerToggleDecade = (decade: RandomizerLabel) => {
    startTransition(() => {
      setSpinFallbackDecade(null)
      setFallbackRows(null)
      setActiveSpinYear(null)
      setActiveDecades((prev) => {
        const pill = decade as DecadePill
        return prev.includes(pill) ? prev.filter((value) => value !== pill) : [...prev, pill]
      })
    })
  }
  const onRandomizerToggleDigit = (digit: number) => {
    startTransition(() => {
      setSpinFallbackDecade(null)
      setFallbackRows(null)
      setActiveSpinYear(null)
      setActiveYearDigits((prev) => (prev.includes(digit) ? prev.filter((value) => value !== digit) : [...prev, digit]))
    })
  }
  const onRandomizerToggleTier = (tier: RandomizerTier) => {
    const filterTier = RANDOMIZER_TO_TIER[tier]
    startTransition(() => {
      setSpinFallbackDecade(null)
      setFallbackRows(null)
      setActiveSpinYear(null)
      setActiveTiers((prev) => (prev.includes(filterTier) ? prev.filter((value) => value !== filterTier) : [...prev, filterTier]))
    })
  }
  const onRetentionFilterSelect = (value: RetentionFilter) => {
    startTransition(() => {
      setRetentionFilter(value)
    })
  }
  const onNewnessModeSelect = (value: NewnessMode) => {
    startTransition(() => {
      setNewnessMode(value)
    })
  }
  const runRingPick = () => {
    const decadePool = (activeDecades.length > 0 ? activeDecades : DECADE_PILLS) as readonly RandomizerLabel[]
    const digitPool = activeYearDigits.length > 0 ? activeYearDigits : YEAR_DIGITS
    const tierPool = activeTiers.length > 0 ? activeTiers.map((tier) => TIER_TO_RANDOMIZER[tier]) : RANDOMIZER_TIERS
    const decade = pickRandomValue(decadePool)
    const digit = pickRandomValue(digitPool)
    const tier = pickRandomValue(tierPool)
    const yearBase = Number(DECADE_PILL_TO_DATA_DECADE[decade as DecadePill].slice(0, 4))
    const focusedYear = yearBase + digit

    onRandomizerSpinComplete({
      decade,
      year: focusedYear,
      years: [focusedYear],
      tier,
    })
  }

  return (
    <section className="vl-page">
      <div className="vl-frame">
        <div className="frame-top">
          <div className="header-bar">
            <input
              type="search"
              value={search}
              onChange={(event) => {
                setSpinFallbackDecade(null)
                setFallbackRows(null)
                setSearch(event.target.value)
              }}
              placeholder="Search . ."
              className="search-field search-input"
              aria-label="Search RetroVerse library"
            />
            <div className="video-count">{statusLabel}</div>
          </div>

          <div className="filter-strip">
            <div className="filter-strip-row">
              <button type="button" className="clear-btn filter-row-btn" onClick={clearAllFilters}>
                Clear
              </button>
                <button type="button" className="clear-btn filter-row-btn" onClick={cycleSortMode}>
                {sortButtonPrimed ? SORT_LABELS[sortMode] : 'Sort'}
                </button>
              <button
                type="button"
                className={`filter-trigger filter-row-btn ${isConsoleOpen ? 'is-active' : ''}`}
                onClick={() => (isConsoleOpen ? closeFilterConsole() : openFilterConsole())}
                aria-expanded={isConsoleOpen}
              >
                Filters
              </button>
            </div>
          </div>
        </div>

        <div ref={listRef} className="scrollable-list">
          {error && <div className="placeholder-box">Failed to load: {error}</div>}
          {!error && isFastModeSampling ? (
            <div className="placeholder-box">
              Fast mode is active. Showing a lighter catalog first.
              <div style={{ marginTop: 8 }}>
                <button type="button" className="clear-btn filter-row-btn" onClick={() => setAllowFullCatalogInFastMode(true)}>
                  Load full library
                </button>
              </div>
            </div>
          ) : null}

          {!error && isConsoleOpen && (
            <div className="filter-console">
              <VideoLibraryFilterRings
                matchCount={matchCount}
                matchCountReady={!loading}
                selectedDecades={activeDecades as RandomizerLabel[]}
                selectedDigits={activeYearDigits}
                selectedTiers={activeTiers.map((tier) => TIER_TO_RANDOMIZER[tier])}
                focusedYear={activeSpinYear}
                retentionFilter={retentionFilter}
                newnessMode={newnessMode}
                onToggleDecade={onRandomizerToggleDecade}
                onToggleDigit={onRandomizerToggleDigit}
                onToggleTier={onRandomizerToggleTier}
                onSelectRetention={onRetentionFilterSelect}
                onSelectNewness={onNewnessModeSelect}
                onPick={runRingPick}
                onClearAll={clearAllFilters}
                onClose={closeFilterConsole}
              />
            </div>
          )}

          {!error && !isConsoleOpen && (
            <div className="vl-list">
              {deferredVisibleRows.map((video) => {
                const key = stableVideoHash(video)
                const currentOffset = dragOffset?.id === video.id ? dragOffset.offset : openSwipe === video.id ? -SWIPE_ACTION_WIDTH : 0
                const tierClass = normalizeTierFilter(video.tier)

                return (
                  <article
                    key={key}
                    className={`vl-row-shell card ${tierClass ?? ''}`}
                    onTouchStart={(event) => onRowTouchStart(event, video)}
                    onTouchMove={onRowTouchMove}
                    onTouchEnd={onRowTouchEnd}
                    onTouchCancel={onRowTouchEnd}
                  >
                    <button
                      type="button"
                      className="vl-row-action"
                      onClick={() => onAddToQueue(video)}
                      aria-label={`Add ${video.title} to playlist`}
                    >
                      Add to Playlist
                    </button>

                    <div className="vl-row-surface" style={{ transform: `translateX(${currentOffset}px)` }}>
                      <div className="vl-row-main">
                        <button
                          type="button"
                          className="vl-row-play"
                          onClick={() => video.videoUrl && openPlayer(video, { preferQueue: true })}
                          disabled={!video.videoUrl}
                          aria-label={video.videoUrl ? `Play ${video.title}` : `${video.title} unavailable`}
                        >
                          <div className="vl-thumb" aria-hidden>
                            {video.thumbnailUrl ? <img src={video.thumbnailUrl} alt="" loading="lazy" /> : <div className="thumb-placeholder" />}
                          </div>

                          <div className="vl-text">
                            <div className="vl-title">{video.title}</div>
                            <div className="vl-artist">{video.artist}</div>
                            <div className="meta-line">
                              <div className="meta-left">
                                {formatYear(video.year)} • {formatDuration(video.durationSec)} ▶ {video.playcount}
                              </div>
                            </div>
                          </div>
                        </button>

                        <button
                          type="button"
                          className="vl-info-btn vl-info-btn--row"
                          onClick={() => openInfoModal(video)}
                          aria-label={`Open info for ${video.title}`}
                        >
                          i
                        </button>
                      </div>
                    </div>
                  </article>
                )
              })}

              {!loading && deferredVisibleRows.length === 0 && <div className="placeholder-box">No videos match this search.</div>}
            </div>
          )}
        </div>
      </div>

      {toast && (
        <div className="vl-toast" role="status" aria-live="polite">
          {toast}
        </div>
      )}

      <VideoInfoModal
        video={infoVideo}
        onClose={() => setInfoVideo(null)}
        onAddToQueue={(video) => {
          onAddToQueue(video)
        }}
      />
    </section>
  )
}
