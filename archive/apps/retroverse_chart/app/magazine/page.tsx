import Link from 'next/link'

const MIN_YEAR = 1958
const MAX_YEAR = 2024
const YEARS = Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i)

export default function MagazinePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-2xl font-black text-foreground tracking-tight">
            RetroVerse Magazine
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Select a year to open the issue
          </p>
        </header>

        <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-3">
          {YEARS.map((year) => (
            <Link
              key={year}
              href={`/magazine/${year}`}
              className="flex items-center justify-center rounded-xl border border-border bg-card p-4 text-center font-semibold text-foreground transition hover:border-primary hover:bg-muted"
            >
              {year}
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
