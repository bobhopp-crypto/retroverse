import type { PipelineContext, PipelineStage } from "../pipeline/types.js";

export function buildUploaderStages(_context: PipelineContext): PipelineStage[] {
  return [
    {
      name: "upload-r2",
      async execute(input, ctx) {
        ctx.diagnostics.info("TODO: push assets to R2");
        return input;
      }
    }
  ];
}
