const DEFAULT_OFFSETS = [-1, 1, -2, 2, -3, 3, -5, 5, -8, 8, -10, 10]

export const shuffleArray = <T>(items: T[]) => {
  const copy = [...items]
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1))
    ;[copy[index], copy[swapIndex]] = [copy[swapIndex]!, copy[index]!]
  }
  return copy
}

type BuildNumberChoicesOptions = {
  min?: number
  max?: number
  total?: number
  offsets?: number[]
}

export const buildNumberChoices = (
  correct: number,
  { min = 1, max = 100, total = 4, offsets = DEFAULT_OFFSETS }: BuildNumberChoicesOptions = {},
) => {
  if (!Number.isInteger(correct) || correct < min || correct > max || total < 2) return []

  const choices = new Set<number>([correct])

  for (const offset of offsets) {
    const candidate = correct + offset
    if (candidate < min || candidate > max) continue
    choices.add(candidate)
    if (choices.size === total) return shuffleArray(Array.from(choices))
  }

  for (let distance = 1; distance <= max - min && choices.size < total; distance += 1) {
    const lower = correct - distance
    const upper = correct + distance

    if (lower >= min) choices.add(lower)
    if (choices.size === total) break
    if (upper <= max) choices.add(upper)
  }

  for (let value = min; value <= max && choices.size < total; value += 1) {
    choices.add(value)
  }

  return shuffleArray(Array.from(choices)).slice(0, total)
}

export const formatChartPosition = (position: number) => `#${position}`

export const clampCount = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

