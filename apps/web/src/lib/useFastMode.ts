import { useMemo } from 'react'

const SLOW_DOWNLINK_THRESHOLD_MBPS = 1.5

type NetworkInfo = {
  saveData?: boolean
  downlink?: number
  effectiveType?: string
}

type NavigatorWithConnection = Navigator & {
  connection?: NetworkInfo
  mozConnection?: NetworkInfo
  webkitConnection?: NetworkInfo
}

const readConnection = (): NetworkInfo | null => {
  if (typeof navigator === 'undefined') return null
  const value = navigator as NavigatorWithConnection
  return value.connection ?? value.mozConnection ?? value.webkitConnection ?? null
}

const isSlowConnection = (connection: NetworkInfo | null): boolean => {
  if (!connection) return false
  if (connection.saveData) return true
  if (typeof connection.downlink === 'number' && connection.downlink > 0 && connection.downlink <= SLOW_DOWNLINK_THRESHOLD_MBPS) {
    return true
  }
  const effectiveType = (connection.effectiveType ?? '').toLowerCase()
  return effectiveType === 'slow-2g' || effectiveType === '2g'
}

const queryForcesFastMode = (): boolean => {
  if (typeof window === 'undefined') return false
  const fast = new URLSearchParams(window.location.search).get('fast')
  if (!fast) return false
  return fast === '1' || fast.toLowerCase() === 'true'
}

export const shouldUseFastMode = (): boolean => {
  if (queryForcesFastMode()) return true
  return isSlowConnection(readConnection())
}

export const useFastMode = (): boolean => useMemo(() => shouldUseFastMode(), [])
