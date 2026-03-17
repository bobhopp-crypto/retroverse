import PerformancePad from './pads/PerformancePad'
import PerformancePadGroup from './pads/PerformancePadGroup'
import SlotCounter from './SlotCounter'
import type { RandomizerLabel, RandomizerTier } from './RetroVerseRandomizer'

type RetentionValue = 'all' | 'S' | 'A' | 'B' | 'C'
type NewnessValue = 'all' | '30d' | '90d' | '1y'

type VideoLibraryFilterRingsProps = {
  matchCount: number
  matchCountReady: boolean
  selectedDecades: RandomizerLabel[]
  selectedDigits: number[]
  selectedTiers: RandomizerTier[]
  focusedYear: number | null
  retentionFilter: RetentionValue
  newnessMode: NewnessValue
  onToggleDecade: (decade: RandomizerLabel) => void
  onToggleDigit: (digit: number) => void
  onToggleTier: (tier: RandomizerTier) => void
  onSelectRetention: (value: RetentionValue) => void
  onSelectNewness: (value: NewnessValue) => void
  onPick: () => void
  onClearAll: () => void
  onClose: () => void
}

const DECADE_VALUES: readonly RandomizerLabel[] = ['60s', '70s', '80s', '90s', '00s', '10s'] as const
const TIER_VALUES: readonly RandomizerTier[] = ['Promo', 'Light', 'Medium', 'Heavy', 'Power'] as const
const RETENTION_VALUES: readonly RetentionValue[] = ['all', 'S', 'A', 'B', 'C'] as const
const DECADE_BASE_YEAR: Record<RandomizerLabel, number> = {
  '60s': 1960,
  '70s': 1970,
  '80s': 1980,
  '90s': 1990,
  '00s': 2000,
  '10s': 2010,
}

const retentionLabel = (value: RetentionValue) => (value === 'all' ? 'All' : value)

export default function VideoLibraryFilterRings({
  matchCount,
  matchCountReady,
  selectedDecades,
  selectedDigits,
  selectedTiers,
  focusedYear,
  retentionFilter,
  newnessMode,
  onToggleDecade,
  onToggleDigit,
  onToggleTier,
  onSelectRetention,
  onSelectNewness,
  onPick,
  onClearAll,
  onClose,
}: VideoLibraryFilterRingsProps) {
  const displayDecade = typeof focusedYear === 'number'
    ? Math.floor(focusedYear / 10) * 10
    : selectedDecades[0]
      ? DECADE_BASE_YEAR[selectedDecades[0]]
      : 1960
  const displayYears = Array.from({ length: 10 }, (_, index) => displayDecade + index)

  return (
    <section className="sb-concentric-panel sb-pad-panel vl-filter-panel" aria-label="Video Library rectangular filter controls">
      <div className="vl-filter-summary">
        <div className="vl-filter-counter">
          <SlotCounter value={matchCount} minSlots={4} ready={matchCountReady} />
        </div>
        <p className="vl-filter-status">
          {typeof focusedYear === 'number' ? `Focused Year ${focusedYear}` : `Year Bank ${displayDecade}s`}
        </p>
      </div>

      <div className="sb-pad-layout">
        <PerformancePadGroup columns={3} className="time-section">
          {DECADE_VALUES.map((decade) => (
            <PerformancePad
              key={decade}
              id={`vl-decade-${decade}`}
              label={decade}
              active={selectedDecades.includes(decade)}
              group="decade"
              onPress={() => onToggleDecade(decade)}
              size="large"
              colorGroup="decade"
            />
          ))}
        </PerformancePadGroup>

        <PerformancePadGroup columns={5} className="time-section">
          {displayYears.map((year) => {
            const digit = year % 10
            const isActive = focusedYear === year || selectedDigits.includes(digit)

            return (
              <PerformancePad
                key={year}
                id={`vl-year-${year}`}
                label={String(year)}
                active={isActive}
                group="year"
                onPress={() => onToggleDigit(digit)}
                size="medium"
                colorGroup="year"
              />
            )
          })}
        </PerformancePadGroup>

        <PerformancePadGroup columns={5} className="energy-section">
          {TIER_VALUES.map((tier) => (
            <PerformancePad
              key={tier}
              id={`vl-tier-${tier.toLowerCase()}`}
              label={tier}
              active={selectedTiers.includes(tier)}
              group="tier"
              onPress={() => onToggleTier(tier)}
              size="medium"
              colorGroup="tier"
            />
          ))}
        </PerformancePadGroup>

        <PerformancePadGroup columns={5} className="count-section">
          {RETENTION_VALUES.map((value) => (
            <PerformancePad
              key={value}
              id={`vl-retention-${value}`}
              label={retentionLabel(value)}
              active={retentionFilter === value}
              group="count"
              onPress={() => onSelectRetention(value)}
              size="small"
              colorGroup="count"
            />
          ))}
        </PerformancePadGroup>

        <div className="sb-scope-row scope-section vl-filter-scope-row" role="group" aria-label="Video Library recency controls">
          <button
            type="button"
            className={`sb-scope-button ${newnessMode === 'all' ? 'is-active' : ''}`}
            onClick={() => onSelectNewness('all')}
          >
            <span className="sb-scope-button-label">Vault</span>
          </button>
          <button
            type="button"
            className={`sb-scope-button ${newnessMode === '30d' ? 'is-active' : ''}`}
            onClick={() => onSelectNewness('30d')}
          >
            <span className="sb-scope-button-label">New</span>
          </button>
          <button
            type="button"
            className={`sb-scope-button ${newnessMode === '90d' ? 'is-active' : ''}`}
            onClick={() => onSelectNewness('90d')}
          >
            <span className="sb-scope-button-label">Recent</span>
          </button>
          <button
            type="button"
            className={`sb-scope-button ${newnessMode === '1y' ? 'is-active' : ''}`}
            onClick={() => onSelectNewness('1y')}
          >
            <span className="sb-scope-button-label">1Y</span>
          </button>
          <button type="button" className="sb-scope-button sb-scope-button--reset" onClick={onClearAll}>
            <span className="sb-scope-button-label">Reset</span>
          </button>
        </div>

        <div className="sb-action-row vl-filter-action-row" role="group" aria-label="Video Library filter actions">
          <button type="button" className="sb-action-button" onClick={onPick}>
            Pick
          </button>
          <button type="button" className="sb-action-button" onClick={onClose}>
            View Results
          </button>
        </div>
      </div>
    </section>
  )
}
