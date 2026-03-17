import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import YearReveal from './YearReveal'

type SurpriseMeProps = {
  minYear: number
  maxYear: number
}

function randomInRange(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

const spinButtonClassName =
  'inline-flex items-center justify-center gap-2 rounded-xl border border-[var(--rv2)] bg-[var(--rv5)] px-4 py-2.5 text-sm font-semibold text-[var(--rv3)] shadow-sm transition hover:-translate-y-0.5 hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

export default function SurpriseMe({ minYear, maxYear }: SurpriseMeProps) {
  const navigate = useNavigate()
  const [displayYear, setDisplayYear] = useState(maxYear)
  const [revealedYear, setRevealedYear] = useState<number | null>(null)
  const [isSpinning, setIsSpinning] = useState(false)
  const spinIntervalRef = useRef<number | null>(null)
  const spinTimeoutRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (spinIntervalRef.current !== null) {
        window.clearInterval(spinIntervalRef.current)
      }
      if (spinTimeoutRef.current !== null) {
        window.clearTimeout(spinTimeoutRef.current)
      }
    }
  }, [])

  const runSpin = () => {
    if (isSpinning) {
      return
    }

    setRevealedYear(null)
    setIsSpinning(true)

    spinIntervalRef.current = window.setInterval(() => {
      setDisplayYear(randomInRange(minYear, maxYear))
    }, 70)

    const spinDurationMs = randomInRange(2200, 3000)
    spinTimeoutRef.current = window.setTimeout(() => {
      if (spinIntervalRef.current !== null) {
        window.clearInterval(spinIntervalRef.current)
        spinIntervalRef.current = null
      }

      const finalYear = randomInRange(minYear, maxYear)
      setDisplayYear(finalYear)
      setRevealedYear(finalYear)
      setIsSpinning(false)
    }, spinDurationMs)
  }

  if (revealedYear !== null) {
    return <YearReveal year={revealedYear} onEnter={() => navigate(`/year/${revealedYear}`)} onBack={() => setRevealedYear(null)} />
  }

  return (
    <section className="space-y-4">
      <motion.div
        className="rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] p-5 text-center shadow-sm"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.24, ease: 'easeOut' }}
      >
        <p className="m-0 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--rv1)]">Surprise Machine</p>
        <div className="mt-2 rounded-xl border border-[var(--rv2)] bg-[var(--rv4)] px-4 py-6">
          <p className="m-0 font-['Baloo_2','Fredoka',sans-serif] text-6xl font-bold leading-none text-[var(--rv1)] sm:text-7xl">{displayYear}</p>
        </div>
        <p className="m-0 mt-3 text-sm text-[var(--rv1)]">Press SPIN to roll through years from 1958 to today.</p>
      </motion.div>

      <div className="flex justify-center">
        <button type="button" onClick={runSpin} disabled={isSpinning} className={spinButtonClassName}>
          <Sparkles size={16} />
          {isSpinning ? 'SPINNING...' : 'SPIN'}
        </button>
      </div>
    </section>
  )
}
