import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { dataUrl } from '../../config/dataSources'

type ChartEntry = {
  artist: string
  title: string
  peak: number
  weeks: number
}

export default function MagazineYear() {
  const { year: yearParam } = useParams<{ year: string }>()
  const year = yearParam ? parseInt(yearParam, 10) : NaN
  const [songs, setSongs] = useState<ChartEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isNaN(year) || year < 1958 || year > 2024) {
      setLoading(false)
      return
    }

    fetch(dataUrl(`charts/${year}.json`))
      .then((res) => (res.ok ? res.json() : []))
      .then((data: ChartEntry[]) => {
        setSongs(Array.isArray(data) ? data : [])
      })
      .catch(() => setSongs([]))
      .finally(() => setLoading(false))
  }, [year])

  const isValidYear = !isNaN(year) && year >= 1958 && year <= 2024

  if (!isValidYear) {
    return (
      <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
        <p>Invalid year. Choose 1958–2024.</p>
        <Link to="/magazine">Back to Magazine</Link>
      </section>
    )
  }

  if (loading) {
    return (
      <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
        <p>Loading {year}…</p>
      </section>
    )
  }

  const top10 = songs
    .filter((s) => s.peak <= 10)
    .sort((a, b) => a.peak - b.peak)
    .slice(0, 10)

  return (
    <section className="hub-page bg-[var(--rv4)] text-[var(--rv1)]">
      <Link to="/magazine" className="text-sm text-[var(--rv5)] hover:underline mb-4 inline-block">
        ← Back to Magazine
      </Link>

      {top10.length > 0 ? (
        <>
          <h1 className="page-title">RetroVerse {year}</h1>
          <p className="text-sm text-[var(--rv1)] opacity-80 mb-4">
            {songs.length} songs charted
          </p>
          <ol className="space-y-2">
            {top10.map((song, i) => (
              <li key={`${song.title}-${song.artist}`} className="flex gap-3 text-sm">
                <span className="font-mono w-6">{i + 1}.</span>
                <span className="font-medium">{song.title}</span>
                <span className="opacity-80">— {song.artist}</span>
                <span className="text-xs opacity-70">#{song.peak}</span>
              </li>
            ))}
          </ol>
        </>
      ) : (
        <>
          <h1 className="page-title">RetroVerse {year}</h1>
          <p className="text-lg opacity-80 mt-4">Coming Soon</p>
          <p className="text-sm opacity-70 mt-2">This issue is in production.</p>
        </>
      )}
    </section>
  )
}
