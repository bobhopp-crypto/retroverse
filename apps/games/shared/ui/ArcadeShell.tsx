import type { ReactNode } from 'react'
import ScoreBar, { type ScoreBarItem } from './ScoreBar'
import { arcadeThemeStyle } from './arcadeTheme'

type ArcadeShellProps = {
  title: string
  subtitle: ReactNode
  stats?: ScoreBarItem[]
  headerMeta?: ReactNode
  sidePanel?: ReactNode
  footer?: ReactNode
  children: ReactNode
}

export default function ArcadeShell({ title, subtitle, stats = [], headerMeta, sidePanel, footer, children }: ArcadeShellProps) {
  return (
    <section className="arcade-shell" style={arcadeThemeStyle}>
      <header className="arcade-shell__header">
        <div className="arcade-shell__titleblock">
          <p className="arcade-shell__kicker">RetroVerse Arcade</p>
          <h1 className="arcade-shell__title">{title}</h1>
          <div className="arcade-shell__subtitle">{subtitle}</div>
        </div>
        {headerMeta ? <div className="arcade-shell__meta">{headerMeta}</div> : null}
      </header>

      <ScoreBar items={stats} />

      <div className={sidePanel ? 'arcade-shell__body arcade-shell__body--with-side' : 'arcade-shell__body'}>
        <div className="arcade-shell__main">{children}</div>
        {sidePanel ? <aside className="arcade-shell__side">{sidePanel}</aside> : null}
      </div>

      {footer ? <footer className="arcade-shell__footer">{footer}</footer> : null}
    </section>
  )
}

