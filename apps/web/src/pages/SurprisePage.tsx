import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import SurpriseMe from '../components/SurpriseMe'
import './Hub.css'

const MIN_YEAR = 1958

export default function SurprisePage() {
  const currentYear = new Date().getFullYear()

  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <motion.header
        className="page-heading"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.24, ease: 'easeOut' }}
      >
        <h1 className="page-title">Surprise</h1>
      </motion.header>

      <p className="hub-intro max-w-3xl text-[15px] leading-relaxed text-[var(--rv1)]">Spin for a random year, then confirm to enter.</p>

      <section className="mt-6 rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] p-4 shadow-sm sm:p-5">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles size={18} className="text-[var(--rv5)]" />
          <h2 className="m-0 text-lg font-semibold text-[var(--rv1)]">Surprise Me</h2>
        </div>
        <SurpriseMe minYear={MIN_YEAR} maxYear={currentYear} />
      </section>
    </section>
  )
}
