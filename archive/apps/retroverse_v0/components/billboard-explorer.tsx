"use client"

import { useState, useMemo, useCallback, useRef, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Search, Music } from "lucide-react"
import { songSlug, artistSlug } from "@/lib/slug"

interface BillboardRecord {
  title: string
  artist: string
  year: number
  chart_position: number
  weeks_on_chart: number
}

interface BillboardExplorerProps {
  data: BillboardRecord[]
}

type FilterChip =
  | "all"
  | "no1"
  | "top10"
  | "top40"
  | "1970s"
  | "1980s"
  | "1990s"

const INITIAL_LOAD = 50
const LOAD_MORE = 50

function getBadgeClass(position: number): string {
  if (position === 1) return "bg-retro-mustard text-amber-950 font-bold"
  if (position <= 10) return "bg-retro-teal/90 text-teal-950 font-semibold"
  if (position <= 40) return "bg-retro-coral/80 text-red-950 font-medium"
  return "bg-retro-mint/70 text-slate-800"
}

function Badge({ position }: { position: number }) {
  return (
    <span
      className={`inline-flex min-w-[2.5rem] items-center justify-center rounded-full px-2.5 py-1 text-sm shadow-sm ${getBadgeClass(position)}`}
    >
      #{position}
    </span>
  )
}

export function BillboardExplorer({ data }: BillboardExplorerProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [chipFilter, setChipFilter] = useState<FilterChip>("all")
  const [visibleCount, setVisibleCount] = useState(INITIAL_LOAD)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  const filteredData = useMemo(() => {
    const query = searchQuery.toLowerCase().trim()
    let result = data

    if (query) {
      result = result.filter(
        (r) =>
          r.title.toLowerCase().includes(query) ||
          r.artist.toLowerCase().includes(query) ||
          r.year.toString().includes(query)
      )
    }

    switch (chipFilter) {
      case "no1":
        result = result.filter((r) => r.chart_position === 1)
        break
      case "top10":
        result = result.filter((r) => r.chart_position <= 10)
        break
      case "top40":
        result = result.filter((r) => r.chart_position <= 40)
        break
      case "1970s":
        result = result.filter((r) => r.year >= 1970 && r.year <= 1979)
        break
      case "1980s":
        result = result.filter((r) => r.year >= 1980 && r.year <= 1989)
        break
      case "1990s":
        result = result.filter((r) => r.year >= 1990 && r.year <= 1999)
        break
      default:
        break
    }

    return result
  }, [data, searchQuery, chipFilter])

  const visibleData = useMemo(
    () => filteredData.slice(0, visibleCount),
    [filteredData, visibleCount]
  )

  const hasMore = visibleCount < filteredData.length

  const handleChipClick = useCallback((chip: FilterChip) => {
    setChipFilter((prev) => (prev === chip ? "all" : chip))
    setVisibleCount(INITIAL_LOAD)
  }, [])

  useEffect(() => {
    setVisibleCount(INITIAL_LOAD)
  }, [searchQuery, chipFilter])

  useEffect(() => {
    if (!hasMore) return
    const el = loadMoreRef.current
    if (!el) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setVisibleCount((c) => Math.min(c + LOAD_MORE, filteredData.length))
        }
      },
      { rootMargin: "200px", threshold: 0 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [hasMore, filteredData.length])

  const chips: { id: FilterChip; label: string }[] = [
    { id: "no1", label: "#1 Hits" },
    { id: "top10", label: "Top 10" },
    { id: "top40", label: "Top 40" },
    { id: "1970s", label: "1970s" },
    { id: "1980s", label: "1980s" },
    { id: "1990s", label: "1990s" },
  ]

  return (
    <div className="flex flex-col min-h-0">
      {/* Sticky search panel - retro stacked style */}
      <div className="sticky top-0 z-10 -mx-4 px-4 py-4 bg-background/95 backdrop-blur border-b-4 border-retro-teal shadow-lg transition-all duration-300">
        <div className="rounded-lg border-2 border-retro-aqua/50 bg-retro-mint/30 p-4 shadow-sm">
          <div className="relative mb-4">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-retro-aqua pointer-events-none" />
            <Input
              type="text"
              placeholder="Search by title, artist, or year..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 h-14 text-lg bg-card border-2 border-retro-teal/50 focus:border-retro-teal focus:ring-2 focus:ring-retro-teal/30 rounded-lg min-h-[3rem] transition-colors"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {chips.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => handleChipClick(id)}
                className={`min-h-[2.75rem] px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 touch-manipulation border-2 ${
                  chipFilter === id
                    ? "bg-retro-coral text-white border-retro-coral shadow-md"
                    : "bg-retro-mustard/50 text-foreground border-retro-mustard/70 hover:bg-retro-mustard/70"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

        </div>
      </div>

      {/* Results count - retro panel */}
      <div className="flex items-center gap-2 py-3 px-2 rounded-lg bg-retro-aqua/20 border border-retro-aqua/40 my-2">
        <Music className="h-4 w-4 text-retro-aqua shrink-0" />
        <span className="text-sm text-foreground">
          {filteredData.length.toLocaleString()} records
          {visibleCount < filteredData.length &&
            ` (showing ${visibleCount.toLocaleString()})`}
        </span>
      </div>

      {/* Card grid - stacked retro panels */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pb-8">
        {visibleData.length === 0 ? (
          <div className="col-span-full min-h-[12rem] flex items-center justify-center text-muted-foreground rounded-lg border-2 border-dashed border-retro-teal/50 bg-retro-mint/20 p-8">
            No records found matching your search.
          </div>
        ) : (
          visibleData.map((record, index) => (
            <Link
              key={`${record.title}-${record.artist}-${index}`}
              href={`/song/${encodeURIComponent(songSlug(record.title, record.artist))}`}
              className="block rounded-lg border-2 border-retro-teal/40 bg-card p-4 shadow-md hover:shadow-lg hover:border-retro-coral/60 transition-all duration-300 min-h-[7.5rem] flex flex-col justify-between group"
            >
              <div>
                <h3 className="font-semibold text-foreground text-base leading-tight mb-1 line-clamp-2 group-hover:text-retro-aqua transition-colors">
                  {record.title}
                </h3>
                <span
                  role="link"
                  tabIndex={0}
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    router.push(`/artist/${encodeURIComponent(artistSlug(record.artist))}`)
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault()
                      router.push(`/artist/${encodeURIComponent(artistSlug(record.artist))}`)
                    }
                  }}
                  className="text-sm text-left w-full block text-muted-foreground hover:text-retro-coral font-medium transition-colors min-h-[2.5rem] -ml-1 pl-1 rounded-lg touch-manipulation cursor-pointer"
                >
                  {record.artist}
                </span>
              </div>
              <div className="mt-3 flex items-center justify-between gap-2 flex-wrap">
                <span className="text-sm text-muted-foreground font-medium">
                  {record.year}
                </span>
                <div className="flex items-center gap-2">
                  <Badge position={record.chart_position} />
                  <span className="text-sm text-muted-foreground">
                    {record.weeks_on_chart}w
                  </span>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {/* Infinite scroll sentinel */}
      {hasMore && <div ref={loadMoreRef} className="h-4" aria-hidden />}
    </div>
  )
}