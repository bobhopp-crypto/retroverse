export type DataSource = {
  name: string;
  type: "database-xml" | "playlist-m3u" | "metadata-json" | "unknown";
  path: string;
};

export interface StorageTargets {
  thumbnailsDir: string;
  normalizedDir: string;
  diagnosticsDir: string;
  tempDir: string;
}

export interface R2Config {
  bucket: string;
  accountId: string;
  accessKeyId: string;
  secretAccessKey: string;
  region?: string;
  endpoint?: string;
}

export interface PipelineConfig {
  sources: DataSource[];
  r2?: R2Config;
  storage: StorageTargets;
  fuzzyMatch: {
    threshold: number;
    strategy: "levenshtein" | "jaro-winkler" | "custom";
  };
  thumbnail: {
    width: number;
    height: number;
    format: "png" | "jpeg" | "webp";
  };
  diagnostics: {
    level: "debug" | "info" | "warn" | "error";
  };
}

export const defaultPipelineConfig: PipelineConfig = {
  sources: [],
  r2: undefined,
  storage: {
    thumbnailsDir: "dist/thumbnails",
    normalizedDir: "dist/normalized",
    diagnosticsDir: "dist/diagnostics",
    tempDir: "dist/tmp"
  },
  fuzzyMatch: {
    threshold: 0.85,
    strategy: "levenshtein"
  },
  thumbnail: {
    width: 640,
    height: 360,
    format: "png"
  },
  diagnostics: {
    level: "info"
  }
};
