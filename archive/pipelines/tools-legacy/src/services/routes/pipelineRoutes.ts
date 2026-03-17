import type { Express, Request, Response } from "express";
import { promises as fs } from "node:fs";
import path from "node:path";
import { createPipelineOrchestrator } from "../../pipeline/orchestrator.js";
import { loadPipelineConfig } from "../../config/index.js";
import { createDiagnostics } from "../../diagnostics/logger.js";
import { getThumbnailUrl } from "../../../../src/lib/media/thumbnail.js";

// TODO: replace in-memory state with persistent job tracking once inputs exist.
let lastRunStatus: "idle" | "running" | "completed" | "failed" = "idle";

const ARTIFACTS_ROOT = process.env.VIDEO_ARTIFACT_ROOT ?? path.resolve(process.cwd(), "..", "artifacts");
const OUTPUT_INDEX_PATH = process.env.VIDEO_INDEX_PATH ?? path.join(ARTIFACTS_ROOT, "output", "video-index.json");
const CANONICAL_DIR = process.env.VDJ_LIBRARY_DIR ?? path.join(ARTIFACTS_ROOT, "canonical");

type VdjVideo = {
  video_id?: string;
  file?: { path?: string | null };
  playback?: { duration_ms?: number | null; play_count?: number | null; last_played?: string | null };
  tags?: { title?: string | null; artist?: string | null; title_raw?: string | null; artist_raw?: string | null; year?: number | null };
  vdj?: { added_at?: string | null };
};

type VideoIndexEntry = {
  filePath?: string;
  filepath?: string;
  duration?: number | null;
  durationSeconds?: number | null;
  playlists?: string[];
  sources?: string[];
  title?: string | null;
  artist?: string | null;
  videoId?: string | null;
  year?: number | null;
  playCount?: number | null;
  addedAt?: string | null;
  lastPlayed?: string | null;
  thumbnail?: string | null;
  video_url?: string | null;
  thumbnail_url?: string | null;
  media_status?: "ok" | "missing";
  relative_media_path?: string | null;
  id?: string | null;
  play_count?: number | null;
  vdj_path?: string | null;
};

const normalizePath = (value?: string | null) => (value ? path.normalize(value) : null);

const VDJ_MEDIA_ROOT = path.normalize("/Users/bobhopp/Library/CloudStorage/Dropbox/VIDEO");

const toPosix = (p: string) => p.split(path.sep).join("/");

const deriveRelativeMediaPath = (vdjPath?: string | null) => {
  if (!vdjPath) return null;
  const normalized = path.normalize(vdjPath);
  const rootWithSep = VDJ_MEDIA_ROOT.endsWith(path.sep) ? VDJ_MEDIA_ROOT : `${VDJ_MEDIA_ROOT}${path.sep}`;
  if (!normalized.startsWith(rootWithSep)) return null;
  const relative = path.relative(VDJ_MEDIA_ROOT, normalized);
  if (relative.startsWith("..")) return null;
  return toPosix(relative);
};

const encodePath = (p: string) =>
  p
    .split("/")
    .map((segment) => encodeURIComponent(segment).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`))
    .join("/");

const buildVideoUrl = (base: string, relativePath: string) => `${base}/video/${encodePath(relativePath)}`;

const buildMediaUrls = (relativePath: string | null) => {
  const base = (process.env.R2_PUBLIC_BASE || "").replace(/\/+$/, "");
  if (!relativePath || !base) {
    return { video_url: null, thumbnail_url: null, media_status: "missing" as const };
  }

  const video_url = buildVideoUrl(base, relativePath);
  const thumbnail_url = getThumbnailUrl(video_url);

  return {
    video_url,
    thumbnail_url,
    media_status: "ok" as const,
  };
};

const readJson = async <T>(filePath: string): Promise<T | null> => {
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw) as T;
  } catch (error) {
    return null;
  }
};

const findLatestByPrefix = async (dir: string, prefix: string) => {
  const entries = await fs.readdir(dir).catch(() => []);
  const files = entries
    .filter((name) => name.startsWith(prefix) && name.endsWith(".json"))
    .map((name) => path.join(dir, name));

  let latest: { path: string; mtime: number } | null = null;
  for (const file of files) {
    const stats = await fs.stat(file).catch(() => null);
    if (!stats) continue;
    if (!latest || stats.mtimeMs > latest.mtime) {
      latest = { path: file, mtime: stats.mtimeMs };
    }
  }
  return latest;
};

const emptyVideoIndexResponse = (error?: unknown) => ({
  count: 0,
  source: {
    indexPath: null,
    indexMtime: null,
    vdjPath: null,
    vdjRunId: null,
    generated_at: null,
  },
  error: error instanceof Error ? error.message : error ? String(error) : undefined,
  items: [] as VideoIndexEntry[],
});

const buildVideoIndexResponse = async () => {
  try {
    const latestVdj = await findLatestByPrefix(CANONICAL_DIR, "vdj_library_");

    let vdjVideos: VdjVideo[] = [];
    let vdjMeta: any = null;
    if (latestVdj) {
      try {
        const raw = await fs.readFile(latestVdj.path, "utf-8");
        const parsed = JSON.parse(raw);
        vdjVideos = Array.isArray(parsed)
          ? parsed
          : Array.isArray((parsed as any).items)
            ? (parsed as any).items
            : Array.isArray((parsed as any).videos)
              ? (parsed as any).videos
              : [];
        vdjMeta = (parsed as any).meta ?? null;
        console.log(`[video-index] snapshot=${path.basename(latestVdj.path)} items=${vdjVideos.length}`);
      } catch (error) {
        console.error("Failed to parse VDJ snapshot", latestVdj.path, error);
      }
    }
    const indexArray = await readJson<VideoIndexEntry[]>(OUTPUT_INDEX_PATH);
    const indexMap = new Map<string, VideoIndexEntry>();
    if (Array.isArray(indexArray)) {
      for (const entry of indexArray) {
        const normalized = normalizePath(entry.filePath ?? entry.filepath);
        if (normalized) indexMap.set(normalized, entry);
      }
    }

    const items = vdjVideos.map((video) => {
      const rawPath = (video as any).vdj_path ?? video.file?.path ?? null;
      const normalizedPath = normalizePath(rawPath);
      const enrichment = normalizedPath ? indexMap.get(normalizedPath) : null;

      const baseTitle = video.tags?.title ?? video.tags?.title_raw ?? null;
      const baseArtist = video.tags?.artist ?? video.tags?.artist_raw ?? null;
      const durationSeconds = (video.playback?.duration_ms ? Math.round(video.playback.duration_ms / 1000) : null)
        ?? enrichment?.durationSeconds
        ?? enrichment?.duration
        ?? null;

      const relativeMediaPath = deriveRelativeMediaPath(rawPath ?? enrichment?.filePath ?? enrichment?.filepath);
      const media = buildMediaUrls(relativeMediaPath);

      const playlists = enrichment?.playlists ?? [];
      const sources = Array.from(new Set([...(enrichment?.sources ?? []), "vdj"].filter(Boolean))) as string[];

      return {
        id: video.video_id ?? enrichment?.videoId ?? normalizedPath ?? rawPath ?? enrichment?.filepath ?? null,
        filePath: rawPath ?? enrichment?.filePath ?? enrichment?.filepath,
        title: baseTitle || enrichment?.title || "Untitled",
        artist: baseArtist || enrichment?.artist || "Unknown",
        playlists,
        sources: sources.length ? sources : ["vdj"],
        videoId: video.video_id ?? enrichment?.videoId ?? normalizedPath ?? video.file?.path ?? enrichment?.filepath,
        durationSeconds,
        duration: durationSeconds ?? enrichment?.duration ?? null,
        year: video.tags?.year ?? enrichment?.year ?? null,
        playCount: video.playback?.play_count ?? enrichment?.playCount ?? null,
        play_count: video.playback?.play_count ?? enrichment?.playCount ?? null,
        addedAt: video.vdj?.added_at ?? enrichment?.addedAt ?? null,
        lastPlayed: video.playback?.last_played ?? enrichment?.lastPlayed ?? null,
        thumbnail: enrichment?.thumbnail ?? null,
        video_url: media.video_url,
        thumbnail_url: media.thumbnail_url,
        media_status: media.media_status,
        relative_media_path: relativeMediaPath,
        vdj_path: rawPath ?? null,
      };
    });

    console.log(`[video-index] returning items=${items.length} snapshot=${latestVdj ? path.basename(latestVdj.path) : "none"}`);

    const indexStat = await fs.stat(OUTPUT_INDEX_PATH).catch(() => null);

    return {
      count: items.length,
      source: {
        indexPath: indexStat ? OUTPUT_INDEX_PATH : null,
        indexMtime: indexStat?.mtimeMs ?? null,
        vdjPath: latestVdj?.path ?? null,
        vdjRunId: vdjMeta?.run_id ?? null,
        generated_at: vdjMeta?.generated_at ?? null,
      },
      items,
    };
  } catch (error) {
    return emptyVideoIndexResponse(error);
  }
};

export function registerPipelineRoutes(app: Express) {
  app.get(["/health", "/api/health"], (_req: Request, res: Response) => {
    res.json({ status: "ok", service: "retroverse-tools" });
  });

  app.get("/api/video-index", async (_req: Request, res: Response) => {
    const payload = await buildVideoIndexResponse();
    res.json(payload);
  });

  app.post("/pipeline/run", async (_req: Request, res: Response) => {
    const diagnostics = createDiagnostics();
    const config = await loadPipelineConfig();
    const orchestrator = createPipelineOrchestrator({ config, diagnostics });

    diagnostics.info("Received pipeline run request (stub).");
    lastRunStatus = "running";

    // TODO: background job execution with queue / worker.
    await orchestrator.prepare();
    lastRunStatus = "completed";

    res.json({ status: "accepted", message: "Pipeline stub executed. Awaiting data uploads." });
  });

  app.get("/pipeline/status", (_req: Request, res: Response) => {
    res.json({ status: lastRunStatus });
  });
}
