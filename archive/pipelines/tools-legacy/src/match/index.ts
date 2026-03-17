import type { PipelineContext, PipelineStage } from "../pipeline/types.js";

export function buildMatcherStages(_context: PipelineContext): PipelineStage[] {
  return [
    {
      name: "fuzzy-match",
      async execute(input, ctx) {
        ctx.diagnostics.info("TODO: apply fuzzy matching to normalized items");
        return input;
      }
    }
  ];
}
