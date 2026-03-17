import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT_DIR = path.resolve(__dirname, '..', '..')
const REGISTRY_PATH = path.join(ROOT_DIR, 'data', 'registry', 'DATA_REGISTRY.yaml')

let cachedRegistry = null

function minimalParseRegistry(content) {
  const datasets = {}
  let inDatasets = false
  let currentId = null

  for (const rawLine of content.split(/\r?\n/)) {
    const line = rawLine.replace(/\s+$/, '')
    if (!line || line.trimStart().startsWith('#')) continue

    if (line === 'datasets:') {
      inDatasets = true
      continue
    }

    if (!inDatasets) continue

    if (line.startsWith('  ') && !line.startsWith('    ') && line.endsWith(':')) {
      currentId = line.trim().slice(0, -1)
      datasets[currentId] = {}
      continue
    }

    if (currentId && line.startsWith('    ')) {
      const trimmed = line.trim()
      const separatorIndex = trimmed.indexOf(':')
      if (separatorIndex === -1) continue
      const key = trimmed.slice(0, separatorIndex)
      const value = trimmed.slice(separatorIndex + 1).trim().replace(/^['"]|['"]$/g, '')
      datasets[currentId][key] = value
    }
  }

  return { datasets }
}

export function loadRegistry() {
  if (cachedRegistry) return cachedRegistry
  if (!fs.existsSync(REGISTRY_PATH)) {
    cachedRegistry = { datasets: {} }
    return cachedRegistry
  }

  const content = fs.readFileSync(REGISTRY_PATH, 'utf8')
  cachedRegistry = minimalParseRegistry(content)
  return cachedRegistry
}

export function getDatasetPath(datasetId, fallback = null) {
  const datasets = loadRegistry().datasets ?? {}
  const pathValue = datasets?.[datasetId]?.path
  if (pathValue) return path.resolve(ROOT_DIR, pathValue)
  if (fallback == null) {
    throw new Error(`Dataset '${datasetId}' not found in ${REGISTRY_PATH}`)
  }
  return path.isAbsolute(fallback) ? fallback : path.resolve(ROOT_DIR, fallback)
}
