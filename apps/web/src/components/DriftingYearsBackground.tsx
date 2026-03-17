import { motion } from 'framer-motion'
import { useMemo } from 'react'

type DriftingYearsBackgroundProps = {
  minYear: number
  maxYear: number
  count?: number
}

type DriftingYear = {
  id: string
  year: number
  left: number
  top: number
  driftX: number
  driftY: number
  duration: number
  delay: number
  fontSize: number
}

function createDeterministicYears(minYear: number, maxYear: number, count: number): DriftingYear[] {
  let seed = 197401
  const next = () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296
    return seed / 4294967296
  }

  return Array.from({ length: count }, (_, index) => {
    const year = Math.floor(next() * (maxYear - minYear + 1)) + minYear
    return {
      id: `drift-${year}-${index}`,
      year,
      left: next() * 100,
      top: next() * 100,
      driftX: next() * 36 - 18,
      driftY: next() * 44 - 22,
      duration: 24 + next() * 20,
      delay: next() * 6,
      fontSize: 14 + next() * 20,
    }
  })
}

export default function DriftingYearsBackground({ minYear, maxYear, count = 28 }: DriftingYearsBackgroundProps) {
  const driftingYears = useMemo(() => createDeterministicYears(minYear, maxYear, count), [minYear, maxYear, count])

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {driftingYears.map((entry) => (
        <motion.span
          key={entry.id}
          className="absolute select-none font-semibold tracking-widest"
          style={{
            left: `${entry.left}%`,
            top: `${entry.top}%`,
            fontSize: `${entry.fontSize}px`,
            color: 'var(--rv1)',
          }}
          initial={{ opacity: 0.05 }}
          animate={{
            opacity: [0.05, 0.14, 0.05],
            x: [0, entry.driftX, -entry.driftX * 0.6, 0],
            y: [0, -entry.driftY, entry.driftY * 0.5, 0],
          }}
          transition={{
            duration: entry.duration,
            repeat: Number.POSITIVE_INFINITY,
            delay: entry.delay,
            ease: 'easeInOut',
          }}
        >
          {entry.year}
        </motion.span>
      ))}
    </div>
  )
}
