import type { ReactNode } from 'react'
import type { ArcadeTone } from './arcadeTheme'
import { joinArcadeClasses } from './arcadeTheme'

export type ScoreBarItem = {
  label: string
  value: ReactNode
  tone?: ArcadeTone
}

type ScoreBarProps = {
  items: ScoreBarItem[]
}

export default function ScoreBar({ items }: ScoreBarProps) {
  if (items.length === 0) return null

  return (
    <div className="arcade-scorebar" role="list" aria-label="Game status">
      {items.map((item) => (
        <div
          key={item.label}
          role="listitem"
          className={joinArcadeClasses(
            'arcade-scorebar__item',
            item.tone && item.tone !== 'default' ? `arcade-scorebar__item--${item.tone}` : '',
          )}
        >
          <span className="arcade-scorebar__label">{item.label}</span>
          <strong className="arcade-scorebar__value">{item.value}</strong>
        </div>
      ))}
    </div>
  )
}
