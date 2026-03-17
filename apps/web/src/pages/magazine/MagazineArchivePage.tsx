import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { MAGAZINE_AVAILABLE_ISSUES, MAGAZINE_YEAR_INDEX } from '../../data/magazineIssues'

const issueCardClassName =
  'group flex min-h-24 items-center justify-between rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] p-4 text-[var(--rv1)] shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--rv5)] hover:brightness-[1.02] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

export default function MagazineArchivePage() {
  const availableSet = new Set(MAGAZINE_AVAILABLE_ISSUES)

  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <header className="page-heading">
        <h1 className="page-title">Magazine</h1>
      </header>
      <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">Select a year to open the issue reader.</p>

      <section className="mt-6 rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] p-4 shadow-sm sm:p-5">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {MAGAZINE_YEAR_INDEX.map((year) => (
            <Link key={year} to={`/magazine/${year}`} className={issueCardClassName}>
              <div>
                <p className="m-0 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">Issue</p>
                <p className="m-0 mt-1 text-2xl font-bold text-[var(--rv1)]">{year}</p>
                <p className="m-0 mt-1 text-xs font-semibold uppercase tracking-[0.06em] text-[var(--rv5)]">
                  {availableSet.has(year) ? 'Featured Content' : 'Chart Summary'}
                </p>
              </div>
              <BookOpen size={20} className="text-[var(--rv5)]" />
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-6 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Link to="/art-department" className={issueCardClassName}>
          <div>
            <p className="m-0 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">Department</p>
            <p className="m-0 mt-1 text-2xl font-bold text-[var(--rv1)]">Art Department</p>
            <p className="m-0 mt-1 text-xs font-semibold uppercase tracking-[0.06em] text-[var(--rv5)]">Profiles, Portraits, Reference Work</p>
          </div>
          <BookOpen size={20} className="text-[var(--rv5)]" />
        </Link>

        <Link to="/art-director" className={issueCardClassName}>
          <div>
            <p className="m-0 text-xs font-semibold uppercase tracking-[0.08em] text-[var(--rv1)]">Tool</p>
            <p className="m-0 mt-1 text-2xl font-bold text-[var(--rv1)]">Art Director</p>
            <p className="m-0 mt-1 text-xs font-semibold uppercase tracking-[0.06em] text-[var(--rv5)]">Rank Artists by Project, Era, Tone</p>
          </div>
          <BookOpen size={20} className="text-[var(--rv5)]" />
        </Link>
      </section>
    </section>
  )
}
