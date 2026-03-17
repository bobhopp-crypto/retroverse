/**
 * Slug utilities for song and artist routes.
 */

function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
}

export function songSlug(title: string, artist: string): string {
  return `${slugify(title)}|${slugify(artist)}`
}

export function artistSlug(artist: string): string {
  return slugify(artist)
}

export function parseSongSlug(slug: string): { titleSlug: string; artistSlug: string } | null {
  const i = slug.lastIndexOf("|")
  if (i < 0) return null
  return {
    titleSlug: slug.slice(0, i),
    artistSlug: slug.slice(i + 1),
  }
}

export function slugMatches(title: string, artist: string, parsed: { titleSlug: string; artistSlug: string }): boolean {
  return slugify(title) === parsed.titleSlug && slugify(artist) === parsed.artistSlug
}
