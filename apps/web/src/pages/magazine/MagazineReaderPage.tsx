import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import {
  MAGAZINE_MAX_YEAR,
  MAGAZINE_MIN_YEAR,
  getMagazineIssue,
  isMagazineYear,
  type MagazineIssue,
} from '../../data/magazineIssues'
import { fetchBillboardYearStats, type BillboardYearStats } from '../../lib/billboardClient'
import './MagazineReaderPage.css'

type MagazineSpreadPage = {
  pageNumber: number
  title: string
  subtitle?: string
  body: string
  image?: string
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

function parsePageParam(pageParam?: string): number {
  const parsed = Number.parseInt(pageParam ?? '1', 10)
  return Number.isFinite(parsed) ? parsed : 1
}

function toSpreadStart(page: number, totalPages: number): number {
  const clamped = clamp(page, 1, totalPages)
  return clamped % 2 === 0 ? clamped - 1 : clamped
}

function buildSpread(issue: MagazineIssue, spreadStart: number): [MagazineSpreadPage | null, MagazineSpreadPage | null] {
  const buildPage = (index: number): MagazineSpreadPage | null => {
    if (index < 0 || index >= issue.pages.length) {
      return null
    }

    const pageId = issue.pages[index]
    const content = issue.content[pageId]
    if (!content) {
      return null
    }

    return {
      pageNumber: index + 1,
      title: content.title,
      subtitle: content.subtitle,
      body: content.body,
      image: content.image,
    }
  }

  return [buildPage(spreadStart - 1), buildPage(spreadStart)]
}

function asList(items: string[]): string {
  if (items.length === 0) return 'No chart rows available for this section yet.'
  return items.map((item, index) => `${index + 1}. ${item}`).join('\n')
}

function buildGeneratedIssue(year: number, stats: BillboardYearStats | null, statsError: string | null): MagazineIssue {
  const snapshotLines =
    stats === null
      ? statsError
        ? ['Chart data is unavailable for this issue right now.', 'Try again later or open another year.']
        : ['Loading year summary from Billboard database...']
      : [
          `${stats.totalSongsCharted.toLocaleString()} songs charted in ${year}.`,
          `${stats.numberOneSongs.length} songs reached #1.`,
          `${stats.longestChartRuns[0]?.title ?? 'N/A'} had one of the longest runs.`,
        ]

  const topSongs = stats?.top10Songs.slice(0, 8).map((song) => `${song.title} — ${song.artist} (best #${song.bestRank})`) ?? []
  const numberOnes = stats?.numberOneSongs.slice(0, 8).map((song) => `${song.title} — ${song.artist} (${song.weeksAtPeak} weeks at peak)`) ?? []
  const longRuns = stats?.longestChartRuns.slice(0, 8).map((song) => `${song.title} — ${song.artist} (${song.chartWeeks} weeks charted)`) ?? []

  return {
    year,
    title: `RetroVerse ${year} Issue`,
    pages: ['cover', 'snapshot', 'top-songs', 'number-ones', 'long-runs', 'closing'],
    content: {
      cover: {
        title: `${year} Annual Issue`,
        subtitle: 'RetroVerse Magazine',
        body: `Digital issue for ${year}.\nUse arrows, swipe, or keyboard left/right to turn spreads.`,
      },
      snapshot: {
        title: 'Year Snapshot',
        subtitle: 'Chart Summary',
        body: snapshotLines.join('\n'),
      },
      'top-songs': {
        title: 'Top Songs',
        subtitle: `Best-performing songs of ${year}`,
        body: asList(topSongs),
      },
      'number-ones': {
        title: '#1 Songs',
        subtitle: `Songs that reached #1 in ${year}`,
        body: asList(numberOnes),
      },
      'long-runs': {
        title: 'Longest Runs',
        subtitle: 'Songs with sustained chart presence',
        body: asList(longRuns),
      },
      closing: {
        title: 'Archive Notes',
        subtitle: 'Data Source',
        body: stats
          ? `Source: ${stats.source}\nIssue generated from Billboard SQLite rows.`
          : 'Issue content will populate as chart data loads.',
      },
    },
  }
}

function SpreadPageCard({ page }: { page: MagazineSpreadPage | null }) {
  if (!page) {
    return <article className="magazine-page magazine-page--blank" aria-hidden />
  }

  return (
    <article className="magazine-page">
      <p className="magazine-page-number">Page {page.pageNumber}</p>
      <h2 className="magazine-page-title">{page.title}</h2>
      {page.subtitle ? <p className="magazine-page-subtitle">{page.subtitle}</p> : null}

      {page.image ? <img src={page.image} alt={page.title} className="magazine-page-image" loading="lazy" decoding="async" /> : null}

      <p className="magazine-page-body">{page.body}</p>
    </article>
  )
}

export default function MagazineReaderPage() {
  const navigate = useNavigate()
  const { year = '', page } = useParams<{ year: string; page?: string }>()

  const parsedYear = useMemo(() => (isMagazineYear(year) ? Number(year) : null), [year])
  const baseIssue = useMemo(() => (parsedYear === null ? undefined : getMagazineIssue(parsedYear)), [parsedYear])
  const [yearStats, setYearStats] = useState<BillboardYearStats | null>(null)
  const [yearStatsError, setYearStatsError] = useState<string | null>(null)
  const [direction, setDirection] = useState(1)

  useEffect(() => {
    if (parsedYear === null || baseIssue) {
      setYearStats(null)
      setYearStatsError(null)
      return
    }

    let cancelled = false
    setYearStats(null)
    setYearStatsError(null)

    fetchBillboardYearStats(parsedYear)
      .then((data) => {
        if (cancelled) return
        setYearStats(data)
      })
      .catch((error: unknown) => {
        if (cancelled) return
        setYearStats(null)
        setYearStatsError(error instanceof Error ? error.message : 'Unable to load year stats.')
      })

    return () => {
      cancelled = true
    }
  }, [baseIssue, parsedYear])

  const issue = useMemo(() => {
    if (parsedYear === null) return null
    if (baseIssue) return baseIssue
    return buildGeneratedIssue(parsedYear, yearStats, yearStatsError)
  }, [baseIssue, parsedYear, yearStats, yearStatsError])

  const totalPages = issue?.pages.length ?? 0
  const spreadStart = useMemo(() => {
    if (!issue) return 1
    return toSpreadStart(parsePageParam(page), totalPages)
  }, [issue, page, totalPages])

  const totalSpreads = issue ? Math.ceil(issue.pages.length / 2) : 0
  const spreadIndex = issue ? Math.floor((spreadStart - 1) / 2) : 0

  const goToSpread = useCallback(
    (nextSpreadStart: number, nextDirection: number) => {
      if (!issue || parsedYear === null) return
      const target = toSpreadStart(nextSpreadStart, issue.pages.length)
      setDirection(nextDirection)
      navigate(`/magazine/${parsedYear}/page/${target}`)
    },
    [issue, navigate, parsedYear],
  )

  const goNext = useCallback(() => {
    if (!issue) return
    const next = spreadStart + 2
    if (next <= issue.pages.length) {
      goToSpread(next, 1)
    }
  }, [goToSpread, issue, spreadStart])

  const goPrev = useCallback(() => {
    if (!issue) return
    const prev = spreadStart - 2
    if (prev >= 1) {
      goToSpread(prev, -1)
    }
  }, [goToSpread, issue, spreadStart])

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowRight') {
        event.preventDefault()
        goNext()
      }
      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        goPrev()
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [goNext, goPrev])

  if (parsedYear === null || issue === null) {
    return (
      <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
        <header className="page-heading">
          <h1 className="page-title">Issue Not Found</h1>
        </header>

        <p className="hub-intro text-[15px] leading-relaxed text-[var(--rv1)]">
          Select a year between {MAGAZINE_MIN_YEAR} and {MAGAZINE_MAX_YEAR}.
        </p>

        <div className="mt-5">
          <Link
            to="/magazine"
            className="inline-flex items-center gap-2 rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] px-3 py-2 text-sm font-semibold text-[var(--rv1)]"
          >
            <ArrowLeft size={15} />
            Back to Year Index
          </Link>
        </div>
      </section>
    )
  }

  const [leftPage, rightPage] = buildSpread(issue, spreadStart)

  return (
    <section className="magazine-reader">
      <header className="magazine-reader-head">
        <div>
          <h1 className="page-title">{issue.title}</h1>
          <p className="magazine-reader-sub">
            {parsedYear} issue • Spread {spreadIndex + 1} of {Math.max(1, totalSpreads)}
          </p>
        </div>
        <Link
          to="/magazine"
          className="inline-flex items-center gap-2 rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] px-3 py-2 text-xs font-semibold uppercase tracking-[0.07em] text-[var(--rv1)]"
        >
          <ArrowLeft size={14} />
          Year Index
        </Link>
      </header>

      <div className="magazine-stage-wrap">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={spreadStart}
            className="magazine-spread"
            initial={{ opacity: 0, rotateY: direction > 0 ? -14 : 14, x: direction > 0 ? 72 : -72 }}
            animate={{ opacity: 1, rotateY: 0, x: 0 }}
            exit={{ opacity: 0, rotateY: direction > 0 ? 14 : -14, x: direction > 0 ? -72 : 72 }}
            transition={{ duration: 0.34, ease: 'easeOut' }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.12}
            onDragEnd={(_, info) => {
              if (info.offset.x < -70) goNext()
              if (info.offset.x > 70) goPrev()
            }}
          >
            <SpreadPageCard page={leftPage} />
            <SpreadPageCard page={rightPage} />
          </motion.div>
        </AnimatePresence>
      </div>

      <footer className="magazine-reader-controls">
        <button type="button" onClick={goPrev} disabled={spreadStart <= 1} className="magazine-nav-btn magazine-nav-btn--secondary">
          <ChevronLeft size={16} />
          Previous
        </button>

        <div className="magazine-indicators" role="tablist" aria-label="Magazine spread index">
          {Array.from({ length: totalSpreads }, (_, index) => {
            const isActive = index === spreadIndex
            return (
              <button
                key={index}
                type="button"
                aria-label={`Go to spread ${index + 1}`}
                aria-selected={isActive}
                className={`magazine-indicator ${isActive ? 'is-active' : ''}`}
                onClick={() => goToSpread(index * 2 + 1, index > spreadIndex ? 1 : -1)}
              />
            )
          })}
        </div>

        <button
          type="button"
          onClick={goNext}
          disabled={spreadStart + 1 >= totalPages}
          className="magazine-nav-btn magazine-nav-btn--primary"
        >
          Next
          <ChevronRight size={16} />
        </button>
      </footer>
    </section>
  )
}
