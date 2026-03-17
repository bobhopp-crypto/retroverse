import { createPipelineOrchestrator } from "./pipeline/orchestrator.js";
import { loadPipelineConfig } from "./config/index.js";
import { createDiagnostics } from "./diagnostics/logger.js";

// Entry point for CLI or programmatic usage. Intentionally minimal.
async function main() {
  const diagnostics = createDiagnostics();
  const config = await loadPipelineConfig();
  const orchestrator = createPipelineOrchestrator({ config, diagnostics });

  // TODO: wire CLI flags/environment controls before running stages.
  await orchestrator.prepare();
  // TODO: call orchestrator.execute() once source files are available.
  diagnostics.info("Pipeline scaffold initialized. Waiting for input uploads.");
}

// Only execute when invoked directly.
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}

export { main };
