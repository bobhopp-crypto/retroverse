/**
 * Normalize artist/title text for chart search.
 * - lowercase
 * - trim whitespace
 * - replace common stylized punctuation (P!nk → Pink)
 * - remove remaining punctuation, collapse spaces
 */
const STYLIZED_REPLACEMENTS: [string, string][] = [
  ['!', 'i'], // P!nk → Pink
  ['@', 'a'],
  ['0', 'o'],
  ['1', 'i'],
  ['3', 'e'],
  ['$', 's'],
]

function applyStylizedReplacements(s: string): string {
  let out = s
  for (const [from, to] of STYLIZED_REPLACEMENTS) {
    out = out.split(from).join(to)
  }
  return out
}

export function normalizeForSearch(value: string): string {
  if (!value || typeof value !== 'string') return ''
  const trimmed = value.trim().toLowerCase()
  const withStylized = applyStylizedReplacements(trimmed)
  return withStylized
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

/**
 * Returns true if the normalized query matches the normalized field (substring).
 */
export function searchMatch(query: string, artist: string, title: string): boolean {
  const q = normalizeForSearch(query)
  if (!q) return false
  const a = normalizeForSearch(artist)
  const t = normalizeForSearch(title)
  return a.includes(q) || t.includes(q)
}
