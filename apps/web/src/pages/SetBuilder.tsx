import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import logoMark from '../assets/round-logo.webp'
import PerformancePad from '../components/pads/PerformancePad'
import PerformancePadGroup from '../components/pads/PerformancePadGroup'
import { HISTORY_INDEX_URL } from '../config/dataSources'
import { usePlaylistContext } from '../context/PlaylistContext'
import { loadVideoIndex, type VideoRecord } from '../lib/videoIndex'
import {
  PLAY_TIERS,
  TIER_COLORS,
  YEAR_DOMAIN_MAX,
  YEAR_DOMAIN_MIN,
  angleToYear,
  clamp,
  indexToAngle,
  spanLabel,
  type PlayTierId,
  type TierSelection,
} from './setBuilderUtils'
import { useConcentricRings } from './useConcentricRings'
import './SetBuilder.css'

const TIER_RING_OPTIONS: Array<{ id: TierSelection; label: string }> = [
  { id: 'promo', label: 'Promo' },
  { id: 'light', label: 'Light' },
  { id: 'medium', label: 'Medium' },
  { id: 'heavy', label: 'Heavy' },
  { id: 'power', label: 'Power' },
  { id: 'mixed', label: 'Mixed' },
]

const PAD_DECADES = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020] as const
const PAD_SPANS = [1, 3, 5, 7] as const
type PadSpan = (typeof PAD_SPANS)[number]
const DAY_IN_MS = 24 * 60 * 60 * 1000
const DEFAULT_DECADE = 1950
const DEFAULT_YEAR = 1950
const DEFAULT_COUNT = 10
const INTRO_LINES = ['SELECT THE YEAR', 'TUNE THE LEVEL', 'BUILD THE SET'] as const

const formatShortYear = (year: number) => `'${String(Math.abs(year % 100)).padStart(2, '0')}`

const TIER_VU_LEVEL: Record<PlayTierId, number> = {
  promo: 1,
  light: 2,
  medium: 3,
  heavy: 4,
  power: 5,
}

type ScopeId = 'full' | 'fresh-cuts' | 'deep-current'

const SCOPE_OPTIONS: Array<{ id: ScopeId; label: string; days: number | null }> = [
  { id: 'full', label: 'The Vault', days: null },
  { id: 'fresh-cuts', label: 'New Adds', days: 60 },
  { id: 'deep-current', label: 'Recent', days: 120 },
]

const DEFAULT_SCOPE_ID: ScopeId = 'full'

const parseAddedAt = (row: VideoRecord): number | null => {
  if (row.firstSeenMs) return row.firstSeenMs
  if (row.addedAt) {
    const ms = new Date(row.addedAt).getTime()
    if (Number.isFinite(ms)) return ms
  }
  return null
}

const weightedPick = (
  items: VideoRecord[],
  count: number,
  intensity: number,
  historyWeights: Record<string, number>,
): VideoRecord[] => {
  const available = [...items]
  const picks: VideoRecord[] = []

  while (available.length > 0 && picks.length < count) {
    const weights = available.map((item) => {
      const libraryPlays = Math.max(0, item.playcount)
      const historyPlays = Math.max(0, historyWeights[item.filePath] ?? historyWeights[item.id] ?? 0)
      const combinedPlays = libraryPlays + historyPlays
      const novelty = 1 / (1 + combinedPlays)
      const retention = clamp(item.retentionScore / 100, 0, 1)
      const retentionBias = 0.65 + retention * 1.1
      return retentionBias * (1 + intensity * Math.random() + novelty * (intensity / 2))
    })

    const total = weights.reduce((sum, value) => sum + value, 0)
    let cursor = Math.random() * total
    let selected = 0

    for (let index = 0; index < weights.length; index += 1) {
      cursor -= weights[index]
      if (cursor <= 0) {
        selected = index
        break
      }
    }

    picks.push(available[selected])
    available.splice(selected, 1)
  }

  return picks
}

export default function SetBuilder() {
  const { addManyToQueue, clearQueue, replaceQueue } = usePlaylistContext()

  const [rows, setRows] = useState<VideoRecord[]>([])
  const [historyWeights, setHistoryWeights] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedGenre] = useState('all')
  const [preview, setPreview] = useState<VideoRecord[]>([])
  const [hasGeneratedPreview, setHasGeneratedPreview] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)

  const rings = useConcentricRings({
    initialYear: DEFAULT_YEAR,
    initialSpan: 5,
    initialEraId: 'none',
    initialTier: 'mixed',
    initialCount: DEFAULT_COUNT,
    initialRecency: 'all',
  })

  const [selectedDecade, setSelectedDecade] = useState<number>(DEFAULT_DECADE)
  const [selectedYear, setSelectedYear] = useState<number>(DEFAULT_YEAR)
  const [selectedSpan, setSelectedSpan] = useState<PadSpan | null>(null)
  const [selectedScope, setSelectedScope] = useState<ScopeId>(DEFAULT_SCOPE_ID)
  const [selectedTierIds, setSelectedTierIds] = useState<PlayTierId[]>([])
  const showLegacyWheel = false

  const yearRingRef = useRef<HTMLDivElement | null>(null)
  const activeYearPointerRef = useRef<number | null>(null)

  useEffect(() => {
    let cancelled = false

    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await loadVideoIndex()
        if (!cancelled) setRows(data)
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
  }, [])

  useEffect(() => {
    let cancelled = false

    fetch(HISTORY_INDEX_URL)
      .then((response) => (response.ok ? response.json() : null))
      .then((history) => {
        if (cancelled || !history?.perSong || typeof history.perSong !== 'object') return

        const weights: Record<string, number> = {}
        for (const [songKey, stats] of Object.entries(history.perSong as Record<string, { totalPlays?: unknown }>)) {
          const plays = typeof stats?.totalPlays === 'number' ? stats.totalPlays : 0
          const normalized = songKey.replace(/\\/g, '/')
          const videoMarker = normalized.toUpperCase().indexOf('/VIDEO/')

          if (videoMarker >= 0) {
            const rel = `/VIDEO/${normalized.slice(videoMarker + '/VIDEO/'.length)}`.replace(/\\/g, '/')
            weights[rel] = Math.max(weights[rel] ?? 0, plays)
          }

          weights[songKey] = Math.max(weights[songKey] ?? 0, plays)
        }

        setHistoryWeights(weights)
      })
      .catch(() => {
        if (!cancelled) setHistoryWeights({})
      })

    return () => {
      cancelled = true
    }
  }, [])

  const yearsForSelectedDecade = useMemo(() => {
    const decadeEnd = Math.min(selectedDecade + 9, YEAR_DOMAIN_MAX)
    const years: number[] = []
    for (let year = selectedDecade; year <= decadeEnd; year += 1) years.push(year)
    return years
  }, [selectedDecade])

  const effectiveRange = useMemo(() => {
    const resolvedSpan = selectedSpan ?? 0
    const start = selectedYear - resolvedSpan
    const end = selectedYear + resolvedSpan
    return { start: Math.min(start, end), end: Math.max(start, end) }
  }, [selectedSpan, selectedYear])

  const hasTierFilter = selectedTierIds.length > 0
  const activeTierIds = useMemo(() => new Set(selectedTierIds), [selectedTierIds])

  const tierStatusLabel = useMemo(() => {
    if (selectedTierIds.length === 0) return 'All Energy Levels'

    const selectedLabels = PLAY_TIERS.filter((tier) => selectedTierIds.includes(tier.id)).map((tier) => tier.label)
    if (selectedLabels.length === 0) return 'All Energy Levels'

    return `Energy: ${selectedLabels.join(' + ')}`
  }, [selectedTierIds])

  const selectedScopeDays = useMemo(() => SCOPE_OPTIONS.find((scope) => scope.id === selectedScope)?.days ?? null, [selectedScope])

  const rowMatchesScope = useCallback((row: VideoRecord, scopeDays: number | null, nowMs: number) => {
    if (scopeDays === null) return true
    const timestamp = parseAddedAt(row)
    if (!timestamp) return false
    return timestamp >= nowMs - scopeDays * DAY_IN_MS
  }, [])

  const rowMatchesBaseFilters = useCallback(
    (row: VideoRecord) => {
      if (hasTierFilter) {
        const rowTier = row.tier ? row.tier.toLowerCase() : ''
        if (!activeTierIds.has(rowTier as PlayTierId)) return false
      }

      if (typeof row.year !== 'number') return false
      if (row.year < effectiveRange.start || row.year > effectiveRange.end) return false

      if (selectedGenre !== 'all' && row.genre !== selectedGenre) return false

      return true
    },
    [activeTierIds, effectiveRange, hasTierFilter, selectedGenre],
  )

  const filtered = useMemo(() => {
    const nowMs = Date.now()
    return rows.filter((row) => rowMatchesBaseFilters(row) && rowMatchesScope(row, selectedScopeDays, nowMs))
  }, [rowMatchesBaseFilters, rowMatchesScope, rows, selectedScopeDays])

  const scopeCounts = useMemo(() => {
    const nowMs = Date.now()
    const counts: Record<ScopeId, number> = {
      full: 0,
      'fresh-cuts': 0,
      'deep-current': 0,
    }

    for (const row of rows) {
      if (!rowMatchesBaseFilters(row)) continue
      for (const scope of SCOPE_OPTIONS) {
        if (rowMatchesScope(row, scope.days, nowMs)) {
          counts[scope.id] += 1
        }
      }
    }

    return counts
  }, [rowMatchesBaseFilters, rowMatchesScope, rows])

  const matchCount = filtered.length
  const previewRows = useMemo(() => preview.slice(0, 25), [preview])

  const crtRangeValue = effectiveRange.start === effectiveRange.end ? String(effectiveRange.start) : `${effectiveRange.start} — ${effectiveRange.end}`
  const crtTierValue = tierStatusLabel
  const crtCountValue = `${matchCount} tracks available`

  useEffect(() => {
    setPreview([])
    setHasGeneratedPreview(false)
  }, [rings.selectedCount, selectedDecade, selectedScope, selectedSpan, selectedTierIds, selectedYear])

  const updateYearFromPointer = useCallback(
    (clientX: number, clientY: number) => {
      const node = yearRingRef.current
      if (!node) return

      const bounds = node.getBoundingClientRect()
      const centerX = bounds.left + bounds.width / 2
      const centerY = bounds.top + bounds.height / 2

      const rawAngle = Math.atan2(clientY - centerY, clientX - centerX) * (180 / Math.PI)
      const ringAngle = rawAngle + 90
      const snappedYear = angleToYear(ringAngle)
      rings.setSelectedYear(snappedYear)
    },
    [rings.setSelectedYear],
  )

  const onYearPointerDown = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      event.preventDefault()
      activeYearPointerRef.current = event.pointerId
      event.currentTarget.setPointerCapture(event.pointerId)
      updateYearFromPointer(event.clientX, event.clientY)
    },
    [updateYearFromPointer],
  )

  const onYearPointerMove = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      if (activeYearPointerRef.current !== event.pointerId) return
      updateYearFromPointer(event.clientX, event.clientY)
    },
    [updateYearFromPointer],
  )

  const onYearPointerUp = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (activeYearPointerRef.current !== event.pointerId) return
    activeYearPointerRef.current = null
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }, [])

  const onSelectDecade = useCallback(
    (decade: number) => {
      setSelectedDecade(decade)
      setSelectedYear(decade)
      rings.setSelectedYear(decade)
    },
    [rings.setSelectedYear],
  )

  const onSelectYear = useCallback(
    (year: number) => {
      setSelectedYear(year)
      rings.setSelectedYear(year)
    },
    [rings.setSelectedYear],
  )

  const onSelectSpan = useCallback(
    (span: PadSpan) => {
      setSelectedSpan((current) => (current === span ? null : span))
    },
    [],
  )

  const onToggleTier = useCallback((tierId: PlayTierId) => {
    setSelectedTierIds((prev) => (prev.includes(tierId) ? prev.filter((value) => value !== tierId) : [...prev, tierId]))
  }, [])

  const onSelectCount = useCallback(
    (count: number) => {
      rings.setSelectedCount(count as (typeof rings.countOptions)[number])
    },
    [rings.setSelectedCount],
  )

  const onSelectScope = useCallback((scopeId: ScopeId) => {
    setSelectedScope(scopeId)
  }, [])

  useEffect(() => {
    if (selectedTierIds.length === 1) {
      rings.setSelectedTier(selectedTierIds[0])
      return
    }
    rings.setSelectedTier('mixed')
  }, [rings.setSelectedTier, selectedTierIds])

  const handleGenerate = useCallback(() => {
    setPreview(weightedPick(filtered, clamp(rings.selectedCount, 1, 50), 5, historyWeights))
    setHasGeneratedPreview(true)
  }, [filtered, historyWeights, rings.selectedCount])

  const handleAddToQueue = useCallback(() => {
    addManyToQueue(preview)
  }, [addManyToQueue, preview])

  const handleReplaceQueue = useCallback(() => {
    replaceQueue(preview)
  }, [preview, replaceQueue])

  const handleReset = useCallback(() => {
    setSelectedDecade(DEFAULT_DECADE)
    setSelectedYear(DEFAULT_YEAR)
    setSelectedSpan(null)
    setSelectedTierIds([])
    setSelectedScope(DEFAULT_SCOPE_ID)
    setPreview([])
    setHasGeneratedPreview(false)
    clearQueue()
    rings.setSelectedYear(DEFAULT_YEAR)
    rings.setSelectedCount(DEFAULT_COUNT)
    rings.setSelectedTier('mixed')
    rings.setSelectedRecency('all')
    setShowPreview(false)
    setHasInteracted(false)
  }, [clearQueue, rings.setSelectedCount, rings.setSelectedRecency, rings.setSelectedTier, rings.setSelectedYear])

  useEffect(() => {
    handleReset()
  }, [handleReset])

  const queueActionDisabled = preview.length === 0
  const onAirLive = hasInteracted && matchCount > 0
  const vuLevel = useMemo(() => {
    if (selectedTierIds.length === 0) return 0
    return selectedTierIds.reduce((level, tierId) => Math.max(level, TIER_VU_LEVEL[tierId]), 0)
  }, [selectedTierIds])

  const yearTicks = useMemo(
    () => Array.from({ length: Math.floor((YEAR_DOMAIN_MAX - YEAR_DOMAIN_MIN) / 10) + 1 }, (_, index) => YEAR_DOMAIN_MIN + index * 10),
    [],
  )

  const markFirstInteraction = useCallback(() => {
    setHasInteracted((previous) => (previous ? previous : true))
  }, [])

  const consoleStyle = useMemo(
    () => ({
      '--sb-tier-accent': selectedTierIds.length === 1 ? TIER_COLORS[selectedTierIds[0]] : TIER_COLORS.mixed,
      '--sb-tier-surface': selectedTierIds.length === 1 ? TIER_COLORS[selectedTierIds[0]] : TIER_COLORS.mixed,
    }) as CSSProperties,
    [selectedTierIds],
  )

  return (
    <section className="stack random-page">
      {error && <div className="placeholder-box">Failed to load: {error}</div>}

      <div className="sb-console" style={consoleStyle}>
        <header className="sb-header" aria-live="polite">
          <div className="sb-on-air" aria-label={onAirLive ? 'On air ready' : 'On air idle'}>
            <span className={`sb-on-air-light ${onAirLive ? 'is-live' : 'is-idle'}`} aria-hidden />
            <span className="sb-on-air-label">ON AIR</span>
          </div>

          <div className="sb-header-stack">
            <div className="sb-broadcast-panel">
              <div className={`sb-panel-state sb-panel-state--intro ${hasInteracted ? '' : 'is-visible'}`} aria-hidden={hasInteracted}>
                {INTRO_LINES.map((line) => (
                  <p key={line} className="sb-intro-line">
                    {line}
                  </p>
                ))}
              </div>

              <div className={`sb-panel-state sb-panel-state--active ${hasInteracted ? 'is-visible' : ''}`} aria-hidden={!hasInteracted}>
                <div className="sb-display-stack">
                  <div className="sb-active-range-shell">
                    <p className="sb-active-range">{crtRangeValue}</p>
                  </div>
                  <p className="sb-active-tier" title={crtTierValue}>
                    {crtTierValue}
                  </p>
                  <p className="sb-active-count">{crtCountValue}</p>
                </div>
              </div>
            </div>

            <div className="sb-vu" aria-hidden>
              {Array.from({ length: 5 }, (_, index) => (
                <span
                  key={index}
                  className={`sb-vu-bar ${index < vuLevel ? 'is-lit' : ''}`}
                  style={{ '--sb-vu-index': index + 1 } as CSSProperties}
                />
              ))}
            </div>
          </div>
        </header>

        {showLegacyWheel ? (
          <section
            className="sb-concentric-panel"
            aria-label="Set Builder concentric controls"
            onPointerDownCapture={markFirstInteraction}
            onKeyDownCapture={markFirstInteraction}
            onFocusCapture={markFirstInteraction}
          >
            <div className="sb-ring-arena">
              <div
                ref={yearRingRef}
                className="sb-ring sb-ring--year"
                onPointerDown={onYearPointerDown}
                onPointerMove={onYearPointerMove}
                onPointerUp={onYearPointerUp}
                onPointerCancel={onYearPointerUp}
                role="slider"
                aria-valuemin={YEAR_DOMAIN_MIN}
                aria-valuemax={YEAR_DOMAIN_MAX}
                aria-valuenow={rings.selectedYear}
                aria-label="Year selector"
              >
                <span className="sb-ring-bezel" aria-hidden />
                <span className="sb-ring-label">YEAR SELECTOR</span>
                <span className="sb-ring-pointer" style={{ '--ring-angle': `${rings.yearAngle}deg` } as CSSProperties} aria-hidden>
                  <span className="sb-ring-pointer-head" />
                </span>
                <span className="sb-ring-value">{rings.selectedYear}</span>
                <div className="sb-ring-markers" aria-hidden>
                  {yearTicks.map((tick, index) => (
                    <span
                      key={tick}
                      className="sb-ring-marker"
                      style={{ '--ring-angle': `${indexToAngle(index, yearTicks.length)}deg` } as CSSProperties}
                    >
                      {String(tick).slice(2)}
                    </span>
                  ))}
                </div>
              </div>

              <div className="sb-ring sb-ring--span" aria-label="Span selector">
                <span className="sb-ring-bezel" aria-hidden />
                <span className="sb-ring-label">SPAN SELECTOR</span>
                <span className="sb-ring-pointer sb-ring-pointer--secondary" style={{ '--ring-angle': `${rings.spanAngle}deg` } as CSSProperties} aria-hidden>
                  <span className="sb-ring-pointer-head" />
                </span>
                {rings.spanOptions.map((span, index) => (
                  <button
                    key={span}
                    type="button"
                    className={`sb-ring-chip ${rings.selectedSpan === span ? 'is-active' : ''}`}
                    style={{ '--ring-angle': `${indexToAngle(index, rings.spanOptions.length)}deg` } as CSSProperties}
                    onClick={() => rings.setSelectedSpan(span)}
                  >
                    {spanLabel(span)}
                  </button>
                ))}
              </div>

              <div className="sb-ring sb-ring--era" aria-label="Era selector">
                <span className="sb-ring-bezel" aria-hidden />
                <span className="sb-ring-label">ERA FILTER</span>
                <span className="sb-ring-pointer sb-ring-pointer--secondary" style={{ '--ring-angle': `${rings.eraAngle}deg` } as CSSProperties} aria-hidden>
                  <span className="sb-ring-pointer-head" />
                </span>
                {rings.eraOptions.map((era, index) => (
                  <button
                    key={era.id}
                    type="button"
                    className={`sb-ring-chip sb-ring-chip--era ${rings.selectedEraId === era.id ? 'is-active' : ''}`}
                    style={{ '--ring-angle': `${indexToAngle(index, rings.eraOptions.length)}deg` } as CSSProperties}
                    onClick={() => rings.setSelectedEraId(era.id)}
                  >
                    {era.label}
                  </button>
                ))}
              </div>

              <div className="sb-ring sb-ring--tier" aria-label="Rotation tier selector">
                <span className="sb-ring-bezel" aria-hidden />
                <span className="sb-ring-label">ROTATION TIER</span>
                <span className="sb-ring-pointer sb-ring-pointer--secondary" style={{ '--ring-angle': `${rings.tierAngle}deg` } as CSSProperties} aria-hidden>
                  <span className="sb-ring-pointer-head" />
                </span>
                {TIER_RING_OPTIONS.map((tier, index) => (
                  <button
                    key={tier.id}
                    type="button"
                    className={`sb-ring-chip sb-ring-chip--tier ${rings.selectedTier === tier.id ? 'is-active' : ''}`}
                    style={{
                      '--ring-angle': `${indexToAngle(index, TIER_RING_OPTIONS.length)}deg`,
                      '--chip-tier-color': TIER_COLORS[tier.id],
                    } as CSSProperties}
                    onClick={() => rings.setSelectedTier(tier.id)}
                  >
                    {tier.label}
                  </button>
                ))}
              </div>

              <div className="sb-ring sb-ring--count" aria-label="Count selector">
                <span className="sb-core-watermark" aria-hidden>
                  <img src={logoMark} alt="" />
                </span>
                <span className="sb-ring-pointer sb-ring-pointer--core" style={{ '--ring-angle': `${rings.countAngle}deg` } as CSSProperties} aria-hidden>
                  <span className="sb-ring-pointer-head" />
                </span>
                {rings.countOptions.map((count, index) => (
                  <button
                    key={count}
                    type="button"
                    className={`sb-core-chip ${rings.selectedCount === count ? 'is-active' : ''}`}
                    style={{ '--ring-angle': `${indexToAngle(index, rings.countOptions.length)}deg` } as CSSProperties}
                    onClick={() => rings.setSelectedCount(count)}
                  >
                    {count}
                  </button>
                ))}
                <span className="sb-core-value">{rings.selectedCount}</span>
                <span className="sb-ring-label sb-ring-label--core">COUNT SELECTOR</span>
              </div>
            </div>
          </section>
        ) : (
          <section
            className="sb-concentric-panel sb-pad-panel"
            aria-label="Set Builder performance pad controls"
            onPointerDownCapture={markFirstInteraction}
            onKeyDownCapture={markFirstInteraction}
            onFocusCapture={markFirstInteraction}
          >
            <div className="sb-pad-layout">
              <PerformancePadGroup title="Decade" columns={4} className="time-section">
                {PAD_DECADES.map((decade) => (
                  <PerformancePad
                    key={decade}
                    id={`sb-decade-${decade}`}
                    label={`${decade}s`}
                    active={selectedDecade === decade}
                    group="decade"
                    onPress={() => onSelectDecade(decade)}
                    size="large"
                    colorGroup="decade"
                  />
                ))}
              </PerformancePadGroup>

              <PerformancePadGroup title="Year" columns={5} className="time-section">
                {yearsForSelectedDecade.map((year) => (
                  <PerformancePad
                    key={year}
                    id={`sb-year-${year}`}
                    label={String(year)}
                    active={selectedYear === year}
                    group="year"
                    onPress={() => onSelectYear(year)}
                    size="medium"
                    colorGroup="year"
                  />
                ))}
              </PerformancePadGroup>

              <PerformancePadGroup title="Span" columns={4} className="time-section">
                {PAD_SPANS.map((span, index) => (
                  <PerformancePad
                    key={span}
                    id={`sb-span-${span}`}
                    label={`${formatShortYear(selectedYear - span)} to ${formatShortYear(selectedYear + span)}`}
                    active={selectedSpan === span}
                    group="span"
                    onPress={() => onSelectSpan(span)}
                    size="small"
                    colorGroup="span"
                    toneIndex={index}
                    toneCount={PAD_SPANS.length}
                  />
                ))}
              </PerformancePadGroup>

              <PerformancePadGroup title="Tier" columns={5} className="energy-section">
                {PLAY_TIERS.map((tier, index) => (
                  <PerformancePad
                    key={tier.id}
                    id={`sb-tier-${tier.id}`}
                    label={tier.label}
                    active={selectedTierIds.includes(tier.id)}
                    group="tier"
                    onPress={() => onToggleTier(tier.id)}
                    size="medium"
                    colorGroup="tier"
                    toneIndex={index}
                    toneCount={PLAY_TIERS.length}
                  />
                ))}
              </PerformancePadGroup>

              <PerformancePadGroup title="Count" columns={5} className="count-section">
                {rings.countOptions.map((count, index) => (
                  <PerformancePad
                    key={count}
                    id={`sb-count-${count}`}
                    label={String(count)}
                    active={rings.selectedCount === count}
                    group="count"
                    onPress={() => onSelectCount(count)}
                    size="small"
                    colorGroup="count"
                    toneIndex={index}
                    toneCount={rings.countOptions.length}
                  />
                ))}
              </PerformancePadGroup>

              <div className="sb-scope-row scope-section" role="group" aria-label="Set Builder scope controls">
                {SCOPE_OPTIONS.map((scope) => (
                  <button
                    key={scope.id}
                    type="button"
                    className={`sb-scope-button ${selectedScope === scope.id ? 'is-active' : ''}`}
                    onClick={() => onSelectScope(scope.id)}
                    aria-pressed={selectedScope === scope.id}
                  >
                    <span className="sb-scope-button-label">{scope.label}</span>
                    <span className="sb-scope-button-count">{scopeCounts[scope.id]}</span>
                  </button>
                ))}
                <button type="button" className="sb-scope-button sb-scope-button--reset" onClick={handleReset}>
                  <span className="sb-scope-button-label">Reset</span>
                  <span className="sb-scope-button-count">{matchCount}</span>
                </button>
              </div>
            </div>
          </section>
        )}

        <section
          className="sb-action-row"
          aria-label="Set Builder action controls"
          onPointerDownCapture={markFirstInteraction}
          onKeyDownCapture={markFirstInteraction}
          onFocusCapture={markFirstInteraction}
        >
          <button type="button" className="sb-action-button" onClick={handleGenerate}>
            Generate
          </button>
          <button type="button" className="sb-action-button" onClick={handleAddToQueue} disabled={queueActionDisabled}>
            Add Queue
          </button>
          <button type="button" className="sb-action-button" onClick={handleReplaceQueue} disabled={queueActionDisabled}>
            Replace Queue
          </button>
          <button
            type="button"
            className={`sb-action-button ${showPreview ? 'is-active' : ''}`}
            onClick={() => setShowPreview((prev) => !prev)}
            aria-expanded={showPreview}
            aria-controls="sb-preview-drawer"
            aria-live="polite"
          >
            Preview
          </button>
        </section>

        {showPreview && (
          <section id="sb-preview-drawer" className="sb-preview-drawer" aria-label="Set Builder preview drawer">
            {loading ? (
              <p className="sb-preview-empty">Loading matches...</p>
            ) : !hasGeneratedPreview ? (
              <p className="sb-preview-empty">Press Generate to build a preview.</p>
            ) : previewRows.length === 0 ? (
              <p className="sb-preview-empty">No matches with current controls.</p>
            ) : (
              <ol className="sb-preview-list">
                {previewRows.map((row) => (
                  <li key={row.id} className="sb-preview-item">
                    <strong>{row.title}</strong>
                    <span>
                      {row.artist} · {typeof row.year === 'number' ? row.year : '----'}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </section>
        )}
      </div>
    </section>
  )
}
