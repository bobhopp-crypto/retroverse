import { motion } from 'framer-motion'

type YearRevealProps = {
  year: number
  onEnter: () => void
  onBack: () => void
}

const buttonClassName =
  'inline-flex w-full items-center justify-center rounded-xl border border-[var(--rv2)] px-4 py-2.5 text-sm font-semibold shadow-sm transition hover:-translate-y-0.5 hover:brightness-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

export default function YearReveal({ year, onEnter, onBack }: YearRevealProps) {
  return (
    <motion.section
      className="rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] p-5 shadow-sm"
      initial={{ opacity: 0, scale: 0.96, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.24, ease: 'easeOut' }}
    >
      <div className="text-center">
        <p className="m-0 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--rv1)]">Year Reveal</p>
        <h1 className="m-0 mt-1 font-['Baloo_2','Fredoka',sans-serif] text-6xl font-bold leading-none text-[var(--rv1)] sm:text-7xl">
          {year}
        </h1>
        <p className="m-0 mt-3 text-base text-[var(--rv1)]">Entering the Year</p>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button type="button" onClick={onEnter} className={`${buttonClassName} bg-[var(--rv5)] text-[var(--rv3)]`}>
          ENTER {year}
        </button>
        <button type="button" onClick={onBack} className={`${buttonClassName} bg-[var(--rv4)] text-[var(--rv1)]`}>
          BACK
        </button>
      </div>
    </motion.section>
  )
}
