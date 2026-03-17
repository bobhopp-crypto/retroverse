import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT_DIR = path.resolve(__dirname, '..', '..')
const LINEAGE_SCRIPT = path.join(ROOT_DIR, 'pipelines', 'support-data', 'scripts', 'generate_data_lineage.py')
const SKIP_ENV = 'RETROVERSE_SKIP_LINEAGE'

export function runLineageGeneration() {
  if (process.env[SKIP_ENV]) return
  execFileSync('python3', [LINEAGE_SCRIPT], {
    cwd: ROOT_DIR,
    stdio: 'inherit',
  })
}

export async function runWithLineage(task) {
  const result = await task()
  runLineageGeneration()
  return result
}
