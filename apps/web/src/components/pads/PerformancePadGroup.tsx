import type { CSSProperties, ReactNode } from 'react'
import './PerformancePad.css'

type Props = {
  title?: string
  columns: number
  children: ReactNode
  className?: string
}

export default function PerformancePadGroup({ columns, children, className }: Props) {
  const gridStyle = { '--perf-pad-columns': columns } as CSSProperties
  const classes = ['perf-pad-group', className].filter(Boolean).join(' ')

  return (
    <div className={classes}>
      <div className="perf-pad-grid" style={gridStyle}>
        {children}
      </div>
    </div>
  )
}
