import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = {
  children: ReactNode
  /** Optional route/page name for context */
  fallbackRoute?: string
}

type State = {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const { error } = this.state
      const { fallbackRoute } = this.props
      return (
        <section
          className="hub-page bg-[var(--rv4)] text-[var(--rv1)]"
          style={{ padding: '2rem', maxWidth: '42rem', margin: '0 auto' }}
        >
          <h1 className="page-title">Something went wrong</h1>
          {fallbackRoute ? <p className="text-sm opacity-80 mb-2">Route: {fallbackRoute}</p> : null}
          <p className="text-sm text-[var(--rv1)] opacity-90 mb-4">{error.message}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg border border-[var(--rv2)] bg-[var(--rv5)] px-4 py-2 text-sm font-semibold text-[var(--rv3)]"
          >
            Reload page
          </button>
        </section>
      )
    }
    return this.props.children
  }
}
