import pino from "pino";

export interface Diagnostics {
  debug(message: string, meta?: unknown): void;
  info(message: string, meta?: unknown): void;
  warn(message: string, meta?: unknown): void;
  error(message: string, meta?: unknown): void;
}

export function createDiagnostics(): Diagnostics {
  const logger = pino({
    level: process.env.PIPELINE_LOG_LEVEL ?? "info",
    transport: {
      target: "pino-pretty",
      options: { colorize: true }
    }
  });

  // TODO: add file transport and structured pipeline event logging.
  return {
    debug: (message, meta) => logger.debug(meta ?? {}, message),
    info: (message, meta) => logger.info(meta ?? {}, message),
    warn: (message, meta) => logger.warn(meta ?? {}, message),
    error: (message, meta) => logger.error(meta ?? {}, message)
  };
}
