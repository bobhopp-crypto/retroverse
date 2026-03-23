/** Base path for static data assets (works at root or subpath) */
const DATA_BASE = `${(import.meta.env.BASE_URL || '/').replace(/\/$/, '') || ''}/data`

/** Resolve a data file path for fetch (e.g. dataUrl('charts/1983.json') or dataUrl('video-index-1960s.json')) */
export const dataUrl = (path: string) => `${DATA_BASE}/${path.replace(/^\//, '')}`

export const VIDEO_INDEX_URL =
  import.meta.env.VITE_VIDEO_INDEX_URL || dataUrl('video-index.json')
export const HISTORY_INDEX_URL =
  import.meta.env.VITE_HISTORY_INDEX_URL || dataUrl('history-index.json')
