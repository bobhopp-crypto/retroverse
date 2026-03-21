// trigger redeploy
import { Link } from 'react-router-dom'

const MIN_YEAR = 1958
const MAX_YEAR = 2024
const YEARS = Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i)

export default function MagazineIndex() {
  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <header className="page-heading">
        <h1 className="page-title">Magazine</h1>
        <p className="hub-intro">Select a year to open the issue.</p>
      </header>

      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-2 mt-6">
        {YEARS.map((year) => (
          <Link
            key={year}
            to={`/magazine/${year}`}
            className="flex items-center justify-center rounded-lg border border-[var(--rv2)] bg-[var(--rv3)] p-3 text-center font-semibold text-[var(--rv1)] hover:border-[var(--rv5)]"
          >
            {year}
          </Link>
        ))}
      </div>
    </section>
  )
}
