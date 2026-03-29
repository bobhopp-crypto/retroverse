import { copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const repoRoot = resolve(process.cwd())
const distDir = join(repoRoot, 'apps/web/dist')
const chartsSourceDir = join(repoRoot, 'apps/charts_app')
const chartsDestDir = join(distDir, 'charts')
const chartOverlaySource = join(repoRoot, 'apps/shared/chartOverlay.js')
const sharedDestDir = join(distDir, 'shared')
const chartOverlaySharedDest = join(sharedDestDir, 'chartOverlay.js')
const chartOverlayChartsDestDir = join(chartsDestDir, 'shared')
const chartOverlayChartsDest = join(chartOverlayChartsDestDir, 'chartOverlay.js')
const landingSource = join(repoRoot, 'apps/web/public/index.html')
const spaIndex = join(distDir, 'index.html')
const videoLibraryDir = join(distDir, 'video-library')
const videoLibraryIndex = join(videoLibraryDir, 'index.html')
const masterDataSource = join(repoRoot, 'data/master/retroverse_master.json')
const masterDataDestDir = join(distDir, 'data/master')
const masterDataDest = join(masterDataDestDir, 'retroverse_master.json')
const chartsBootstrapDest = join(chartsDestDir, 'bootstrap.json')
const CHARTS_BOOTSTRAP_YEAR = '1975'
const REQUIRED_CHARTS_SOURCE_FILES = ['index.html', 'app.js', 'styles.css']
const REQUIRED_CHARTS_OUTPUT_FILES = ['index.html', 'app.js', 'styles.css', 'shared/chartOverlay.js']

const normalizeChartDate = (value) => (typeof value === 'string' ? value.slice(0, 10) : '')

const songHistory = (song) => {
  if (Array.isArray(song?.chart_history)) return song.chart_history
  if (Array.isArray(song?.billboard?.history)) return song.billboard.history
  return []
}

const albumHistory = (album) => (Array.isArray(album?.chart_history) ? album.chart_history : [])

const filterEntriesForYear = (entries, year) =>
  entries.filter((entry) => normalizeChartDate(entry?.chart_date).slice(0, 4) === year)

const findLatestSongYear = (master) => {
  let latestYear = ''
  const songs = Array.isArray(master?.songs) ? master.songs : []
  for (let index = 0; index < songs.length; index += 1) {
    const history = songHistory(songs[index])
    for (let entryIndex = 0; entryIndex < history.length; entryIndex += 1) {
      const year = normalizeChartDate(history[entryIndex]?.chart_date).slice(0, 4)
      if (year && year > latestYear) latestYear = year
    }
  }
  return latestYear
}

const resolveBootstrapYear = (master) => {
  const songs = Array.isArray(master?.songs) ? master.songs : []
  for (let index = 0; index < songs.length; index += 1) {
    const history = songHistory(songs[index])
    for (let entryIndex = 0; entryIndex < history.length; entryIndex += 1) {
      const year = normalizeChartDate(history[entryIndex]?.chart_date).slice(0, 4)
      if (year === CHARTS_BOOTSTRAP_YEAR) {
        return CHARTS_BOOTSTRAP_YEAR
      }
    }
  }
  return findLatestSongYear(master)
}

const cloneSongForBootstrap = (song, year) => {
  if (!song || typeof song !== 'object') return null

  const songChartHistory = Array.isArray(song.chart_history) ? filterEntriesForYear(song.chart_history, year) : null
  const billboardHistory =
    song?.billboard && Array.isArray(song.billboard.history) ? filterEntriesForYear(song.billboard.history, year) : null
  const hasSongHistory = Array.isArray(songChartHistory) && songChartHistory.length > 0
  const hasBillboardHistory = Array.isArray(billboardHistory) && billboardHistory.length > 0
  if (!hasSongHistory && !hasBillboardHistory) return null

  const cloned = { ...song }
  if (songChartHistory) {
    cloned.chart_history = songChartHistory
  }
  if (billboardHistory) {
    cloned.billboard = { ...song.billboard, history: billboardHistory }
  }
  return cloned
}

const cloneAlbumForBootstrap = (album, year) => {
  if (!album || typeof album !== 'object' || !Array.isArray(album.chart_history)) return null
  const filtered = filterEntriesForYear(album.chart_history, year)
  if (!filtered.length) return null
  return { ...album, chart_history: filtered }
}

const createChartsBootstrap = (master) => {
  const bootstrapYear = resolveBootstrapYear(master)
  if (!bootstrapYear) {
    return {
      meta: { ...(master?.meta || {}), bootstrap_year: '' },
      stats: master?.stats || {},
      songs: [],
      albums: [],
      videos: [],
      movies: [],
      tv: [],
    }
  }

  const songs = []
  const matchedSongIds = new Set()
  const sourceSongs = Array.isArray(master?.songs) ? master.songs : []
  for (let index = 0; index < sourceSongs.length; index += 1) {
    const clonedSong = cloneSongForBootstrap(sourceSongs[index], bootstrapYear)
    if (!clonedSong) continue
    songs.push(clonedSong)
    if (clonedSong.retroverse_id) matchedSongIds.add(clonedSong.retroverse_id)
  }

  const albums = []
  const sourceAlbums = Array.isArray(master?.albums) ? master.albums : []
  for (let index = 0; index < sourceAlbums.length; index += 1) {
    const clonedAlbum = cloneAlbumForBootstrap(sourceAlbums[index], bootstrapYear)
    if (clonedAlbum) albums.push(clonedAlbum)
  }

  const videos = (Array.isArray(master?.videos) ? master.videos : []).filter((video) => {
    const songId = video?.matched_song_id || video?.matched_song?.retroverse_id
    return matchedSongIds.has(songId)
  })

  return {
    meta: {
      ...(master?.meta || {}),
      bootstrap_year: bootstrapYear,
    },
    stats: master?.stats || {},
    songs,
    albums,
    videos,
    movies: [],
    tv: [],
  }
}

const requiredPaths = [
  { path: distDir, label: 'web dist directory' },
  { path: chartsSourceDir, label: 'charts static export' },
  { path: chartOverlaySource, label: 'charts overlay module' },
  { path: landingSource, label: 'landing page source' },
  { path: spaIndex, label: 'vite index output' },
  { path: masterDataSource, label: 'master charts dataset' },
]

for (const { path, label } of requiredPaths) {
  if (!existsSync(path)) {
    throw new Error(`Missing ${label}: ${path}`)
  }
}

for (const relativePath of REQUIRED_CHARTS_SOURCE_FILES) {
  const absolutePath = join(chartsSourceDir, relativePath)
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing required charts source file: ${absolutePath}`)
  }
}

mkdirSync(videoLibraryDir, { recursive: true })
copyFileSync(spaIndex, videoLibraryIndex)

rmSync(chartsDestDir, { recursive: true, force: true })
cpSync(chartsSourceDir, chartsDestDir, {
  recursive: true,
  force: true,
  errorOnExist: false,
  dereference: true,
})
mkdirSync(sharedDestDir, { recursive: true })
copyFileSync(chartOverlaySource, chartOverlaySharedDest)
mkdirSync(chartOverlayChartsDestDir, { recursive: true })
copyFileSync(chartOverlaySource, chartOverlayChartsDest)

mkdirSync(masterDataDestDir, { recursive: true })
copyFileSync(masterDataSource, masterDataDest)

const masterData = JSON.parse(readFileSync(masterDataSource, 'utf8'))
const chartsBootstrap = createChartsBootstrap(masterData)
writeFileSync(chartsBootstrapDest, JSON.stringify(chartsBootstrap))

for (const relativePath of REQUIRED_CHARTS_OUTPUT_FILES) {
  const absolutePath = join(chartsDestDir, relativePath)
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing required charts output file: ${absolutePath}`)
  }
}

copyFileSync(landingSource, spaIndex)

console.log('[prepare_public_deploy] Added /video-library entrypoint')
console.log('[prepare_public_deploy] Copied static charts app to /charts')
console.log('[prepare_public_deploy] Copied shared chartOverlay.js to /shared and /charts/shared')
console.log(
  `[prepare_public_deploy] Generated charts/bootstrap.json (${chartsBootstrap.meta.bootstrap_year || 'no-year'})`
)
console.log('[prepare_public_deploy] Copied master dataset for charts app')
console.log('[prepare_public_deploy] Published landing page at /')
