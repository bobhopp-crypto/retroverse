import { defaultPipelineConfig, type PipelineConfig } from "./pipelineConfig.js";
import { readFile } from "node:fs/promises";
import path from "node:path";

const CONFIG_FILE = "pipeline.config.json";

export async function loadPipelineConfig(cwd: string = process.cwd()): Promise<PipelineConfig> {
  const candidate = path.join(cwd, CONFIG_FILE);

  try {
    const raw = await readFile(candidate, "utf-8");
    const parsed = JSON.parse(raw) as Partial<PipelineConfig>;
    // TODO: add schema validation before enabling writes.
    return { ...defaultPipelineConfig, ...parsed };
  } catch (error) {
    // TODO: surface validation/IO errors to diagnostics once logger is wired.
    return defaultPipelineConfig;
  }
}

export { CONFIG_FILE };
