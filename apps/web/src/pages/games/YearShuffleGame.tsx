import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ArcadeShell from '../../../../games/shared/ui/ArcadeShell.tsx'
import GamePanel from '../../../../games/shared/ui/GamePanel.tsx'
import { joinArcadeClasses } from '../../../../games/shared/ui/arcadeTheme.ts'
import type { YearShuffleRound } from '../../lib/arcadeClient'
import { yearShuffleDemoRounds } from './demoRounds'
import './arcade.css'
import { useArcadeRoundQueue } from './useArcadeRoundQueue'

const BATCH_SIZE = 6

type PickableEntry = YearShuffleRound['entries'][number] & {
  key: string
}

const makeEntryKey = (entry: YearShuffleRound['entries'][number], index: number) => `${entry.artist}::${entry.title}::${entry.year}::${index}`

const sortEntries = (entries: PickableEntry[]) =>
  [...entries].sort((left, right) => left.year - right.year || left.artist.localeCompare(right.artist) || left.title.localeCompare(right.title))

export default function YearShuffleGame() {
  const { currentRound, hasRounds, loading, message, mode, nextRound, reload, roundNumber } = useArcadeRoundQueue<YearShuffleRound>({
    endpoint: '/year-shuffle',
    batchSize: BATCH_SIZE,
    fallbackRounds: yearShuffleDemoRounds,
  })
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [entries, setEntries] = useState<PickableEntry[]>([])
  const [pickedKeys, setPickedKeys] = useState<string[]>([])
  const [revealed, setRevealed] = useState(false)
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null)

  useEffect(() => {
    const nextEntries = currentRound?.entries.map((entry, index) => ({ ...entry, key: makeEntryKey(entry, index) })) ?? []
    setEntries(nextEntries)
    setPickedKeys([])
    setRevealed(false)
    setWasCorrect(null)
  }, [currentRound, roundNumber])

  const selectedEntries = pickedKeys
    .map((key) => entries.find((entry) => entry.key === key))
    .filter((entry): entry is PickableEntry => entry !== undefined)

  const correctOrder = sortEntries(entries).map((entry) => entry.key)
  const progressLabel = `${pickedKeys.length}/4 selected`

  const gradeOrder = (nextKeys: string[]) => {
    const correct = nextKeys.length === correctOrder.length && nextKeys.every((key, index) => key === correctOrder[index])
    setRevealed(true)
    setWasCorrect(correct)
    setScore((value) => value + (correct ? 1 : 0))
    setStreak((value) => (correct ? value + 1 : 0))
  }

  const pickEntry = (entry: PickableEntry) => {
    if (revealed || pickedKeys.includes(entry.key)) return

    const nextKeys = [...pickedKeys, entry.key]
    setPickedKeys(nextKeys)

    if (nextKeys.length === entries.length && entries.length > 0) {
      gradeOrder(nextKeys)
    }
  }

  const resetOrder = () => {
    if (revealed) return
    setPickedKeys([])
  }

  return (
    <section className="arcade-page">
      <ArcadeShell
        title="Year Shuffle"
        subtitle="Tap the songs in chronological order, oldest to newest, and lock the full four-song sequence."
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
              {mode === 'live' ? 'Live chronology' : 'Demo fallback'}
            </span>
          </div>
        }
        footer={
          <div className="arcade-actions">
            {revealed ? (
              <button type="button" className="arcade-button arcade-button--primary" onClick={() => void nextRound()} disabled={loading}>
                Next Round
              </button>
            ) : (
              <button type="button" className="arcade-button arcade-button--primary" onClick={resetOrder} disabled={pickedKeys.length === 0}>
                Reset Order
              </button>
            )}
            <button type="button" className="arcade-button arcade-button--secondary" onClick={() => void reload()} disabled={loading}>
              Refresh Queue
            </button>
          </div>
        }
        sidePanel={
          <>
            <GamePanel eyebrow="Ordering Track" title="Your sequence">
              <div className="arcade-order-track">
                {Array.from({ length: 4 }).map((_, index) => {
                  const entry = selectedEntries[index]
                  return (
                    <div key={index} className="arcade-order-slot">
                      <strong>Slot {index + 1}</strong>
                      {entry ? (
                        <p>
                          {entry.artist}
                          <br />
                          {entry.title}
                          {revealed ? <><br />{entry.year}</> : null}
                        </p>
                      ) : (
                        <p>Tap a song card to place it here.</p>
                      )}
                    </div>
                  )
                })}
              </div>
              <div className="arcade-detail-row">
                <span>Progress</span>
                <strong>{progressLabel}</strong>
              </div>
            </GamePanel>

            <GamePanel eyebrow="Reveal" title="Correct chronology" tone={revealed ? (wasCorrect ? 'good' : 'warning') : 'default'}>
              {revealed ? (
                <div className="arcade-stack">
                  {sortEntries(entries).map((entry, index) => (
                    <div key={entry.key} className="arcade-detail-row">
                      <span>
                        {index + 1}. {entry.artist} - {entry.title}
                      </span>
                      <strong>{entry.year}</strong>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="arcade-supporting">Years stay hidden until you finish the order. Think in eras, not exact dates.</p>
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
        <GamePanel eyebrow="Round Objective" title="Build The Timeline">
          {currentRound ? (
            <>
              <p className="arcade-prompt">Start with the earliest song and finish with the most recent one.</p>

              <div className="arcade-order-grid">
                {entries.map((entry) => (
                  <button
                    key={entry.key}
                    type="button"
                    className={joinArcadeClasses('arcade-order-card', pickedKeys.includes(entry.key) ? 'is-picked' : '')}
                    onClick={() => pickEntry(entry)}
                    disabled={revealed || pickedKeys.includes(entry.key)}
                  >
                    <span className="arcade-order-card__label">Song clue</span>
                    <strong className="arcade-order-card__title">{entry.title}</strong>
                    <p className="arcade-order-card__artist">{entry.artist}</p>
                  </button>
                ))}
              </div>

              {revealed ? (
                <div className={joinArcadeClasses('arcade-feedback', wasCorrect ? 'arcade-feedback--correct' : 'arcade-feedback--wrong')}>
                  {wasCorrect ? 'Correct order. The timeline is locked.' : 'Order mismatch. Check the chronology in the side panel.'}
                </div>
              ) : (
                <div className="arcade-feedback arcade-feedback--info">Tap all four cards. The round grades automatically once your sequence is full.</div>
              )}
            </>
          ) : (
            <div className="arcade-empty">{hasRounds ? 'Loading the next shuffle.' : 'No year-shuffle rounds available.'}</div>
          )}
        </GamePanel>
      </ArcadeShell>
    </section>
  )
}
