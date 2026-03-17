#!/usr/bin/env node

import fs from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'

const ROOT = process.cwd()
const WIDTH = 720
const HEIGHT = 1280

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function hashString(value) {
  let hash = 2166136261
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function parseArgs(argv) {
  const defaults = {
    cardType: 'ace',
    rankSymbol: 'A',
    songTitle: 'Annie\'s Song',
    artistName: 'John Denver',
    filmTitle: 'The Godfather Part II',
    tvTitle: 'Happy Days',
    headlineText: 'Watergate Aftershocks Reshape America',
    songBlockList: [
      '31. Whatever Gets You Thru The Night - John Lennon',
      '32. I Can Help - Billy Swan',
      '33. Kung Fu Fighting - Carl Douglas',
      '34. Cat\'s In The Cradle - Harry Chapin',
      '35. Angie Baby - Helen Reddy',
      '36. I Shot The Sheriff - Eric Clapton',
      '37. Rock Me Gently - Andy Kim',
      '38. Nothing From Nothing - Billy Preston',
      '39. Then Came You - Dionne Warwicke & The Spinners',
      '40. You Haven\'t Done Nothin\' - Stevie Wonder',
    ],
    motionLines: 'auto',
    output: path.join(ROOT, 'public', 'cards', '1974', 'playing-card-1974-720x1280.png'),
  }

  const out = { ...defaults }

  for (const arg of argv) {
    if (!arg.startsWith('--')) continue
    const [key, ...valueParts] = arg.slice(2).split('=')
    const value = valueParts.join('=')
    if (!value) continue

    if (key === 'card-type') out.cardType = value.trim().toLowerCase()
    if (key === 'rank-symbol') out.rankSymbol = value.trim()
    if (key === 'song-title') out.songTitle = value.trim()
    if (key === 'artist-name') out.artistName = value.trim()
    if (key === 'film-title') out.filmTitle = value.trim()
    if (key === 'tv-title') out.tvTitle = value.trim()
    if (key === 'headline-text') out.headlineText = value.trim()
    if (key === 'song-block-list') {
      out.songBlockList = value
        .split('|')
        .map((line) => line.trim())
        .filter(Boolean)
    }
    if (key === 'motion-lines') out.motionLines = value.trim().toLowerCase()
    if (key === 'output') out.output = path.resolve(ROOT, value.trim())
  }

  if (!['ace', 'number', 'king'].includes(out.cardType)) {
    throw new Error('`--card-type` must be one of: ace, number, king')
  }

  if (!['auto', 'on', 'off'].includes(out.motionLines)) {
    throw new Error('`--motion-lines` must be one of: auto, on, off')
  }

  return out
}

function motionLinesEnabled(config) {
  if (config.motionLines === 'on') return true
  if (config.motionLines === 'off') return false
  const seed = hashString(
    `${config.cardType}|${config.rankSymbol}|${config.songTitle}|${config.artistName}|${config.headlineText}`,
  )
  return (seed % 10) < 6
}

function buildMotionLines(enabled) {
  if (!enabled) return ''
  return `
    <div class="motion-lines" aria-hidden="true">
      <span style="top: 168px; left: 58px; width: 148px; transform: rotate(-15deg)"></span>
      <span style="top: 218px; right: 44px; width: 176px; transform: rotate(14deg)"></span>
      <span style="top: 878px; left: 64px; width: 166px; transform: rotate(-12deg)"></span>
      <span style="top: 934px; right: 58px; width: 152px; transform: rotate(17deg)"></span>
      <span style="top: 1030px; left: 272px; width: 200px; transform: rotate(-6deg)"></span>
    </div>
  `
}

function buildOrganicShapes() {
  return `
    <svg class="shape-layer" viewBox="0 0 720 1280" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <path d="M50 230 C10 120 130 30 270 80 C350 110 370 210 305 280 C240 350 100 350 50 230 Z" fill="#be5d2f"/>
      <path d="M458 122 C565 30 700 138 665 290 C648 368 546 440 458 372 C369 304 372 194 458 122 Z" fill="#d7a22f"/>
      <path d="M115 965 C47 846 138 740 270 744 C394 750 470 860 418 980 C370 1092 180 1080 115 965 Z" fill="#80935b"/>
      <path d="M470 852 C548 740 684 798 682 930 C680 1042 564 1128 446 1068 C340 1014 397 920 470 852 Z" fill="#5f7d96"/>
      <circle cx="336" cy="514" r="114" fill="#c46b50"/>
    </svg>
  `
}

function buildAceOrNumberBody(config) {
  const isAce = config.cardType === 'ace'
  const heroClass = isAce ? 'hero ace-hero' : 'hero number-hero'
  const burst = isAce
    ? `<div class="accent-burst" aria-hidden="true">
         <span></span><span></span><span></span><span></span>
       </div>`
    : ''

  return `
    <section class="top-index">${escapeHtml(config.rankSymbol)}</section>
    <main class="content">
      ${burst}
      <h1 class="${heroClass}">${escapeHtml(config.songTitle)}</h1>
      <p class="artist">${escapeHtml(config.artistName)}</p>

      <section class="meta-band">
        <div class="meta-item">
          <h2>Film Of The Year</h2>
          <p>${escapeHtml(config.filmTitle)}</p>
        </div>
        <div class="meta-item">
          <h2>Top TV Program</h2>
          <p>${escapeHtml(config.tvTitle)}</p>
        </div>
        <div class="meta-item">
          <h2>Cultural Headline</h2>
          <p>${escapeHtml(config.headlineText)}</p>
        </div>
      </section>
    </main>
  `
}

function buildKingBody(config) {
  const rows = config.songBlockList
    .map((line) => `<li>${escapeHtml(line)}</li>`)
    .join('')

  return `
    <section class="top-index">K</section>
    <main class="content king-content">
      <h1 class="king-title">1974 Year-End Songs (31-40)</h1>
      <section class="king-grid-wrap">
        <ol class="king-grid">${rows}</ol>
      </section>
    </main>
  `
}

function buildHtml(config) {
  const isKing = config.cardType === 'king'
  const motionLines = buildMotionLines(motionLinesEnabled(config))
  const body = isKing ? buildKingBody(config) : buildAceOrNumberBody(config)

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=720, initial-scale=1" />
    <title>1974 Playing Card</title>
    <style>
      :root {
        --burnt-orange: #be5d2f;
        --mustard: #d7a22f;
        --avocado: #80935b;
        --dusty-blue: #5f7d96;
        --faded-red: #c46b50;
        --cream-ink: #f3e5c7;
        --dark-ink: #211910;
      }

      * { box-sizing: border-box; }

      html,
      body {
        margin: 0;
        width: ${WIDTH}px;
        height: ${HEIGHT}px;
        overflow: hidden;
      }

      body {
        background: #1f160f;
      }

      .card {
        position: relative;
        width: ${WIDTH}px;
        height: ${HEIGHT}px;
        color: var(--dark-ink);
        background:
          radial-gradient(circle at 18% 12%, rgba(255, 225, 156, 0.26), transparent 38%),
          radial-gradient(circle at 85% 78%, rgba(255, 207, 122, 0.2), transparent 42%),
          linear-gradient(160deg, #e8cf9a 0%, #dbc28f 42%, #cfb07c 100%);
      }

      .shape-layer {
        position: absolute;
        inset: 0;
        opacity: 0.96;
      }

      .halftone {
        position: absolute;
        inset: 0;
        background-image: radial-gradient(rgba(37, 28, 19, 0.18) 0.95px, transparent 0.95px);
        background-size: 8px 8px;
        mix-blend-mode: multiply;
        opacity: 0.24;
      }

      .grain {
        position: absolute;
        inset: 0;
        background:
          repeating-linear-gradient(
            0deg,
            rgba(255, 255, 255, 0.02) 0,
            rgba(255, 255, 255, 0.02) 1px,
            transparent 1px,
            transparent 3px
          );
        opacity: 0.42;
      }

      .motion-lines {
        position: absolute;
        inset: 0;
      }

      .motion-lines span {
        position: absolute;
        height: 4px;
        border-radius: 999px;
        background: rgba(245, 231, 194, 0.66);
      }

      .frame {
        position: absolute;
        inset: 22px;
        border: 3px solid rgba(38, 26, 17, 0.64);
        border-radius: 22px;
      }

      .frame::after {
        content: '';
        position: absolute;
        inset: 8px;
        border: 2px solid rgba(246, 227, 183, 0.58);
        border-radius: 16px;
      }

      .top-index {
        position: absolute;
        top: 44px;
        left: 52px;
        z-index: 3;
        font-family: 'Marker Felt', 'Comic Sans MS', 'Trebuchet MS', sans-serif;
        font-size: 74px;
        line-height: 1;
        color: #f9f0d8;
        text-shadow: 0 3px 0 rgba(0, 0, 0, 0.32);
      }

      .content {
        position: relative;
        z-index: 3;
        height: 100%;
        padding: 146px 62px 58px;
        display: grid;
        grid-template-rows: auto auto 1fr;
      }

      .hero {
        margin: 0;
        font-family: 'Marker Felt', 'Comic Sans MS', 'Trebuchet MS', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        line-height: 0.95;
        color: #f7edd2;
        text-shadow:
          0 2px 0 rgba(34, 21, 14, 0.5),
          0 10px 24px rgba(34, 21, 14, 0.32);
      }

      .ace-hero {
        font-size: 88px;
      }

      .number-hero {
        font-size: 66px;
      }

      .artist {
        margin: 16px 0 0;
        font-family: 'Trebuchet MS', 'Gill Sans', sans-serif;
        font-size: 40px;
        letter-spacing: 0.8px;
        color: #f6e4bf;
        text-transform: uppercase;
      }

      .accent-burst {
        position: absolute;
        top: 128px;
        right: 62px;
        width: 112px;
        height: 112px;
        z-index: 2;
      }

      .accent-burst span {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 10px;
        height: 112px;
        border-radius: 999px;
        background: #ffefbf;
        transform-origin: center;
        opacity: 0.9;
      }

      .accent-burst span:nth-child(1) { transform: translate(-50%, -50%) rotate(0deg); }
      .accent-burst span:nth-child(2) { transform: translate(-50%, -50%) rotate(45deg); }
      .accent-burst span:nth-child(3) { transform: translate(-50%, -50%) rotate(90deg); }
      .accent-burst span:nth-child(4) { transform: translate(-50%, -50%) rotate(135deg); }

      .meta-band {
        align-self: end;
        display: grid;
        gap: 14px;
        padding: 16px;
        border-radius: 18px;
        background: rgba(34, 24, 15, 0.68);
        border: 2px solid rgba(245, 229, 191, 0.6);
      }

      .meta-item {
        padding-bottom: 8px;
        border-bottom: 1px dashed rgba(245, 229, 191, 0.5);
      }

      .meta-item:last-child {
        border-bottom: 0;
        padding-bottom: 0;
      }

      .meta-item h2 {
        margin: 0;
        font-family: 'Trebuchet MS', 'Gill Sans', sans-serif;
        font-size: 18px;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: #f2dca5;
      }

      .meta-item p {
        margin: 6px 0 0;
        font-family: 'Trebuchet MS', 'Gill Sans', sans-serif;
        font-size: 30px;
        line-height: 1.1;
        color: #fff5dc;
      }

      .king-content {
        display: grid;
        grid-template-rows: auto 1fr;
        gap: 20px;
      }

      .king-title {
        margin: 0;
        font-family: 'Marker Felt', 'Comic Sans MS', 'Trebuchet MS', sans-serif;
        font-size: 54px;
        text-transform: uppercase;
        line-height: 0.95;
        color: #f8efda;
        text-shadow: 0 3px 0 rgba(31, 20, 12, 0.46);
      }

      .king-grid-wrap {
        border-radius: 18px;
        background: rgba(33, 24, 16, 0.64);
        border: 2px solid rgba(246, 227, 183, 0.62);
        padding: 18px 18px 14px;
      }

      .king-grid {
        margin: 0;
        padding: 0;
        list-style: none;
        columns: 2;
        column-gap: 20px;
      }

      .king-grid li {
        break-inside: avoid;
        margin: 0 0 10px;
        font-family: 'Trebuchet MS', 'Gill Sans', sans-serif;
        font-size: 20px;
        line-height: 1.15;
        color: #fff5dc;
      }
    </style>
  </head>
  <body>
    <article class="card">
      ${buildOrganicShapes()}
      <div class="halftone" aria-hidden="true"></div>
      <div class="grain" aria-hidden="true"></div>
      ${motionLines}
      <div class="frame" aria-hidden="true"></div>
      ${body}
    </article>
  </body>
</html>`
}

async function render(config) {
  const outputDir = path.dirname(config.output)
  await fs.mkdir(outputDir, { recursive: true })

  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
  })

  try {
    await page.setContent(buildHtml(config), { waitUntil: 'networkidle' })
    await page.locator('.card').screenshot({ path: config.output, type: 'png' })
  } finally {
    await page.close()
    await browser.close()
  }
}

async function main() {
  const config = parseArgs(process.argv.slice(2))
  await render(config)
  console.log(`Rendered: ${config.output}`)
}

main().catch((error) => {
  console.error(`[render-1974-playing-card][fatal] ${error instanceof Error ? error.message : String(error)}`)
  process.exitCode = 1
})

