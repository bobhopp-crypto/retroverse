import { ArrowRight, BarChart3, Clapperboard, Gauge, Shuffle, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import ArcadeShell from '../../../games/shared/ui/ArcadeShell.tsx'
import GamePanel from '../../../games/shared/ui/GamePanel.tsx'
import './games/arcade.css'

type ArcadeCard = {
  title: string
  description: string
  route: string
  status: string
  detail: string
  icon: LucideIcon
}

const ARCADE_GAMES: ArcadeCard[] = [
  {
    title: 'Chart Climber',
    description: 'Predict the next Billboard chart position from a five-week movement slice.',
    route: '/games/chart-climber',
    status: 'Live data',
    detail: 'Curated chart climbers pool',
    icon: BarChart3,
  },
  {
    title: 'Year Shuffle',
    description: 'Put four songs in chronological order using only the song and artist clues.',
    route: '/games/year-shuffle',
    status: 'Live data',
    detail: 'Year identifier songs',
    icon: Shuffle,
  },
  {
    title: 'Video Time Machine',
    description: 'Match a video frame and metadata cue to the exact year.',
    route: '/games/video-time-machine',
    status: 'Live data',
    detail: 'Filtered video puzzle pool',
    icon: Clapperboard,
  },
  {
    title: 'Guess The Peak',
    description: 'Call the highest Billboard rank a song reached from a curated hit-song pool.',
    route: '/games/guess-peak',
    status: 'Live data',
    detail: 'Top-hit nostalgia rounds',
    icon: Gauge,
  },
]

export default function Games() {
  return (
    <section className="arcade-page">
      <ArcadeShell
        title="RetroVerse Arcade"
        subtitle="A single preliminary arcade built on the shared RetroVerse game data engine. Each game uses the live shared API first and falls back to demo mode safely if a queue is unavailable."
        stats={[
          { label: 'Playable Games', value: ARCADE_GAMES.length, tone: 'accent' },
          { label: 'Data Mode', value: 'Live API', tone: 'good' },
          { label: 'Fallback', value: 'Demo Ready', tone: 'warning' },
          { label: 'Hub Route', value: '/games', tone: 'default' },
        ]}
        headerMeta={
          <div className="arcade-shell__header-actions">
            <span className="arcade-pill arcade-pill--accent">Preliminary arcade</span>
            <span className="arcade-pill arcade-pill--good">Deployment-ready pass</span>
          </div>
        }
        footer={
          <div className="arcade-actions">
            <Link to="/hub" className="arcade-button arcade-button--ghost">
              Back to Hub
            </Link>
            <Link to="/games/chart-climber" className="arcade-button arcade-button--primary">
              Start Playing
            </Link>
          </div>
        }
        sidePanel={
          <>
            <GamePanel eyebrow="Arcade Notes" title="What ships in this pass">
              <div className="arcade-stack">
                <div className="arcade-detail-row">
                  <span>Shared shell</span>
                  <strong>Unified layout and score bar</strong>
                </div>
                <div className="arcade-detail-row">
                  <span>Live endpoints</span>
                  <strong>4 games wired to `/api`</strong>
                </div>
                <div className="arcade-detail-row">
                  <span>Failure mode</span>
                  <strong>Safe demo fallback</strong>
                </div>
              </div>
            </GamePanel>

            <GamePanel eyebrow="Launch Flow" title="How to use the hub">
              <p className="arcade-supporting">Open any game card. Scores and streaks stay local to the current session so you can jump between rounds without waiting on the backend for every interaction.</p>
            </GamePanel>
          </>
        }
      >
        <GamePanel eyebrow="Live Games" title="Choose a cabinet">
          <div className="arcade-hub-grid">
            {ARCADE_GAMES.map((game) => {
              const Icon = game.icon
              return (
                <Link key={game.route} to={game.route} className="arcade-hub-card">
                  <div className="arcade-hub-card__top">
                    <span className="arcade-hub-card__icon" aria-hidden>
                      <Icon size={22} />
                    </span>
                    <span className="arcade-pill arcade-pill--good">{game.status}</span>
                  </div>

                  <div className="arcade-stack">
                    <h2 className="arcade-hub-card__title">{game.title}</h2>
                    <p className="arcade-hub-card__desc">{game.description}</p>
                  </div>

                  <div className="arcade-hub-card__meta">
                    <span className="arcade-pill">{game.detail}</span>
                  </div>

                  <span className="arcade-hub-card__cta">
                    Launch cabinet
                    <ArrowRight size={16} aria-hidden />
                  </span>
                </Link>
              )
            })}
          </div>
        </GamePanel>
      </ArcadeShell>
    </section>
  )
}
