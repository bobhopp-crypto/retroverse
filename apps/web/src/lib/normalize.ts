const DIACRITICS_PATTERN = /[\u0300-\u036f]/g
const BRACKETED_TEXT_PATTERN = /\([^)]*\)|\[[^\]]*\]/g
const ARTIST_COLLAB_TAIL_PATTERN = /\b(?:feat\.?|ft\.?|featuring|with)\b.*$/g
const ARTIST_LEADING_ARTICLE_PATTERN = /^the\s+/g
const ARTIST_PUNCTUATION_PATTERN = /[.,\-_/'"]/g
const TITLE_FEAT_TAIL_PATTERN = /\b(?:feat\.?|ft\.?|featuring)\b.*$/g
const GENERAL_PUNCTUATION_PATTERN = /[^a-z0-9\s]/g
const MULTISPACE_PATTERN = /\s+/g

const normalizeBase = (value: string): string =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(DIACRITICS_PATTERN, '')

export const normalizeArtist = (name: string): string =>
  normalizeBase(name)
    .replace(BRACKETED_TEXT_PATTERN, ' ')
    .replace(ARTIST_COLLAB_TAIL_PATTERN, ' ')
    .replace(ARTIST_LEADING_ARTICLE_PATTERN, '')
    .replace(ARTIST_PUNCTUATION_PATTERN, ' ')
    .replace(MULTISPACE_PATTERN, ' ')
    .trim()

export const normalizeTitle = (title: string): string =>
  normalizeBase(title)
    .replace(BRACKETED_TEXT_PATTERN, ' ')
    .replace(TITLE_FEAT_TAIL_PATTERN, ' ')
    .replace(GENERAL_PUNCTUATION_PATTERN, ' ')
    .replace(MULTISPACE_PATTERN, ' ')
    .trim()
