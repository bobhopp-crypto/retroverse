import type { PipelineContext, PipelineStage } from "../pipeline/types.js";

export function buildNormalizerStages(_context: PipelineContext): PipelineStage[] {
  return [
    {
      name: "normalize-records",
      async execute(input, ctx) {
        ctx.diagnostics.info("TODO: normalize parsed items");
        return input;
      }
    }
  ];
}
