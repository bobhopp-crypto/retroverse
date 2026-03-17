import { BarChart2, Gamepad2, GitMerge, ListMusic, Shuffle, Wrench, type LucideIcon } from 'lucide-react'
import { CARD_ICON_CHIP_CLASS_NAME, CardLink, Panel } from '../components/ui/Card'
import './Hub.css'

type HubEntry = {
  title: string
  description: string
  href: string
  icon: LucideIcon
}

const DECADES = ['1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']

const CREATE_ENTRIES: HubEntry[] = [
  {
    title: 'Playlists',
    description: 'Build and manage RetroVerse listening queues.',
    href: '/playlists',
    icon: ListMusic,
  },
  {
    title: 'SetBuilder',
    description: 'Generate themed sets and quick combinations.',
    href: '/setbuilder',
    icon: Shuffle,
  },
]

const TOOL_ENTRIES: HubEntry[] = [
  {
    title: 'Games',
    description: 'Try RetroVerse interactive challenges.',
    href: '/games',
    icon: Gamepad2,
  },
  {
    title: 'Matching',
    description: 'Align metadata and review match quality.',
    href: '/matching',
    icon: GitMerge,
  },
  {
    title: 'Analytics',
    description: 'Track usage and output trends.',
    href: '/analytics',
    icon: BarChart2,
  },
  {
    title: 'Tools',
    description: 'Access utility workflows for production tasks.',
    href: '/tools',
    icon: Wrench,
  },
]

function DecadeCard({ decade }: { decade: string }) {
  return (
    <CardLink to={`/decade/${decade}`} className="flex min-h-20 h-full items-center justify-center p-4">
      <span className="text-lg font-semibold tracking-tight text-[var(--rv1)]">{decade}</span>
    </CardLink>
  )
}

function ToolCard({ entry }: { entry: HubEntry }) {
  const Icon = entry.icon

  return (
    <CardLink to={entry.href} className="flex h-full flex-col gap-2 p-4">
      <div className="flex items-start gap-3">
        <span aria-hidden className={CARD_ICON_CHIP_CLASS_NAME}>
          <Icon size={18} />
        </span>
        <div className="flex min-w-0 flex-col gap-1">
          <h3 className="m-0 text-base font-semibold text-[var(--rv1)]">{entry.title}</h3>
          <p className="m-0 text-xs leading-relaxed text-[var(--rv1)]">{entry.description}</p>
        </div>
      </div>
    </CardLink>
  )
}

export default function HubPage() {
  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <header className="page-heading">
        <h1 className="page-title">RetroVerse</h1>
      </header>
      <p className="hub-intro max-w-3xl text-[15px] leading-relaxed text-[var(--rv1)]">
        Explore music history one moment at a time.
      </p>

      <section className="mt-6">
        <h2 className="m-0 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--rv1)]">Start with a decade</h2>
        <Panel className="mt-3 p-4 sm:p-5">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {DECADES.map((decade) => (
              <DecadeCard key={decade} decade={decade} />
            ))}
          </div>
        </Panel>
      </section>

      <section className="mt-8">
        <h2 className="m-0 text-xs font-semibold uppercase tracking-[0.1em] text-[var(--rv1)]">Secondary Tools</h2>

        <div className="mt-3">
          <h3 className="m-0 text-sm font-semibold text-[var(--rv1)]">Create</h3>
          <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {CREATE_ENTRIES.map((entry) => (
              <ToolCard key={entry.href} entry={entry} />
            ))}
          </div>
        </div>

        <div className="mt-4">
          <h3 className="m-0 text-sm font-semibold text-[var(--rv1)]">Tools</h3>
          <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {TOOL_ENTRIES.map((entry) => (
              <ToolCard key={entry.href} entry={entry} />
            ))}
          </div>
        </div>
      </section>
    </section>
  )
}
