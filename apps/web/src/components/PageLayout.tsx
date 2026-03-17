import type { PropsWithChildren } from 'react'

/**
 * Consistent page wrapper: padding, spacing, min-height.
 * Use for pages that need the standard layout container.
 */
export default function PageLayout({ children }: PropsWithChildren) {
  return <div className="page-layout">{children}</div>
}
