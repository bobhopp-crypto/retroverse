import { getVideoPuzzles } from '../data/playablePools.js'
import type { VideoMetadataRecord } from '../types/gameData.js'

const randomInt = (maxExclusive: number) => Math.floor(Math.random() * maxExclusive)

export const generateVideoYearRound = async (): Promise<VideoMetadataRecord | null> => {
  const videos = await getVideoPuzzles()
  if (videos.length === 0) return null

  return videos[randomInt(videos.length)] ?? null
}
