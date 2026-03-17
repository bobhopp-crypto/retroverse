import { BillboardExplorer } from "@/components/billboard-explorer"
import { Disc3 } from "lucide-react"

interface BillboardRecord {
  title: string
  artist: string
  year: number
  chart_position: number
  weeks_on_chart: number
}

async function getBillboardData(): Promise<BillboardRecord[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"}/data/billboard_hot_100.json`,
    { cache: "no-store" }
  )

  if (!response.ok) {
    return []
  }

  return response.json()
}

export default async function HomePage() {
  const data = await getBillboardData()

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6 md:py-10 max-w-7xl">
        {/* Header */}
        <header className="text-center mb-8 md:mb-10">
          <div className="inline-flex items-center justify-center gap-3 md:gap-4 mb-4">
            <Disc3
              className="h-10 w-10 md:h-12 md:w-12 text-retro-teal animate-spin"
              style={{ animationDuration: "3s" }}
            />
            <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-foreground tracking-tight">
              <span className="text-retro-coral">RetroVerse</span> Billboard Explorer
            </h1>
            <Disc3
              className="h-10 w-10 md:h-12 md:w-12 text-retro-teal animate-spin"
              style={{ animationDuration: "3s", animationDirection: "reverse" }}
            />
          </div>
          <p className="text-base md:text-lg text-muted-foreground max-w-2xl mx-auto px-2">
            Explore the Billboard Hot 100 database. Search, filter, and discover
            the hits that defined generations.
          </p>
        </header>

        {/* Billboard Explorer */}
        <BillboardExplorer data={data} />

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-muted-foreground border-t border-border pt-6">
          <p>
            RetroVerse Billboard Explorer &bull; Celebrating the music that shaped
            our world
          </p>
        </footer>
      </div>
    </main>
  )
}
