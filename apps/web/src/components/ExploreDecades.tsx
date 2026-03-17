import { CalendarRange } from 'lucide-react'
import { Link } from 'react-router-dom'

const DEFAULT_DECADES = ['1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']

type ExploreDecadesProps = {
  decades?: string[]
}

const decadeCardClassName =
  'group flex min-h-20 items-center justify-between rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] p-4 text-[var(--rv1)] shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--rv5)] hover:brightness-[1.01] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

export default function ExploreDecades({ decades = DEFAULT_DECADES }: ExploreDecadesProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {decades.map((decade) => (
        <Link key={decade} to={`/decade/${decade}`} className={decadeCardClassName}>
          <span className="text-base font-semibold tracking-tight">{decade}</span>
          <CalendarRange size={16} className="text-[var(--rv5)]" />
        </Link>
      ))}
    </div>
  )
}
