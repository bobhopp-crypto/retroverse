import type { PipelineContext, PipelineStage } from "../pipeline/types.js";

export function buildParserStages(context: PipelineContext): PipelineStage[] {
  const stages: PipelineStage[] = [
    {
      name: "parse-database-xml",
      async execute(_input, ctx) {
        ctx.diagnostics.info("TODO: implement database.xml parser");
        return [];
      }
    },
    {
      name: "parse-playlists",
      async execute(_input, ctx) {
        ctx.diagnostics.info("TODO: implement playlist parser");
        return [];
      }
    }
  ];

  return stages;
}
