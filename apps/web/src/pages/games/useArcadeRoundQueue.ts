import { useEffect, useRef, useState } from 'react'
import { fetchArcadeRounds } from '../../lib/arcadeClient'
import { shuffleArray } from './arcadeUtils'

type ArcadeQueueMode = 'loading' | 'live' | 'demo'

type UseArcadeRoundQueueOptions<T> = {
  endpoint: string
  batchSize?: number
  fallbackRounds: T[]
}

export function useArcadeRoundQueue<T>({ endpoint, batchSize = 6, fallbackRounds }: UseArcadeRoundQueueOptions<T>) {
  const requestRef = useRef(0)
  const [rounds, setRounds] = useState<T[]>([])
  const [cursor, setCursor] = useState(0)
  const [roundNumber, setRoundNumber] = useState(1)
  const [mode, setMode] = useState<ArcadeQueueMode>('loading')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState<string | null>(null)

  const loadBatch = async (nextRoundNumber: number) => {
    const requestId = requestRef.current + 1
    requestRef.current = requestId
    setLoading(true)

    try {
      const liveRounds = await fetchArcadeRounds<T>(endpoint, batchSize)

      if (requestRef.current !== requestId) return

      if (liveRounds.length > 0) {
        setRounds(liveRounds)
        setCursor(0)
        setRoundNumber(nextRoundNumber)
        setMode('live')
        setMessage(null)
        return
      }

      throw new Error('No live rounds available')
    } catch (error) {
      if (requestRef.current !== requestId) return

      const fallbackBatch = shuffleArray(fallbackRounds)
      setRounds(fallbackBatch)
      setCursor(0)
      setRoundNumber(nextRoundNumber)
      setMode('demo')

      const reason = error instanceof Error && error.message ? error.message : 'Live feed unavailable'
      setMessage(fallbackBatch.length > 0 ? `${reason}. Demo mode enabled.` : reason)
    } finally {
      if (requestRef.current === requestId) {
        setLoading(false)
      }
    }
  }

  useEffect(() => {
    void loadBatch(1)

    return () => {
      requestRef.current += 1
    }
  }, [batchSize, endpoint, fallbackRounds])

  const nextRound = async () => {
    const nextRoundNumber = roundNumber + 1

    if (cursor + 1 < rounds.length) {
      setCursor(cursor + 1)
      setRoundNumber(nextRoundNumber)
      return
    }

    await loadBatch(nextRoundNumber)
  }

  const reload = async () => {
    await loadBatch(roundNumber)
  }

  return {
    currentRound: rounds[cursor] ?? null,
    hasRounds: rounds.length > 0,
    loading,
    mode,
    message,
    nextRound,
    reload,
    roundNumber,
  }
}

