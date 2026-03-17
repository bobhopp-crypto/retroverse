import type { PipelineContext, PipelineStage } from "../pipeline/types.js";

export function buildThumbnailStages(_context: PipelineContext): PipelineStage[] {
  return [
    {
      name: "generate-thumbnails",
      async execute(input, ctx) {
        ctx.diagnostics.info("TODO: generate thumbnails from media metadata");
        return input;
      }
    }
  ];
}
