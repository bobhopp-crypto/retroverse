import { motion } from 'framer-motion'
import { Compass } from 'lucide-react'
import { useMemo } from 'react'
import DriftingYearsBackground from '../components/DriftingYearsBackground'
import ExploreDecades from '../components/ExploreDecades'

const MIN_YEAR = 1958

const panelClassName = 'rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] p-4 shadow-sm sm:p-5'

export default function LandingPage() {
  const currentYear = useMemo(() => new Date().getFullYear(), [])

  return (
    <section
      className="relative min-h-[calc(100vh-128px)] overflow-hidden rounded-[18px] border border-[var(--rv2)] p-4 sm:p-6"
      style={{
        background: 'linear-gradient(155deg, var(--rv4) 0%, var(--rv3) 52%, var(--rv4) 100%)',
      }}
    >
      <DriftingYearsBackground minYear={MIN_YEAR} maxYear={currentYear} />

      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(circle at 10% 18%, var(--rv5) 0%, transparent 38%), radial-gradient(circle at 86% 78%, var(--rv4) 0%, transparent 36%)',
          opacity: 0.18,
        }}
      />

      <div className="relative z-10 mx-auto flex w-full max-w-5xl flex-col gap-4">
        <motion.header
          className={panelClassName}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
        >
          <p className="m-0 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--rv1)]">RetroVerse</p>
          <h1 className="m-0 mt-1 font-['Baloo_2','Fredoka',sans-serif] text-4xl font-bold text-[var(--rv1)] sm:text-5xl">
            Explore
          </h1>
          <p className="m-0 mt-2 text-base text-[var(--rv1)]">Choose a decade to begin.</p>
        </motion.header>

        <motion.section
          className={panelClassName}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.06, ease: 'easeOut' }}
        >
          <div className="mb-3 flex items-center gap-2">
            <Compass size={18} className="text-[var(--rv5)]" />
            <h2 className="m-0 text-lg font-semibold text-[var(--rv1)]">Explore</h2>
          </div>
          <ExploreDecades />
        </motion.section>
      </div>
    </section>
  )
}
