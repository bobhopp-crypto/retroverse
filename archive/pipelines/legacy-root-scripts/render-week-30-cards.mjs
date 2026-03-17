import fs from 'node:fs/promises'
import path from 'node:path'
import Database from 'better-sqlite3'
import { chromium } from 'playwright'

const ROOT = process.cwd()
const DB_PATH = path.join(ROOT, 'raw-data', 'billboard-hot-100.db')
const LIB_PATH = path.join(ROOT, 'data', 'retro-verse-1974-weekly-data.md')
const OUTPUT_DIR = path.join(ROOT, 'public', 'cards', '1974', 'week-30')
const REVIEW_PAGE_PATH = path.join(ROOT, 'public', '1974', 'review-week-30.html')

const TARGET_ISSUE_DATE = '1974-08-03'
const WEEK_RANGE = '1974-07-29 to 1974-08-04'

const SECTION_HEADERS = {
  movies: 'Movies',
  textures: 'Cultural Textures',
  moods: 'Mood Tags',
  tvRefs: 'TV References',
  tones: 'Headline Tones',
}

function seededRandom(seed) {
  let state = seed >>> 0
  return () => {
    state += 0x6d2b79f5
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function shuffle(source, seed) {
  const values = [...source]
  const rand = seededRandom(seed)
  for (let i = values.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rand() * (i + 1))
    ;[values[i], values[j]] = [values[j], values[i]]
  }
  return values
}

function parseListSection(markdown, heading) {
  const escapedHeading = heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const pattern = new RegExp(`##\\s+${escapedHeading}\\n([\\s\\S]*?)(?=\\n##\\s+|$)`)
  const match = markdown.match(pattern)
  if (!match) {
    throw new Error(`Missing section "${heading}" in ${LIB_PATH}`)
  }

  return match[1]
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.startsWith('- '))
    .map((line) => line.slice(2).trim())
    .filter(Boolean)
}

function validateUnique(values, label) {
  const unique = [...new Set(values)]
  if (unique.length !== values.length) {
    throw new Error(`${label} contains duplicates; expected unique entries.`)
  }
  return unique
}

function buildAssignments(top40, libraries) {
  const movies = shuffle(validateUnique(libraries.movies, 'Movies'), 1974301).slice(0, 40)
  const textures = shuffle(validateUnique(libraries.textures, 'Cultural Textures'), 1974302).slice(0, 40)

  if (movies.length < 40) throw new Error('Need at least 40 unique movies for week-30 build.')
  if (textures.length < 40) throw new Error('Need at least 40 unique cultural textures for week-30 build.')

  const moods = shuffle(validateUnique(libraries.moods, 'Mood Tags'), 1974303)
  const tvRefs = shuffle(validateUnique(libraries.tvRefs, 'TV References'), 1974304)
  const tones = shuffle(validateUnique(libraries.tones, 'Headline Tones'), 1974305)

  if (moods.length < 20) throw new Error('Need at least 20 unique mood tags for max-repeat=2 across 40 cards.')
  if (tvRefs.length < 20) throw new Error('Need at least 20 unique TV references for max-repeat=2 across 40 cards.')
  if (tones.length < 20) throw new Error('Need at least 20 unique headline tones for max-repeat=2 across 40 cards.')

  const moodCounts = new Map()
  const tvCounts = new Map()
  const toneCounts = new Map()

  return top40.map((entry, index) => {
    const mood = moods[index % moods.length]
    const tvRef = tvRefs[index % tvRefs.length]
    const tone = tones[index % tones.length]

    moodCounts.set(mood, (moodCounts.get(mood) || 0) + 1)
    tvCounts.set(tvRef, (tvCounts.get(tvRef) || 0) + 1)
    toneCounts.set(tone, (toneCounts.get(tone) || 0) + 1)

    if (moodCounts.get(mood) > 2) throw new Error(`Mood tag repeat limit exceeded for "${mood}"`)
    if (tvCounts.get(tvRef) > 2) throw new Error(`TV reference repeat limit exceeded for "${tvRef}"`)
    if (toneCounts.get(tone) > 2) throw new Error(`Headline tone repeat limit exceeded for "${tone}"`)

    return {
      ...entry,
      movie: movies[index],
      cultural_texture: textures[index],
      mood_tag: mood,
      tv_reference: tvRef,
      headline_tone: tone,
      date_range: WEEK_RANGE,
      chart_date: TARGET_ISSUE_DATE,
      is_anchor: entry.rank === 1,
    }
  })
}

function cardHtml(record) {
  const anchorClass = record.is_anchor ? ' anchor' : ''
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, initial-scale=1" />
    <title>Week 30 Rank ${String(record.rank).padStart(2, '0')}</title>
    <style>
      :root {
        --ink: #f3ecde;
        --soft: #d9c6a0;
        --gold: #d9a547;
        --line: rgba(246, 221, 174, 0.45);
      }

      * { box-sizing: border-box; }
      html, body {
        margin: 0;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        font-family: 'Trebuchet MS', 'Gill Sans', 'Verdana', sans-serif;
        background: #050506;
      }

      .card {
        position: relative;
        width: 1080px;
        height: 1920px;
        padding: 44px;
        color: var(--ink);
        background:
          radial-gradient(circle at 10% 9%, rgba(255, 188, 98, 0.24), transparent 34%),
          radial-gradient(circle at 90% 12%, rgba(118, 53, 116, 0.28), transparent 41%),
          radial-gradient(circle at 20% 88%, rgba(255, 111, 66, 0.2), transparent 35%),
          linear-gradient(160deg, #1f1a2d 0%, #151225 36%, #171112 100%);
      }

      .card::before {
        content: '';
        position: absolute;
        inset: 20px;
        border: 6px solid var(--line);
        border-radius: 26px;
        box-shadow: inset 0 0 0 2px rgba(255, 213, 145, 0.35), 0 0 0 1px rgba(0, 0, 0, 0.35);
        pointer-events: none;
      }

      .card::after {
        content: '';
        position: absolute;
        inset: 0;
        background-image: radial-gradient(rgba(255, 236, 193, 0.08) 1px, transparent 1px);
        background-size: 4px 4px;
        mix-blend-mode: soft-light;
        opacity: 0.55;
        pointer-events: none;
      }

      .anchor {
        background:
          radial-gradient(circle at 8% 6%, rgba(255, 220, 112, 0.42), transparent 37%),
          radial-gradient(circle at 88% 12%, rgba(152, 83, 170, 0.34), transparent 41%),
          radial-gradient(circle at 22% 87%, rgba(255, 122, 62, 0.32), transparent 37%),
          linear-gradient(160deg, #2a203a 0%, #1a1430 32%, #1b1413 100%);
      }

      .anchor::before {
        border-width: 10px;
        box-shadow: inset 0 0 0 3px rgba(255, 233, 170, 0.45), 0 0 42px rgba(247, 187, 94, 0.33);
      }

      .layout {
        position: relative;
        z-index: 2;
        width: 100%;
        height: 100%;
        display: grid;
        grid-template-rows: auto auto 1fr auto;
        gap: 20px;
      }

      .topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--soft);
        font-size: 24px;
        letter-spacing: 2px;
        text-transform: uppercase;
      }

      .sigil {
        padding: 8px 14px;
        border: 2px solid rgba(255, 214, 147, 0.5);
        border-radius: 999px;
        background: rgba(18, 15, 20, 0.46);
      }

      .hero {
        display: grid;
        gap: 10px;
        border: 3px solid rgba(255, 214, 147, 0.36);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(33, 28, 41, 0.7), rgba(14, 12, 18, 0.7));
        padding: 22px;
      }

      .anchor .hero {
        border-width: 5px;
        border-color: rgba(255, 219, 138, 0.65);
        box-shadow: 0 0 36px rgba(225, 167, 81, 0.28);
        padding: 28px;
      }

      .rankline {
        display: flex;
        align-items: baseline;
        gap: 16px;
      }

      .rank {
        font-size: 72px;
        font-weight: 900;
        line-height: 1;
        color: var(--gold);
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
      }

      .anchor .rank { font-size: 112px; }

      .title {
        margin: 0;
        font-size: 62px;
        line-height: 1.03;
        letter-spacing: 0.3px;
      }

      .anchor .title {
        font-size: 78px;
        text-shadow: 0 3px 18px rgba(251, 212, 136, 0.22);
      }

      .artist {
        margin: 0;
        color: #ffe8bc;
        font-size: 36px;
      }

      .anchor .artist { font-size: 44px; }

      .context {
        display: grid;
        gap: 12px;
      }

      .context-chip {
        border: 2px solid rgba(245, 212, 153, 0.33);
        border-radius: 16px;
        background: rgba(14, 12, 17, 0.62);
        padding: 14px 16px;
      }

      .label {
        margin: 0 0 6px;
        color: var(--soft);
        font-size: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
      }

      .value {
        margin: 0;
        font-size: 30px;
        line-height: 1.18;
      }

      .anchor .value { font-size: 34px; }

      .stats {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .stat {
        border: 2px dashed rgba(243, 204, 138, 0.35);
        border-radius: 14px;
        padding: 12px 14px;
        background: rgba(10, 8, 12, 0.52);
      }

      .stat h3 {
        margin: 0;
        color: var(--soft);
        font-size: 17px;
        letter-spacing: 1px;
        text-transform: uppercase;
      }

      .stat p {
        margin: 6px 0 0;
        font-size: 32px;
        color: #fff0c9;
      }
    </style>
  </head>
  <body>
    <article class="card${anchorClass}">
      <section class="layout">
        <header class="topline">
          <span class="sigil">Week 30 · 1974</span>
          <span>${record.chart_date}</span>
        </header>

        <section class="hero">
          <div class="rankline">
            <span class="rank">#${record.rank}</span>
            <h1 class="title">${escapeHtml(record.title)}</h1>
          </div>
          <p class="artist">${escapeHtml(record.artist)}</p>
        </section>

        <section class="context">
          <div class="context-chip">
            <p class="label">Movie Pull</p>
            <p class="value">${escapeHtml(record.movie)}</p>
          </div>

          <div class="context-chip">
            <p class="label">Cultural Texture</p>
            <p class="value">${escapeHtml(record.cultural_texture)}</p>
          </div>

          <div class="context-chip">
            <p class="label">TV Echo</p>
            <p class="value">${escapeHtml(record.tv_reference)}</p>
          </div>

          <div class="stats">
            <div class="stat">
              <h3>Mood Tag</h3>
              <p>${escapeHtml(record.mood_tag)}</p>
            </div>
            <div class="stat">
              <h3>Headline Tone</h3>
              <p>${escapeHtml(record.headline_tone)}</p>
            </div>
          </div>
        </section>

        <section class="stats">
          <div class="stat">
            <h3>Weeks on Chart</h3>
            <p>${record.weeks_on_chart}</p>
          </div>
          <div class="stat">
            <h3>Peak Position</h3>
            <p>${record.peak_position}</p>
          </div>
        </section>
      </section>
    </article>
  </body>
</html>`
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function buildReviewPage() {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>Week 30 Review</title>
    <style>
      html, body {
        margin: 0;
        width: 100%;
        height: 100%;
        background: #000;
        overflow: hidden;
      }

      .stack {
        width: 100vw;
        height: 100vh;
        overflow-y: auto;
        overflow-x: hidden;
        scroll-snap-type: y mandatory;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
      }

      .slide {
        width: 100vw;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        scroll-snap-align: start;
        scroll-snap-stop: always;
        background: #000;
      }

      .slide img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        user-select: none;
        -webkit-user-drag: none;
        pointer-events: none;
      }

      .stack::-webkit-scrollbar { display: none; }
    </style>
  </head>
  <body>
    <main id="stack" class="stack" aria-label="Week 30 artwork review"></main>
    <script>
      const container = document.getElementById('stack')
      for (let rank = 1; rank <= 40; rank += 1) {
        const label = String(rank).padStart(2, '0')
        const slide = document.createElement('section')
        slide.className = 'slide'

        const image = document.createElement('img')
        image.src = '../cards/1974/week-30/week-30-rank-' + label + '.png'
        image.alt = 'Week 30 rank ' + label + ' card'
        image.decoding = 'async'
        image.loading = rank <= 2 ? 'eager' : 'lazy'

        slide.appendChild(image)
        container.appendChild(slide)
      }
    </script>
  </body>
</html>`
}

async function renderCards(records) {
  await fs.mkdir(OUTPUT_DIR, { recursive: true })
  const existing = await fs.readdir(OUTPUT_DIR)
  await Promise.all(
    existing
      .filter((file) => /^week-30-rank-\d{2}\.png$/.test(file))
      .map((file) => fs.unlink(path.join(OUTPUT_DIR, file))),
  )

  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
  })

  try {
    for (const record of records) {
      const html = cardHtml(record)
      const fileName = `week-30-rank-${String(record.rank).padStart(2, '0')}.png`
      const outPath = path.join(OUTPUT_DIR, fileName)

      await page.setContent(html, { waitUntil: 'networkidle' })
      await page.locator('.card').screenshot({ path: outPath, type: 'png' })
    }
  } finally {
    await page.close()
    await browser.close()
  }
}

async function main() {
  const markdown = await fs.readFile(LIB_PATH, 'utf8')

  const libraries = {
    movies: parseListSection(markdown, SECTION_HEADERS.movies),
    textures: parseListSection(markdown, SECTION_HEADERS.textures),
    moods: parseListSection(markdown, SECTION_HEADERS.moods),
    tvRefs: parseListSection(markdown, SECTION_HEADERS.tvRefs),
    tones: parseListSection(markdown, SECTION_HEADERS.tones),
  }

  const db = new Database(DB_PATH, { readonly: true })

  const query = `
SELECT
  ee.rank AS rank,
  w.title_display AS title,
  IFNULL(p.name_display, '') AS artist,
  ee.weeks_on_chart AS weeks_on_chart,
  ee.peak_pos AS peak_position
FROM event e
JOIN event_entry ee ON ee.event_id = e.event_id
JOIN work w ON w.work_id = ee.work_id
LEFT JOIN person p ON p.person_id = w.primary_person_id
WHERE e.issue_date = ?
  AND ee.rank BETWEEN 1 AND 40
ORDER BY ee.rank
`

  const top40 = db.prepare(query).all(TARGET_ISSUE_DATE)
  db.close()

  if (top40.length !== 40) {
    throw new Error(`Expected 40 records for ${TARGET_ISSUE_DATE}, got ${top40.length}`)
  }

  const assigned = buildAssignments(top40, libraries)

  await renderCards(assigned)
  await fs.mkdir(path.dirname(REVIEW_PAGE_PATH), { recursive: true })
  await fs.writeFile(REVIEW_PAGE_PATH, buildReviewPage(), 'utf8')

  console.log(`[week-30] rendered ${assigned.length} cards to ${OUTPUT_DIR}`)
  console.log(`[week-30] review page: ${REVIEW_PAGE_PATH}`)
}

main().catch((error) => {
  console.error(`[week-30][fatal] ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
})
