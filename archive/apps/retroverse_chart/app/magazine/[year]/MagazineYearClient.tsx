'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import type { Song } from '@/lib/types'

export default function MagazineYearClient({ year: yearParam }: { year: string }) {
  const year = parseInt(yearParam, 10)
  const [songs, setSongs] = useState<Song[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/data/billboard_hot_100.json')
      .then((res) => (res.ok ? res.json() : []))
      .then((data: Song[]) => {
        const yearSongs = (data || []).filter((s) => s.year === year)
        setSongs(yearSongs)
      })
      .catch(() => setSongs([]))
      .finally(() => setLoading(false))
  }, [year])

  const isValidYear = year >= 1958 && year <= 2024

  if (!isValidYear) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-2xl mx-auto px-4 py-12 text-center">
          <h1 className="text-xl font-bold text-foreground">Invalid Year</h1>
          <p className="text-muted-foreground mt-2">Please choose a year between 1958 and 2024.</p>
          <Link href="/magazine" className="mt-4 inline-block text-primary underline">
            Back to Magazine
          </Link>
        </div>
      </main>
    )
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background">
        <div className="max-w-2xl mx-auto px-4 py-12 flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground">Loading {year} issue…</p>
        </div>
      </main>
    )
  }

  const hasData = songs.length > 0

  return (
    <main className="min-h-screen bg-background">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Link href="/magazine" className="text-sm text-muted-foreground hover:text-primary mb-6 inline-block">
          ← Back to Magazine
        </Link>

        {hasData ? (
          <article className="space-y-6">
            <header>
              <h1 className="text-2xl font-black text-foreground">
                RetroVerse {year} Issue
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {songs.length.toLocaleString()} songs charted in {year}
              </p>
            </header>

            <section className="rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">Top 10 of {year}</h2>
              <ol className="space-y-2">
                {songs
                  .filter((s) => s.peak <= 10)
                  .sort((a, b) => a.peak - b.peak)
                  .slice(0, 10)
                  .map((song, i) => (
                    <li key={`${song.title}-${song.artist}`} className="flex gap-3 text-sm">
                      <span className="font-mono text-muted-foreground w-6">{i + 1}.</span>
                      <span className="text-foreground font-medium">{song.title}</span>
                      <span className="text-muted-foreground">— {song.artist}</span>
                      <span className="text-muted-foreground text-xs">#{song.peak}</span>
                    </li>
                  ))}
              </ol>
            </section>

            <section className="rounded-xl border border-border bg-card p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">#1 Hits</h2>
              <ul className="space-y-2">
                {songs
                  .filter((s) => s.peak === 1)
                  .sort((a, b) => (b.weeks_at_peak ?? b.weeks) - (a.weeks_at_peak ?? a.weeks))
                  .slice(0, 5)
                  .map((song) => (
                    <li key={`${song.title}-${song.artist}`} className="text-sm">
                      <span className="font-medium text-foreground">{song.title}</span>
                      <span className="text-muted-foreground"> — {song.artist}</span>
                    </li>
                  ))}
              </ul>
            </section>
          </article>
        ) : (
          <article className="rounded-xl border border-border bg-card p-12 text-center">
            <h1 className="text-2xl font-black text-foreground">RetroVerse {year}</h1>
            <p className="text-lg text-muted-foreground mt-4">Coming Soon</p>
            <p className="text-sm text-muted-foreground mt-2">
              This issue is in production. Check back later.
            </p>
          </article>
        )}
      </div>
    </main>
  )
}
