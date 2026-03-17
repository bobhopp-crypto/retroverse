import express from "express";
import { registerPipelineRoutes } from "./routes/pipelineRoutes.js";

export function createServer() {
  const app = express();
  app.use(express.json());

  registerPipelineRoutes(app);

  return app;
}

// Allow manual start for local testing.
if (import.meta.url === `file://${process.argv[1]}`) {
  const app = createServer();
  const port = Number(process.env.TOOLS_SERVICE_PORT ?? 4040);
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`Tools service listening on http://localhost:${port}`);
  });
}
