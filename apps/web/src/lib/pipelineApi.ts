const LOCAL_PIPELINE_API_BASE = 'http://127.0.0.1:8787'

const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '')

const isLocalHostname = (hostname: string) => {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]'
}

const resolveDefaultPipelineApiBase = () => {
  if (typeof window !== 'undefined' && (import.meta.env.DEV || isLocalHostname(window.location.hostname))) {
    return LOCAL_PIPELINE_API_BASE
  }

  return '/api'
}

const configuredPipelineApiBase =
  typeof import.meta.env.VITE_PIPELINE_API === 'string' ? import.meta.env.VITE_PIPELINE_API.trim() : ''

export const PIPELINE_API_BASE = trimTrailingSlash(configuredPipelineApiBase || resolveDefaultPipelineApiBase())
