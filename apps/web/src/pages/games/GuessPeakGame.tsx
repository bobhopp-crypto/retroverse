import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArcadeShell from '../../../../games/shared/ui/ArcadeShell.tsx'
import GamePanel from '../../../../games/shared/ui/GamePanel.tsx'
import { joinArcadeClasses } from '../../../../games/shared/ui/arcadeTheme.ts'
import type { GuessPeakRound } from '../../lib/arcadeClient'
import { guessPeakDemoRounds } from './demoRounds'
import './arcade.css'
import { useArcadeRoundQueue } from './useArcadeRoundQueue'

const BATCH_SIZE = 6

export default function GuessPeakGame() {
  const { currentRound, hasRounds, loading, message, mode, nextRound, reload, roundNumber } = useArcadeRoundQueue<GuessPeakRound>({
    endpoint: '/guess-peak',
    batchSize: BATCH_SIZE,
    fallbackRounds: guessPeakDemoRounds,
  })
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [selectedChoice, setSelectedChoice] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null)

  useEffect(() => {
    setSelectedChoice(null)
    setRevealed(false)
    setWasCorrect(null)
  }, [currentRound, roundNumber])

  const correctAnswer = currentRound?.correct ?? null

  const submitChoice = (choice: number) => {
    if (!currentRound || revealed || correctAnswer === null) return

    const correct = choice === correctAnswer
    setSelectedChoice(choice)
    setRevealed(true)
    setWasCorrect(correct)
    setScore((value) => value + (correct ? 1 : 0))
    setStreak((value) => (correct ? value + 1 : 0))
  }

  const revealAnswer = () => {
    if (!currentRound || revealed) return
    setRevealed(true)
    setWasCorrect(false)
    setSelectedChoice(null)
    setStreak(0)
  }

  return (
    <section className="arcade-page">
      <ArcadeShell
        title="Guess The Peak"
        subtitle="Use the song and year, then call the highest Billboard position it reached."
        stats={[
          { label: 'Score', value: score, tone: score > 0 ? 'good' : 'default' },
          { label: 'Round', value: roundNumber, tone: 'accent' },
          { label: 'Streak', value: streak, tone: streak > 1 ? 'good' : 'default' },
          { label: 'Mode', value: mode === 'live' ? 'Live Data' : loading ? 'Loading' : 'Demo Mode', tone: mode === 'live' ? 'accent' : 'warning' },
        ]}
        headerMeta={
          <div className="arcade-shell__header-actions">
            <Link to="/games" className="arcade-button arcade-button--ghost">
              Back to Arcade
            </Link>
            <span className={joinArcadeClasses('arcade-pill', mode === 'live' ? 'arcade-pill--good' : 'arcade-pill--warning')}>
              {mode === 'live' ? 'Hit songs live' : 'Demo fallback'}
            </span>
          </div>
        }
        footer={
          <div className="arcade-actions">
            <button type="button" className="arcade-button arcade-button--primary" onClick={() => void nextRound()} disabled={loading}>
              {revealed ? 'Next Round' : 'Skip Round'}
            </button>
            {!revealed ? (
              <button type="button" className="arcade-button arcade-button--ghost" onClick={revealAnswer} disabled={!currentRound}>
                Reveal Peak
              </button>
            ) : null}
            <button type="button" className="arcade-button arcade-button--secondary" onClick={() => void reload()} disabled={loading}>
              Refresh Queue
            </button>
          </div>
        }
        sidePanel={
          <>
            <GamePanel eyebrow="Track Detail" title={currentRound ? `${currentRound.artist} - ${currentRound.title}` : 'Waiting for a song'}>
              {currentRound ? (
                <>
                  <div className="arcade-detail-list">
                    <div className="arcade-detail-row">
                      <span>Release year</span>
                      <strong>{currentRound.year}</strong>
                    </div>
                    <div className="arcade-detail-row">
                      <span>Choice spread</span>
                      <strong>{currentRound.choices.join(' / ')}</strong>
                    </div>
                    <div className="arcade-detail-row">
                      <span>Hint</span>
                      <strong>These are all Top 20 hits</strong>
                    </div>
                  </div>
                  {revealed && correctAnswer !== null ? (
                    <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                      Peak position: <strong>#{correctAnswer}</strong>
                    </div>
                  ) : (
                    <p className="arcade-supporting">The lower the number, the bigger the chart record.</p>
                  )}
                </>
              ) : (
                <div className="arcade-empty">No hit-song round is available right now.</div>
              )}
            </GamePanel>
            {message ? (
              <GamePanel eyebrow="Feed Status" title="Queue note" tone={mode === 'live' ? 'accent' : 'warning'}>
                <p className="arcade-supporting">{message}</p>
              </GamePanel>
            ) : null}
          </>
        }
      >
        <GamePanel eyebrow="Round Objective" title="Call The Peak">
          {currentRound ? (
            <>
              <div className="arcade-meta">
                <div className="arcade-meta__item">
                  Artist <strong>{currentRound.artist}</strong>
                </div>
                <div className="arcade-meta__item">
                  Song <strong>{currentRound.title}</strong>
                </div>
                <div className="arcade-meta__item">
                  Year <strong>{currentRound.year}</strong>
                </div>
              </div>

              <p className="arcade-prompt">Which Billboard Hot 100 peak fits this song?</p>

              <div className="arcade-choice-grid">
                {currentRound.choices.map((choice) => (
                  <button
                    key={choice}
                    type="button"
                    className={joinArcadeClasses(
                      'arcade-choice',
                      selectedChoice === choice ? 'is-selected' : '',
                      revealed && correctAnswer === choice ? 'is-correct' : '',
                      revealed && selectedChoice === choice && correctAnswer !== choice ? 'is-wrong' : '',
                    )}
                    onClick={() => submitChoice(choice)}
                    disabled={revealed}
                  >
                    <span className="arcade-choice__label">Peak Position</span>
                    <strong className="arcade-choice__value">#{choice}</strong>
                  </button>
                ))}
              </div>

              {revealed && correctAnswer !== null ? (
                <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                  {wasCorrect
                    ? `Correct. ${currentRound.title} peaked at #${correctAnswer}.`
                    : `Not this time. ${currentRound.title} peaked at #${correctAnswer}.`}
                </div>
              ) : (
                <div className="arcade-feedback arcade-feedback--info">Choose the highest chart position that song reached.</div>
              )}
            </>
          ) : (
            <div className="arcade-empty">{hasRounds ? 'Loading the next hit.' : 'No guess-the-peak rounds available.'}</div>
          )}
        </GamePanel>
      </ArcadeShell>
    </section>
  )
}

