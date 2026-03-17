import Link from "next/link"
import { notFound } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { SongDetailClient } from "./song-detail-client"
import { parseSongSlug, slugMatches, artistSlug } from "@/lib/slug"

interface BillboardRecord {
  title: string
  artist: string
  year: number
  chart_position: number
  weeks_on_chart: number
}

async function getBillboardData(): Promise<BillboardRecord[]> {
  const base = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"
  const res = await fetch(`${base}/data/billboard_hot_100.json`, {
    cache: "no-store",
  })
  if (!res.ok) return []
  return res.json()
}

function findSong(data: BillboardRecord[], slug: string): BillboardRecord | null {
  const parsed = parseSongSlug(slug)
  if (!parsed) return null
  return data.find((r) => slugMatches(r.title, r.artist, parsed)) ?? null
}

export default async function SongPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const data = await getBillboardData()
  const song = findSong(data, slug)

  if (!song) notFound()

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-retro-coral mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Explorer
        </Link>

        <div className="rounded-lg border-2 border-retro-teal/50 bg-card p-6 shadow-lg mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
            {song.title}
          </h1>
          <Link
            href={`/artist/${encodeURIComponent(artistSlug(song.artist))}`}
            className="text-lg text-retro-coral hover:underline font-medium"
          >
            {song.artist}
          </Link>
          <div className="flex flex-wrap gap-4 mt-4 text-muted-foreground">
            <span>Year: {song.year}</span>
            <span>Peak: #{song.chart_position}</span>
            <span>Weeks on chart: {song.weeks_on_chart}</span>
          </div>
        </div>

        <div className="rounded-lg border-2 border-retro-mint/50 bg-card p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Chart History
          </h2>
          <SongDetailClient
            peakPosition={song.chart_position}
            weeksOnChart={song.weeks_on_chart}
          />
        </div>
      </div>
    </main>
  )
}
