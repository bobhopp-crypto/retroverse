import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArcadeShell from '../../../../games/shared/ui/ArcadeShell.tsx'
import GamePanel from '../../../../games/shared/ui/GamePanel.tsx'
import { joinArcadeClasses } from '../../../../games/shared/ui/arcadeTheme.ts'
import type { ChartClimberRound } from '../../lib/arcadeClient'
import { buildNumberChoices, formatChartPosition } from './arcadeUtils'
import { chartClimberDemoRounds } from './demoRounds'
import './arcade.css'
import { useArcadeRoundQueue } from './useArcadeRoundQueue'

const BATCH_SIZE = 6

export default function ChartClimberGame() {
  const { currentRound, hasRounds, loading, message, mode, nextRound, reload, roundNumber } = useArcadeRoundQueue<ChartClimberRound>({
    endpoint: '/chart-climber',
    batchSize: BATCH_SIZE,
    fallbackRounds: chartClimberDemoRounds,
  })
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [choices, setChoices] = useState<number[]>([])
  const [selectedChoice, setSelectedChoice] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null)

  useEffect(() => {
    const correct = currentRound?.positions[4]
    setChoices(typeof correct === 'number' ? buildNumberChoices(correct) : [])
    setSelectedChoice(null)
    setRevealed(false)
    setWasCorrect(null)
  }, [currentRound, roundNumber])

  const correctAnswer = currentRound?.positions[4] ?? null
  const trendLabel =
    currentRound && currentRound.positions.length === 5
      ? currentRound.positions[4]! < currentRound.positions[0]!
        ? 'Climbing toward #1'
        : currentRound.positions[4]! > currentRound.positions[0]!
          ? 'Losing ground'
          : 'Holding steady'
      : 'Waiting for a new round'

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
    setSelectedChoice(null)
    setRevealed(true)
    setWasCorrect(false)
    setStreak(0)
  }

  const goToNextRound = () => {
    void nextRound()
  }

  const refreshRounds = () => {
    void reload()
  }

  const footer = (
    <div className="arcade-actions">
      <button type="button" className="arcade-button arcade-button--primary" onClick={goToNextRound} disabled={loading}>
        {revealed ? 'Next Round' : 'Skip Round'}
      </button>
      {!revealed ? (
        <button type="button" className="arcade-button arcade-button--ghost" onClick={revealAnswer} disabled={!currentRound}>
          Reveal Answer
        </button>
      ) : null}
      <button type="button" className="arcade-button arcade-button--secondary" onClick={refreshRounds} disabled={loading}>
        Refresh Queue
      </button>
    </div>
  )

  return (
    <section className="arcade-page">
      <ArcadeShell
        title="Chart Climber"
        subtitle="Read the first four chart snapshots, then predict the fifth position in the run."
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
              {mode === 'live' ? 'Live queue' : 'Demo fallback'}
            </span>
          </div>
        }
        footer={footer}
        sidePanel={
          <>
            <GamePanel eyebrow="Now Playing" title={currentRound ? `${currentRound.artist} - ${currentRound.title}` : 'Queue status'}>
              {currentRound ? (
                <>
                  <div className="arcade-detail-list">
                    <div className="arcade-detail-row">
                      <span>Year</span>
                      <strong>{currentRound.year}</strong>
                    </div>
                    <div className="arcade-detail-row">
                      <span>Trend</span>
                      <strong>{trendLabel}</strong>
                    </div>
                    <div className="arcade-detail-row">
                      <span>Best rank shown</span>
                      <strong>{formatChartPosition(Math.min(...currentRound.positions))}</strong>
                    </div>
                  </div>
                  {revealed && correctAnswer !== null ? (
                    <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                      Week five landed at <strong>{formatChartPosition(correctAnswer)}</strong>.
                    </div>
                  ) : (
                    <p className="arcade-supporting">Lower numbers are stronger. Read the slope and commit to the next move.</p>
                  )}
                </>
              ) : (
                <div className="arcade-empty">No playable rounds are available right now.</div>
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
        <GamePanel eyebrow="Round Objective" title="Predict Week Five">
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

              <p className="arcade-prompt">These are the first four chart weeks in sequence. What position came next?</p>

              <div className="arcade-sequence-grid">
                {currentRound.positions.slice(0, 4).map((position, index) => (
                  <div key={`${position}-${index}`} className="arcade-sequence-card">
                    <span className="arcade-sequence-card__label">Week {index + 1}</span>
                    <strong className="arcade-sequence-card__value">{formatChartPosition(position)}</strong>
                  </div>
                ))}
                <div className="arcade-sequence-card arcade-sequence-card--masked">
                  <span className="arcade-sequence-card__label">Week 5</span>
                  <strong className="arcade-sequence-card__value">?</strong>
                </div>
              </div>

              <div className="arcade-choice-grid">
                {choices.map((choice) => (
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
                    <span className="arcade-choice__label">Possible Position</span>
                    <strong className="arcade-choice__value">{formatChartPosition(choice)}</strong>
                  </button>
                ))}
              </div>

              {revealed && correctAnswer !== null ? (
                <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                  {wasCorrect
                    ? `Correct. ${currentRound.title} moved to ${formatChartPosition(correctAnswer)} in week five.`
                    : `The correct answer was ${formatChartPosition(correctAnswer)}.`}
                </div>
              ) : (
                <div className="arcade-feedback arcade-feedback--info">Pick the number that best continues the chart movement.</div>
              )}
            </>
          ) : (
            <div className="arcade-empty">{hasRounds ? 'Loading the next chart run.' : 'No chart rounds available.'}</div>
          )}
        </GamePanel>
      </ArcadeShell>
    </section>
  )
}

