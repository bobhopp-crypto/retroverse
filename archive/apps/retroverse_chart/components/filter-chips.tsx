'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'
import type { FilterType } from '@/lib/types'
import { Calendar } from 'lucide-react'

interface FilterChipsProps {
  activeFilters: FilterType[]
  onFilterToggle: (filter: FilterType) => void
  onRandomYear: () => void
  onPickWeek: (date: string) => void
  onRandomChart: () => void
}

const filters: { label: string; value: FilterType }[] = [
  { label: '#1', value: '#1' },
  { label: 'Top10', value: 'Top10' },
  { label: 'Top40', value: 'Top40' },
]

export function FilterChips({ 
  activeFilters, 
  onFilterToggle, 
  onRandomYear,
  onPickWeek,
  onRandomChart,
}: FilterChipsProps) {
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [dateValue, setDateValue] = useState('')

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setDateValue(value)
    if (value) {
      onPickWeek(value)
      setShowDatePicker(false)
    }
  }

  return (
    <div className="space-y-3">
      {/* Filter Pills - single scrollable row */}
      <div className="filter-row-wrapper">
        <div className="filter-row">
          {filters.map((filter) => {
            const isActive = activeFilters.includes(filter.value)
            return (
              <button
                key={filter.value}
                onClick={() => onFilterToggle(filter.value)}
                className={cn(
                  "filter-pill px-3 py-1.5 rounded-full text-sm font-medium transition-all",
                  "active:scale-95",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                )}
              >
                {filter.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Action Buttons - full width */}
      <div className="actions flex flex-col gap-2.5 mt-2.5">
        <button
          onClick={() => setShowDatePicker(!showDatePicker)}
          className={cn(
            "w-full flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all",
            "active:scale-[0.98]",
            showDatePicker
              ? "bg-primary text-primary-foreground shadow-md"
              : "bg-retro-aqua text-foreground hover:opacity-90"
          )}
        >
          <Calendar className="w-4 h-4" />
          <span>Pick Chart Week</span>
        </button>

        <button
          onClick={onRandomYear}
          className="w-full px-3 py-2.5 rounded-xl text-sm font-medium transition-all bg-retro-coral text-foreground hover:opacity-90 active:scale-[0.98]"
        >
          Random Year
        </button>
      </div>

      {/* Date Picker (appears when Pick Chart Week is clicked) */}
      {showDatePicker && (
        <div className="flex gap-2 mt-2">
          <input
            type="date"
            value={dateValue}
            onChange={handleDateChange}
            min="1958-08-04"
            max="2024-12-28"
            className={cn(
              "px-3 py-1.5 rounded-xl text-sm font-medium",
              "bg-card border border-border text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary"
            )}
          />
        </div>
      )}
    </div>
  )
}
