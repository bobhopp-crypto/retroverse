import fs from 'node:fs/promises'
import path from 'node:path'
import Database from 'better-sqlite3'
import { chromium } from 'playwright'

const ROOT = process.cwd()
const DB_PATH = path.join(ROOT, 'raw-data', 'billboard-hot-100.db')
const LIB_PATH = path.join(ROOT, 'data', 'retro-verse-1974-weekly-data.md')
const OUTPUT_DIR = path.join(ROOT, 'public', 'cards', '1974', 'week-30-illustrated')
const REVIEW_PAGE_PATH = path.join(ROOT, 'public', '1974', 'review-week-30-illustrated.html')

const TARGET_ISSUE_DATE = '1974-08-03'
const WEEK_RANGE = '1974-07-29 to 1974-08-04'

const SECTION_HEADERS = {
  movies: 'Movies',
  textures: 'Cultural Textures',
  moods: 'Mood Tags',
  tvRefs: 'TV References',
  tones: 'Headline Tones',
}

function hashString(value) {
  let hash = 2166136261
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
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

function randomFrom(values, rand) {
  return values[Math.floor(rand() * values.length)]
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

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function buildAmbientLines(record, libraries) {
  const seed = hashString(`${record.rank}|${record.title}|${record.artist}|ambient`)
  const rand = seededRandom(seed)

  const builders = [
    () => `In Theaters (1974): ${randomFrom(libraries.movies, rand)}`,
    () => `On Television: ${randomFrom(libraries.tvRefs, rand)}`,
    () => `Cultural Backdrop: ${randomFrom(libraries.textures, rand)}`,
    () => `Headlines: ${randomFrom(libraries.tones, rand)}`,
    () => `Mood: ${randomFrom(libraries.moods, rand)}`,
  ]

  const count = Math.floor(rand() * 4)
  const lines = []

  for (let i = 0; i < count; i += 1) {
    const lineBuilder = randomFrom(builders, rand)
    lines.push(lineBuilder())
  }

  return lines
}

function illustrationSvg(record) {
  const seed = hashString(`${record.rank}|${record.title}|${record.artist}|illustration`)
  const rand = seededRandom(seed)

  const centerX = 540 + (rand() - 0.5) * 110
  const centerY = 875 + (rand() - 0.5) * 90
  const haloRadius = 170 + rand() * 90

  const lines = []
  for (let i = 0; i < 14; i += 1) {
    const angle = (Math.PI * 2 * i) / 14 + rand() * 0.3
    const x1 = centerX + Math.cos(angle) * (140 + rand() * 40)
    const y1 = centerY + Math.sin(angle) * (140 + rand() * 40)
    const x2 = centerX + Math.cos(angle) * (260 + rand() * 90)
    const y2 = centerY + Math.sin(angle) * (260 + rand() * 90)
    lines.push(`<line x1="${x1.toFixed(2)}" y1="${y1.toFixed(2)}" x2="${x2.toFixed(2)}" y2="${y2.toFixed(2)}" />`)
  }

  const shards = []
  for (let i = 0; i < 8; i += 1) {
    const baseX = 170 + rand() * 740
    const baseY = 620 + rand() * 520
    const w = 60 + rand() * 120
    const h = 45 + rand() * 110
    const skew = (rand() - 0.5) * 80
    const points = [
      [baseX, baseY],
      [baseX + w, baseY + skew],
      [baseX + w * 0.6, baseY + h],
      [baseX - w * 0.2, baseY + h * 0.75],
    ]
      .map(([x, y]) => `${x.toFixed(2)},${y.toFixed(2)}`)
      .join(' ')
    shards.push(`<polygon points="${points}" />`)
  }

  const starbursts = []
  for (let i = 0; i < 11; i += 1) {
    const x = 120 + rand() * 840
    const y = 560 + rand() * 640
    const r = 6 + rand() * 14
    starbursts.push(`<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${r.toFixed(2)}" />`)
  }

  return `<svg class="art-svg" viewBox="0 0 1080 1920" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <radialGradient id="orb-${record.rank}" cx="50%" cy="45%" r="48%">
        <stop offset="0%" stop-color="rgba(255,220,145,0.76)"/>
        <stop offset="58%" stop-color="rgba(255,117,86,0.40)"/>
        <stop offset="100%" stop-color="rgba(30,16,32,0)"/>
      </radialGradient>
      <linearGradient id="ribbon-${record.rank}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="rgba(255,189,115,0.44)"/>
        <stop offset="100%" stop-color="rgba(153,88,174,0.32)"/>
      </linearGradient>
      <pattern id="paper-${record.rank}" width="24" height="24" patternUnits="userSpaceOnUse">
        <circle cx="4" cy="5" r="1.2" fill="rgba(255,243,211,0.08)" />
        <circle cx="15" cy="12" r="1" fill="rgba(250,214,167,0.06)" />
        <circle cx="21" cy="18" r="1.2" fill="rgba(255,240,188,0.05)" />
      </pattern>
    </defs>

    <rect x="0" y="0" width="1080" height="1920" fill="url(#paper-${record.rank})" />
    <circle cx="${centerX.toFixed(2)}" cy="${centerY.toFixed(2)}" r="${haloRadius.toFixed(2)}" fill="url(#orb-${record.rank})" />

    <g class="burst-lines">
      ${lines.join('')}
    </g>

    <g class="shards">
      ${shards.join('')}
    </g>

    <g class="stars">
      ${starbursts.join('')}
    </g>

    <rect x="160" y="560" width="760" height="720" rx="36" fill="url(#ribbon-${record.rank})" opacity="0.34" />
  </svg>`
}

function cardHtml(record) {
  const anchorClass = record.rank === 1 ? ' anchor' : ''
  const ambientList = record.ambient_lines
    .map((line) => `<li>${escapeHtml(line)}</li>`)
    .join('')

  const ambientBlock = ambientList
    ? `<section class="ambient">
      <ul>${ambientList}</ul>
    </section>`
    : ''

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, initial-scale=1" />
    <title>Week 30 Rank ${String(record.rank).padStart(2, '0')}</title>
    <style>
      :root {
        --ink: #f4e7ce;
        --ink-soft: #e0c79e;
        --gold: #e2aa59;
        --frame: rgba(248, 214, 158, 0.6);
      }

      * { box-sizing: border-box; }

      html,
      body {
        margin: 0;
        width: 1080px;
        height: 1920px;
        overflow: hidden;
        background: #070709;
        font-family: 'Trebuchet MS', 'Gill Sans', 'Verdana', sans-serif;
      }

      .card {
        position: relative;
        width: 1080px;
        height: 1920px;
        padding: 38px;
        color: var(--ink);
        background:
          radial-gradient(circle at 12% 8%, rgba(254, 176, 101, 0.27), transparent 33%),
          radial-gradient(circle at 84% 10%, rgba(121, 63, 138, 0.30), transparent 40%),
          radial-gradient(circle at 20% 90%, rgba(255, 97, 78, 0.24), transparent 35%),
          linear-gradient(167deg, #1e1729 0%, #14121f 34%, #1b1413 100%);
      }

      .card::before {
        content: '';
        position: absolute;
        inset: 16px;
        border: 9px double var(--frame);
        border-radius: 28px;
        box-shadow:
          inset 0 0 0 2px rgba(255, 230, 183, 0.27),
          inset 0 0 52px rgba(0, 0, 0, 0.34);
        pointer-events: none;
      }

      .card::after {
        content: '';
        position: absolute;
        inset: 0;
        background:
          repeating-linear-gradient(
            12deg,
            rgba(255, 228, 180, 0.026) 0,
            rgba(255, 228, 180, 0.026) 2px,
            transparent 2px,
            transparent 8px
          );
        pointer-events: none;
        mix-blend-mode: soft-light;
      }

      .anchor::before {
        border-width: 12px;
        box-shadow:
          inset 0 0 0 3px rgba(255, 237, 194, 0.45),
          inset 0 0 70px rgba(245, 177, 84, 0.21),
          0 0 48px rgba(238, 172, 75, 0.28);
      }

      .art-svg {
        position: absolute;
        inset: 0;
      }

      .art-svg .burst-lines line {
        stroke: rgba(255, 227, 173, 0.24);
        stroke-width: 2;
      }

      .art-svg .shards polygon {
        fill: rgba(253, 190, 120, 0.12);
        stroke: rgba(255, 223, 162, 0.24);
        stroke-width: 1.5;
      }

      .art-svg .stars circle {
        fill: rgba(255, 230, 187, 0.30);
      }

      .content {
        position: relative;
        z-index: 2;
        width: 100%;
        height: 100%;
        display: grid;
        grid-template-rows: auto auto 1fr auto auto;
        gap: 16px;
      }

      .issue {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--ink-soft);
        text-transform: uppercase;
        letter-spacing: 1.8px;
        font-size: 22px;
      }

      .issue-tag {
        padding: 8px 14px;
        border: 2px solid rgba(250, 216, 156, 0.52);
        border-radius: 999px;
        background: rgba(10, 8, 14, 0.42);
      }

      .spine {
        border: 3px solid rgba(255, 219, 161, 0.43);
        border-radius: 22px;
        background: linear-gradient(154deg, rgba(32, 24, 40, 0.78), rgba(11, 10, 15, 0.68));
        padding: 18px 20px 20px;
        display: grid;
        gap: 8px;
      }

      .anchor .spine {
        border-width: 5px;
        border-color: rgba(255, 227, 164, 0.68);
        padding: 22px 24px 24px;
      }

      .rankline {
        display: flex;
        align-items: baseline;
        gap: 14px;
      }

      .rank {
        margin: 0;
        font-size: 92px;
        font-weight: 900;
        color: var(--gold);
        line-height: 1;
        letter-spacing: 1px;
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.44);
      }

      .anchor .rank {
        font-size: 132px;
      }

      .title {
        margin: 0;
        font-size: 58px;
        line-height: 1.04;
      }

      .anchor .title {
        font-size: 78px;
      }

      .artist {
        margin: 0;
        font-size: 35px;
        color: #ffe9bc;
      }

      .anchor .artist {
        font-size: 44px;
      }

      .ambient {
        align-self: end;
        border: 2px solid rgba(246, 212, 153, 0.33);
        border-radius: 18px;
        background: rgba(12, 10, 14, 0.58);
        padding: 12px 14px;
      }

      .ambient ul {
        margin: 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 6px;
      }

      .ambient li {
        font-size: 24px;
        line-height: 1.25;
        color: #f8e8c9;
      }

      .stats {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .stat {
        border: 2px dashed rgba(253, 219, 159, 0.42);
        border-radius: 14px;
        background: rgba(9, 8, 12, 0.56);
        padding: 10px 12px;
      }

      .stat h2 {
        margin: 0;
        font-size: 18px;
        color: var(--ink-soft);
        letter-spacing: 1px;
        text-transform: uppercase;
      }

      .stat p {
        margin: 6px 0 0;
        font-size: 38px;
        color: #fff0ca;
      }

      .anchor .stat p {
        font-size: 44px;
      }
    </style>
  </head>
  <body>
    <article class="card${anchorClass}">
      ${illustrationSvg(record)}
      <section class="content">
        <header class="issue">
          <span class="issue-tag">Billboard Hot 100</span>
          <span>${TARGET_ISSUE_DATE}</span>
        </header>

        <section class="spine">
          <div class="rankline">
            <p class="rank">#${record.rank}</p>
            <h1 class="title">${escapeHtml(record.title)}</h1>
          </div>
          <p class="artist">${escapeHtml(record.artist)}</p>
        </section>

        <div></div>

        ${ambientBlock}

        <section class="stats">
          <article class="stat">
            <h2>Weeks on Chart</h2>
            <p>${record.weeks_on_chart}</p>
          </article>
          <article class="stat">
            <h2>Peak Position</h2>
            <p>${record.peak_position}</p>
          </article>
        </section>
      </section>
    </article>
  </body>
</html>`
}

function buildReviewPage() {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>Week 30 Illustrated Review</title>
    <style>
      html,
      body {
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

      .stack::-webkit-scrollbar {
        display: none;
      }
    </style>
  </head>
  <body>
    <main id="stack" class="stack" aria-label="Week 30 illustrated review"></main>
    <script>
      const container = document.getElementById('stack')
      for (let rank = 1; rank <= 40; rank += 1) {
        const label = String(rank).padStart(2, '0')
        const slide = document.createElement('section')
        slide.className = 'slide'

        const image = document.createElement('img')
        image.src = '../cards/1974/week-30-illustrated/week-30-rank-' + label + '.png'
        image.alt = 'Week 30 illustrated rank ' + label + ' card'
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
      const filename = `week-30-rank-${String(record.rank).padStart(2, '0')}.png`
      const outPath = path.join(OUTPUT_DIR, filename)
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

  const records = top40.map((row) => ({
    ...row,
    week_range: WEEK_RANGE,
    ambient_lines: buildAmbientLines(row, libraries),
  }))

  await renderCards(records)
  await fs.mkdir(path.dirname(REVIEW_PAGE_PATH), { recursive: true })
  await fs.writeFile(REVIEW_PAGE_PATH, buildReviewPage(), 'utf8')

  console.log(`[week-30-illustrated] rendered ${records.length} cards to ${OUTPUT_DIR}`)
  console.log(`[week-30-illustrated] review page: ${REVIEW_PAGE_PATH}`)
}

main().catch((error) => {
  console.error(`[week-30-illustrated][fatal] ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
})
