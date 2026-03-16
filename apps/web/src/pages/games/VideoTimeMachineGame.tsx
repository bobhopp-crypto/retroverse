import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArcadeShell from '../../../../games/shared/ui/ArcadeShell.tsx'
import GamePanel from '../../../../games/shared/ui/GamePanel.tsx'
import { joinArcadeClasses } from '../../../../games/shared/ui/arcadeTheme.ts'
import type { VideoMetadataRecord } from '../../lib/arcadeClient'
import { buildNumberChoices } from './arcadeUtils'
import { videoTimeMachineDemoRounds } from './demoRounds'
import './arcade.css'
import { useArcadeRoundQueue } from './useArcadeRoundQueue'

const BATCH_SIZE = 6

export default function VideoTimeMachineGame() {
  const { currentRound, hasRounds, loading, message, mode, nextRound, reload, roundNumber } = useArcadeRoundQueue<VideoMetadataRecord>({
    endpoint: '/video-year',
    batchSize: BATCH_SIZE,
    fallbackRounds: videoTimeMachineDemoRounds,
  })
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [choices, setChoices] = useState<number[]>([])
  const [selectedChoice, setSelectedChoice] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null)
  const [imageFailed, setImageFailed] = useState(false)

  useEffect(() => {
    setChoices(currentRound ? buildNumberChoices(currentRound.year, { min: 1950, max: 1999, offsets: [-1, 1, -2, 2, -3, 3, -5, 5, -7, 7] }) : [])
    setSelectedChoice(null)
    setRevealed(false)
    setWasCorrect(null)
    setImageFailed(false)
  }, [currentRound, roundNumber])

  const correctAnswer = currentRound?.year ?? null

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

  const showThumbnail = Boolean(currentRound?.thumbnail) && !imageFailed

  return (
    <section className="arcade-page">
      <ArcadeShell
        title="Video Time Machine"
        subtitle="Read the frame, the artist, and the title, then pin the video to the right year."
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
              {mode === 'live' ? 'Live video pool' : 'Demo fallback'}
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
                Reveal Year
              </button>
            ) : null}
            <button type="button" className="arcade-button arcade-button--secondary" onClick={() => void reload()} disabled={loading}>
              Refresh Queue
            </button>
          </div>
        }
        sidePanel={
          <>
            <GamePanel eyebrow="Visual Cue" title={currentRound ? `${currentRound.artist} - ${currentRound.title}` : 'Preview'}>
              <div className="arcade-image-frame">
                {currentRound && showThumbnail ? (
                  <img
                    src={currentRound.thumbnail}
                    alt={`${currentRound.artist} ${currentRound.title}`}
                    onError={() => setImageFailed(true)}
                  />
                ) : (
                  <div className="arcade-image-placeholder">
                    <strong>{currentRound ? `${currentRound.artist} - ${currentRound.title}` : 'Awaiting frame'}</strong>
                    <span>{currentRound ? 'Thumbnail unavailable. Use the metadata clues.' : 'Load a round to begin.'}</span>
                  </div>
                )}
              </div>
              {revealed && correctAnswer !== null ? (
                <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                  Correct year: <strong>{correctAnswer}</strong>
                </div>
              ) : (
                <p className="arcade-supporting">If the image is missing, the round stays playable with title and artist clues.</p>
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
        <GamePanel eyebrow="Round Objective" title="Pin The Video To A Year">
          {currentRound ? (
            <>
              <div className="arcade-meta">
                <div className="arcade-meta__item">
                  Artist <strong>{currentRound.artist}</strong>
                </div>
                <div className="arcade-meta__item">
                  Title <strong>{currentRound.title}</strong>
                </div>
                <div className="arcade-meta__item">
                  Asset <strong>{showThumbnail ? 'Frame loaded' : 'Metadata only'}</strong>
                </div>
              </div>

              <p className="arcade-prompt">Choose the exact year this clip belongs to.</p>

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
                    <span className="arcade-choice__label">Release Year</span>
                    <strong className="arcade-choice__value">{choice}</strong>
                  </button>
                ))}
              </div>

              {revealed && correctAnswer !== null ? (
                <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                  {wasCorrect
                    ? `Correct. ${currentRound.title} lands in ${correctAnswer}.`
                    : `The right year was ${correctAnswer}.`}
                </div>
              ) : (
                <div className="arcade-feedback arcade-feedback--info">Look for hairstyle, lighting, wardrobe, and typography cues if the frame is available.</div>
              )}
            </>
          ) : (
            <div className="arcade-empty">{hasRounds ? 'Loading the next clip.' : 'No video rounds available.'}</div>
          )}
        </GamePanel>
      </ArcadeShell>
    </section>
  )
}

