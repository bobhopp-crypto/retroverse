import { type ReactNode } from 'react'
import { Link, type LinkProps } from 'react-router-dom'

function joinClasses(...classes: Array<string | undefined | false>): string {
  return classes.filter(Boolean).join(' ')
}

const CARD_BASE_CLASS_NAME =
  'group rounded-xl border border-[var(--rv2)] bg-[var(--rv3)] text-[var(--rv1)] no-underline shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--rv5)] hover:brightness-[1.02] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--rv5)]'

const PANEL_BASE_CLASS_NAME = 'rounded-2xl border border-[var(--rv2)] bg-[var(--rv3)] shadow-sm'

export const CARD_ICON_CHIP_CLASS_NAME =
  'inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-[var(--rv2)] bg-[var(--rv4)] text-[var(--rv1)]'

type CardLinkProps = LinkProps & {
  children: ReactNode
  className?: string
}

export function CardLink({ children, className, ...props }: CardLinkProps) {
  return (
    <Link {...props} className={joinClasses(CARD_BASE_CLASS_NAME, className)}>
      {children}
    </Link>
  )
}

type PanelProps = {
  children: ReactNode
  className?: string
}

export function Panel({ children, className }: PanelProps) {
  return <div className={joinClasses(PANEL_BASE_CLASS_NAME, className)}>{children}</div>
}
