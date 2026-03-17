import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchBillboardYearStats, type BillboardYearSongStat, type BillboardYearStats } from '../lib/billboardClient'
import './Landing.css'

const MIN_YEAR = 1958

type ArtistPreview = {
  name: string
  songCount: number
}

const getCurrentYear = () => new Date().getFullYear()

const getRandomYear = (minYear: number, maxYear: number) => Math.floor(Math.random() * (maxYear - minYear + 1)) + minYear

const getNumberOneSong = (stats: BillboardYearStats | null): BillboardYearSongStat | null => {
  if (!stats) return null
  return stats.numberOneSongs[0] ?? stats.top10Songs[0] ?? null
}

const getFallbackTopArtist = (stats: BillboardYearStats): ArtistPreview | null => {
  const uniqueSongs = new Map<string, BillboardYearSongStat>()
  const songPools = [stats.top10Songs, stats.numberOneSongs, stats.longestChartRuns]

  for (const songs of songPools) {
    for (const song of songs) {
      const key = song.songId.trim().length > 0 ? song.songId : `${song.title}::${song.artist}`
      if (!uniqueSongs.has(key)) uniqueSongs.set(key, song)
    }
  }

  const byArtist = new Map<
    string,
    {
      songCount: number
      bestRank: number
      totalWeeksAtPeak: number
      totalChartWeeks: number
    }
  >()

  for (const song of uniqueSongs.values()) {
    const artist = song.artist.trim().length > 0 ? song.artist.trim() : 'Unknown Artist'
    const existing = byArtist.get(artist)
    if (!existing) {
      byArtist.set(artist, {
        songCount: 1,
        bestRank: song.bestRank,
        totalWeeksAtPeak: song.weeksAtPeak,
        totalChartWeeks: song.chartWeeks,
      })
      continue
    }

    existing.songCount += 1
    existing.bestRank = Math.min(existing.bestRank, song.bestRank)
    existing.totalWeeksAtPeak += song.weeksAtPeak
    existing.totalChartWeeks += song.chartWeeks
  }

  const leader = Array.from(byArtist.entries())
    .sort(
      (a, b) =>
        b[1].songCount - a[1].songCount ||
        a[1].bestRank - b[1].bestRank ||
        b[1].totalWeeksAtPeak - a[1].totalWeeksAtPeak ||
        b[1].totalChartWeeks - a[1].totalChartWeeks ||
        a[0].localeCompare(b[0]),
    )[0]

  if (!leader) return null
  return {
    name: leader[0],
    songCount: leader[1].songCount,
  }
}

const getTopArtist = (stats: BillboardYearStats | null): ArtistPreview | null => {
  if (!stats) return null

  const topArtist = stats.topArtists?.[0]
  if (topArtist) {
    return {
      name: topArtist.artist,
      songCount: topArtist.songCount,
    }
  }

  return getFallbackTopArtist(stats)
}

export default function Landing() {
  const navigate = useNavigate()
  const currentYear = getCurrentYear()
  const [previewYear, setPreviewYear] = useState<number | null>(null)
  const [stats, setStats] = useState<BillboardYearStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSpinning, setIsSpinning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPreview = useCallback(async (year: number): Promise<BillboardYearStats | null> => {
    setPreviewYear(year)
    setIsLoading(true)
    setError(null)
    try {
      const payload = await fetchBillboardYearStats(year)
      setStats(payload)
      return payload
    } catch (err: unknown) {
      setStats(null)
      setError(err instanceof Error ? err.message : 'Unable to load year preview.')
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    const initialYear = getRandomYear(MIN_YEAR, currentYear)
    void loadPreview(initialYear)
  }, [currentYear, loadPreview])

  const numberOneSong = useMemo(() => getNumberOneSong(stats), [stats])
  const topArtist = useMemo(() => getTopArtist(stats), [stats])

  const handleSpin = useCallback(async () => {
    if (isSpinning) return

    setIsSpinning(true)
    const targetYear = getRandomYear(MIN_YEAR, currentYear)
    const payload = await loadPreview(targetYear)
    setIsSpinning(false)

    if (!payload) return
    navigate(`/year/${targetYear}`)
  }, [currentYear, isSpinning, loadPreview, navigate])

  const showPreview = !isLoading && !error && stats !== null

  return (
    <section className="landing-spin-page">
      <div className="landing-spin-glow landing-spin-glow--one" />
      <div className="landing-spin-glow landing-spin-glow--two" />
      <div className="landing-spin-shell">
        <p className="landing-spin-kicker">RetroVerse Primary Entry</p>
        <h1 className="landing-spin-title">Spin Into A Billboard Year</h1>
        <p className="landing-spin-subtitle">
          Random jump from {MIN_YEAR} through {currentYear}.
        </p>

        <div className={['landing-spin-wheel', isSpinning ? 'is-spinning' : ''].join(' ')}>
          <button
            type="button"
            className="landing-spin-button"
            onClick={handleSpin}
            disabled={isLoading || isSpinning}
            aria-label="Spin the Year and open a random year page"
          >
            <span>Spin</span>
            <span>The Year</span>
          </button>
        </div>

        <div className="landing-spin-year-pill" aria-live="polite">
          {previewYear !== null ? `Preview Year ${previewYear}` : 'Loading preview year'}
        </div>

        {isLoading ? <p className="landing-preview-note">Loading preview...</p> : null}
        {error ? <p className="landing-preview-error">{error}</p> : null}

        {showPreview ? (
          <div className="landing-preview-grid">
            <article className="landing-preview-card">
              <h2>#1 Song</h2>
              <p className="landing-preview-value">
                {numberOneSong ? `${numberOneSong.title} - ${numberOneSong.artist}` : 'Unavailable'}
              </p>
            </article>

            <article className="landing-preview-card">
              <h2>Top Artist</h2>
              <p className="landing-preview-value">{topArtist ? topArtist.name : 'Unavailable'}</p>
              {topArtist ? <p className="landing-preview-sub">{topArtist.songCount} standout songs in preview set</p> : null}
            </article>

            <article className="landing-preview-card">
              <h2>Total Songs Charted</h2>
              <p className="landing-preview-value">{stats.totalSongsCharted.toLocaleString()}</p>
            </article>
          </div>
        ) : null}

        <p className="landing-spin-links">
          Need the full navigation map? <Link to="/hub">Open Hub</Link>
        </p>
      </div>
    </section>
  )
}
