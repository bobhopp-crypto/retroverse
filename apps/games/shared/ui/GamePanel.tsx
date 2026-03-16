import type { ReactNode } from 'react'
import type { ArcadeTone } from './arcadeTheme'
import { joinArcadeClasses } from './arcadeTheme'

type GamePanelProps = {
  title?: string
  eyebrow?: string
  footer?: ReactNode
  className?: string
  tone?: ArcadeTone
  children: ReactNode
}

export default function GamePanel({ title, eyebrow, footer, className, tone = 'default', children }: GamePanelProps) {
  return (
    <section
      className={joinArcadeClasses(
        'arcade-panel',
        tone !== 'default' ? `arcade-panel--${tone}` : '',
        className,
      )}
    >
      {(eyebrow || title) && (
        <header className="arcade-panel__header">
          {eyebrow ? <span className="arcade-panel__eyebrow">{eyebrow}</span> : null}
          {title ? <h2 className="arcade-panel__title">{title}</h2> : null}
        </header>
      )}
      <div className="arcade-panel__body">{children}</div>
      {footer ? <footer className="arcade-panel__footer">{footer}</footer> : null}
    </section>
  )
}
