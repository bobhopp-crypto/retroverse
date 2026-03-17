import Link from "next/link"
import { notFound } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { ArtistDetailClient } from "./artist-detail-client"
import { artistSlug, songSlug } from "@/lib/slug"

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

function findArtistSongs(
  data: BillboardRecord[],
  slug: string
): { artist: string; songs: BillboardRecord[] } | null {
  const targetSlug = slug.toLowerCase().replace(/[^a-z0-9-]/g, "")
  const songs = data.filter((r) => artistSlug(r.artist) === targetSlug)
  if (songs.length === 0) return null
  return { artist: songs[0].artist, songs }
}

export default async function ArtistPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const data = await getBillboardData()
  const result = findArtistSongs(data, slug)

  if (!result) notFound()

  const { artist, songs } = result
  const top10Count = songs.filter((s) => s.chart_position <= 10).length
  const no1Count = songs.filter((s) => s.chart_position === 1).length

  const decadeCounts: Record<string, number> = {}
  for (const s of songs) {
    const decade = `${Math.floor(s.year / 10) * 10}s`
    decadeCounts[decade] = (decadeCounts[decade] || 0) + 1
  }
  const decades = Object.entries(decadeCounts)
    .sort(([a], [b]) => parseInt(a) - parseInt(b))
    .map(([decade, count]) => ({ decade, count }))

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
          <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
            {artist}
          </h1>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-lg bg-retro-mint/40 p-4 border border-retro-mint/60">
              <div className="text-2xl font-bold text-foreground">
                {songs.length}
              </div>
              <div className="text-sm text-muted-foreground">
                Chart songs
              </div>
            </div>
            <div className="rounded-lg bg-retro-teal/40 p-4 border border-retro-teal/60">
              <div className="text-2xl font-bold text-foreground">
                {top10Count}
              </div>
              <div className="text-sm text-muted-foreground">
                Top 10 hits
              </div>
            </div>
            <div className="rounded-lg bg-retro-mustard/50 p-4 border border-retro-mustard/70">
              <div className="text-2xl font-bold text-foreground">
                {no1Count}
              </div>
              <div className="text-sm text-muted-foreground">
                #1 hits
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-lg border-2 border-retro-mint/50 bg-card p-6 shadow-lg mb-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Songs by decade
          </h2>
          <ArtistDetailClient decades={decades} />
        </div>

        <div className="rounded-lg border-2 border-retro-aqua/50 bg-card p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-foreground mb-4">
            All songs ({songs.length})
          </h2>
          <ul className="space-y-2 max-h-96 overflow-y-auto">
            {songs
              .sort((a, b) => a.year - b.year || a.chart_position - b.chart_position)
              .map((song, i) => (
                <li key={`${song.title}-${i}`}>
                  <Link
                    href={`/song/${encodeURIComponent(songSlug(song.title, song.artist))}`}
                    className="flex justify-between items-center py-2 px-3 rounded-lg hover:bg-retro-teal/20 transition-colors"
                  >
                    <span className="font-medium">{song.title}</span>
                    <span className="text-sm text-muted-foreground">
                      {song.year} · #{song.chart_position}
                    </span>
                  </Link>
                </li>
              ))}
          </ul>
        </div>
      </div>
    </main>
  )
}
