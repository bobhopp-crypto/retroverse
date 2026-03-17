import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import YearReveal from '../components/YearReveal'
import { Panel } from '../components/ui/Card'
import './Hub.css'

function parseDecadeStart(decadeParam?: string): number | null {
  if (!decadeParam) {
    return null
  }

  const decadeMatch = decadeParam.match(/^(\d{4})s$/)
  if (!decadeMatch) {
    return null
  }

  return Number(decadeMatch[1])
}

const backLinkClassName =
  'inline-flex items-center gap-2 rounded-lg border border-[var(--rv2)] bg-[var(--rv4)] px-3 py-2 text-sm font-semibold text-[var(--rv1)] transition hover:brightness-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

const yearButtonClassName =
  'group flex min-h-[4.5rem] h-full items-center justify-center rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] p-3.5 text-[var(--rv1)] shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--rv5)] hover:brightness-[1.02] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

export default function DecadePage() {
  const navigate = useNavigate()
  const { decade } = useParams<{ decade: string }>()
  const decadeStart = parseDecadeStart(decade)
  const [selectedYear, setSelectedYear] = useState<number | null>(null)

  if (decadeStart === null) {
    return (
      <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
        <header className="page-heading">
          <h1 className="page-title">Decade</h1>
        </header>
        <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">Explore the decade</p>

        <Panel className="mt-6 p-5">
          <p className="m-0 text-sm text-[var(--rv1)]">The requested decade is not available.</p>
          <Link to="/" className="mt-3 inline-flex">
            <span className={backLinkClassName}>
              <ArrowLeft size={15} />
              Back to Explore
            </span>
          </Link>
        </Panel>
      </section>
    )
  }

  const years = Array.from({ length: 10 }, (_, index) => decadeStart + index)
  const heading = `${decadeStart}s`

  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <header className="page-heading">
        <h1 className="page-title">{heading}</h1>
        <Link to="/" className={backLinkClassName}>
          <ArrowLeft size={15} />
          Explore
        </Link>
      </header>
      <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">Choose a year</p>

      <section className="mt-6">
        {selectedYear === null ? (
          <Panel className="p-4 sm:p-5">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
              {years.map((year) => (
                <button key={year} type="button" onClick={() => setSelectedYear(year)} className={yearButtonClassName}>
                  <span className="text-base font-semibold tracking-tight text-[var(--rv1)]">{year}</span>
                </button>
              ))}
            </div>
          </Panel>
        ) : (
          <YearReveal
            year={selectedYear}
            onEnter={() => navigate(`/year/${selectedYear}`)}
            onBack={() => setSelectedYear(null)}
          />
        )}
      </section>
    </section>
  )
}
