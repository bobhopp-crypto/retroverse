/**
 * Builds data/master/retroverse_master.json from read-only sources.
 * Does not modify raw or derived inputs.
 */
import Database from "better-sqlite3";
import dotenv from "dotenv";
import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, relative } from "node:path";
import Fuse from "fuse.js";

dotenv.config();

const REPO_ROOT = join(import.meta.dirname, "..");
const OUT_PATH = join(REPO_ROOT, "data/master/retroverse_master.json");
const BILLBOARD_ARTIST_CORRECTIONS_PATH = join(
  REPO_ROOT,
  "data/registry/billboard_artist_name_corrections.json",
);

const R2_BASE_URL = process.env.R2_BASE_URL || "";

if (!R2_BASE_URL) {
  throw new Error("R2_BASE_URL is not set");
}

function deriveCanonicalMediaPaths(filePath: string | null): {
  relative_path: string | null;
  video_url: string | null;
  thumbnail_url: string | null;
} {
  if (!filePath) {
    return {
      relative_path: null,
      video_url: null,
      thumbnail_url: null,
    };
  }

  const normalized = filePath
    .replace(/%20/g, " ")
    .replace(/\\/g, "/")
    .trim();

  const roots = [
    "/Users/bobhopp/DJ MEDIA/VIDEO/",
    "/Users/bobhopp/DJ MEDIA/VIDEO VAULT/",
    "/Users/bobhopp/Library/CloudStorage/Dropbox/VIDEO/",
    "/Volumes/DJ MAIN/DJ MEDIA/VIDEO/",
  ];

  let relativePath: string | null = null;

  for (const root of roots) {
    if (normalized.startsWith(root)) {
      relativePath = normalized.slice(root.length);
      break;
    }
  }

  if (!relativePath) {
    const idx = normalized.indexOf("/VIDEO/");
    if (idx !== -1) {
      relativePath = normalized.slice(idx + 7);
    }
  }

  if (!relativePath) {
    const idx = normalized.indexOf("/VIDEO VAULT/");
    if (idx !== -1) {
      relativePath = normalized.slice(idx + 13);
    }
  }

  if (!relativePath) {
    console.warn("FAILED PATH NORMALIZATION:", filePath);
    return {
      relative_path: null,
      video_url: null,
      thumbnail_url: null,
    };
  }

  relativePath = relativePath.replace(/^\/+/, "");

  const encoded = relativePath
    .split("/")
    .map(encodeURIComponent)
    .join("/");

  return {
    relative_path: relativePath,
    video_url: `${R2_BASE_URL}/video/${encoded}`,
    thumbnail_url: `${R2_BASE_URL}/video/${encoded.replace(/\.[^/.]+$/, ".jpg")}`,
  };
}

function norm(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Title matching: punctuation, underscores/dashes, parentheticals; then compare / includes. */
function normalizeTitle(s: string): string {
  return (s || "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\([^)]*\)/g, " ")
    .replace(/[_-]/g, " ")
    .replace(/[^\w\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Compare pre-normalized titles (equality or substring overlap). */
function titlesCompatible(aNorm: string, bNorm: string): boolean {
  if (aNorm === bNorm) return true;
  if (!aNorm.length || !bNorm.length) return false;
  return bNorm.includes(aNorm) || aNorm.includes(bNorm);
}

function artistTokens(s: string): string[] {
  return norm(s)
    .replace(/[^\w\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function artistSimilarityScore(a: string, b: string): number {
  const aTokens = artistTokens(a);
  const bTokens = artistTokens(b);
  if (!aTokens.length || !bTokens.length) return 0;

  const aSet = new Set(aTokens);
  const bSet = new Set(bTokens);
  let overlap = 0;
  for (const token of aSet) {
    if (bSet.has(token)) overlap++;
  }

  const tokenScore = overlap / Math.max(aSet.size, bSet.size);
  const aCompact = aTokens.join("");
  const bCompact = bTokens.join("");
  const prefixScore =
    aCompact.slice(0, 4) === bCompact.slice(0, 4) && aCompact.length >= 4 && bCompact.length >= 4
      ? 0.2
      : 0;
  const containsScore =
    aCompact.includes(bCompact) || bCompact.includes(aCompact)
      ? 0.2
      : 0;

  return Math.min(1, tokenScore + prefixScore + containsScore);
}

function titleMatchScore(songTitleNorm: string, videoTitleNorm: string): number {
  if (!songTitleNorm.length || !videoTitleNorm.length) return 0;
  if (songTitleNorm === videoTitleNorm) return 3;
  if (
    songTitleNorm.length >= 5 &&
    (videoTitleNorm.startsWith(songTitleNorm) || videoTitleNorm.endsWith(songTitleNorm))
  ) {
    return 2;
  }
  if (
    songTitleNorm.length >= 5 &&
    (videoTitleNorm.includes(songTitleNorm) || songTitleNorm.includes(videoTitleNorm))
  ) {
    return 1;
  }
  return 0;
}

/** Registry keys: lowercase + trim (per data/registry/artist_aliases.json). */
function aliasKey(s: string): string {
  return s.toLowerCase().trim();
}

function buildAliasMap(
  entries: Array<{ canonical: string; aliases?: string[] }>,
): Map<string, string> {
  const m = new Map<string, string>();
  for (const e of entries) {
    const can = String(e.canonical ?? "").trim();
    if (!can) continue;
    const ck = aliasKey(can);
    if (!m.has(ck)) m.set(ck, can);
    for (const a of e.aliases ?? []) {
      const al = String(a).trim();
      if (!al) continue;
      const ak = aliasKey(al);
      if (!m.has(ak)) m.set(ak, can);
    }
  }
  return m;
}

function resolveCanonical(artist: string, aliasMap: Map<string, string>): string {
  const k = aliasKey(artist);
  const v = aliasMap.get(k);
  return v !== undefined ? v : artist;
}

function retroverseSongId(title: string, artist: string, aliasMap: Map<string, string>): string {
  const a = resolveCanonical(artist, aliasMap);
  return createHash("sha256")
    .update(`${norm(a)}\t${norm(title)}`)
    .digest("hex")
    .slice(0, 32);
}

function retroverseAlbumId(artist: string, album: string, aliasMap: Map<string, string>): string {
  const a = resolveCanonical(artist, aliasMap);
  return createHash("sha256")
    .update(`${norm(a)}\t${norm(album)}`)
    .digest("hex")
    .slice(0, 32);
}

function findLatestFile(dir: string, pattern: RegExp): string | null {
  if (!existsSync(dir)) return null;
  const hits = readdirSync(dir)
    .filter((f) => pattern.test(f))
    .map((f) => ({ f, t: statSync(join(dir, f)).mtimeMs }))
    .sort((a, b) => b.t - a.t);
  return hits[0] ? join(dir, hits[0].f) : null;
}

/** Newest `vdj_library_run_<digits>.json` by mtime (ignores e.g. decision_demo). */
function findLatestVdjLibraryRunPath(canonicalDir: string): string | null {
  if (!existsSync(canonicalDir)) return null;
  const vdjFiles = readdirSync(canonicalDir)
    .filter((f) => /^vdj_library_run_\d+\.json$/.test(f))
    .map((f) => {
      const path = join(canonicalDir, f);
      return { path, mtime: statSync(path).mtimeMs };
    })
    .sort((a, b) => b.mtime - a.mtime);
  if (!vdjFiles.length) return null;
  const latestVdjFile = vdjFiles[0].path;
  console.error(`[build_master_dataset] Using VDJ file: ${basename(latestVdjFile)}`);
  return latestVdjFile;
}

type BillboardSong = {
  chart_song_id: string;
  artist: string;
  title: string;
  source_type?: string;
  chart_appearances?: number;
  peak_position?: number;
  first_chart_week?: string;
  last_chart_week?: string;
  first_chart_year?: number;
  last_chart_year?: number;
};

type IndexedBillboardSong = BillboardSong & {
  artist_canonical: string;
  retroverse_id: string;
};

type ChartHistoryPoint = {
  chart_date: string;
  rank: number;
  last_week: number | null;
  peak: number | null;
  weeks_on_chart: number | null;
};

type VdjVideo = {
  video_id: string;
  file?: { path?: string; filename?: string; extension?: string };
  album?: string | null;
  year?: number | null;
  genre?: string | null;
  bpm?: number | null;
  musical_key?: string | null;
  metadata?: Record<string, unknown>;
  tags?: Record<string, unknown>;
  playback?: Record<string, unknown>;
  vdj?: Record<string, unknown>;
};

type YearBlock = {
  year: number;
  top_40?: Array<{
    rv_rank?: number;
    title?: string;
    artist?: string;
    peak_rank?: number;
    weeks_on_chart?: number;
    weeks_in_top_10?: number;
    weeks_in_top_40?: number;
  }>;
};

type MasterSong = {
  retroverse_id: string;
  title: string;
  artist: string;
  artist_canonical: string;
  title_normalized: string;
  artist_normalized: string;
  year: number | null;
  library_year: number | null;
  song_year: number | null;
  year_context: {
    song: number | null;
    library: number | null;
  };
  sources: Array<Record<string, unknown>>;
  billboard: Record<string, unknown> | null;
  chart_history: ChartHistoryPoint[];
  year_master: Array<Record<string, unknown>>;
  vdj_videos: Array<Record<string, unknown>>;
  play_count_total: number;
  album: Record<string, unknown> | null;
  acoustic_features: Record<string, unknown> | null;
};

type MasterAlbum = {
  retroverse_album_id: string;
  album_title: string;
  artist: string;
  artist_canonical: string;
  chart_date: string | null;
  chart_rank: string | null;
  chart_history: ChartHistoryPoint[];
  length: number | null;
  track_length: number | null;
  sources: Array<Record<string, unknown>>;
  acoustic_features: Record<string, unknown> | null;
};

type MasterVideo = {
  video_id: string;
  file_path: string | null;
  relative_path: string | null;
  video_url: string | null;
  thumbnail_url: string | null;
  filename: string | null;
  extension: string | null;
  artist: string | null;
  artist_canonical: string | null;
  title: string | null;
  title_normalized: string;
  album: string | null;
  year: number | null;
  library_year: number | null;
  song_year: number | null;
  year_context: {
    library: number | null;
    song: number | null;
  };
  genre: string | null;
  duration_ms: number | null;
  play_count: number | null;
  last_played: number | null;
  bpm: number | null;
  musical_key: string | null;
  matched_song_id: string | null;
  sources: Array<Record<string, unknown>>;
  matched_song: Record<string, unknown> | null;
};

function loadJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function loadBillboardArtistCorrections(path: string): Map<string, string> {
  if (!existsSync(path)) return new Map<string, string>();
  const parsed = loadJson<Record<string, unknown>>(path);
  const out = new Map<string, string>();
  for (const [from, to] of Object.entries(parsed)) {
    if (typeof from !== "string" || typeof to !== "string") continue;
    const fromKey = from.trim();
    const toValue = to.trim();
    if (!fromKey || !toValue) continue;
    out.set(fromKey, toValue);
  }
  return out;
}

function applyBillboardArtistCorrection(artist: string, corrections: Map<string, string>): string {
  const trimmed = String(artist ?? "").trim();
  if (!trimmed) return "";
  return corrections.get(trimmed) ?? trimmed;
}

function isSequentialChartWeek(prevDate: string | null, nextDate: string | null): boolean {
  if (!prevDate || !nextDate) return false;
  const prevMs = Date.parse(`${prevDate}T00:00:00Z`);
  const nextMs = Date.parse(`${nextDate}T00:00:00Z`);
  if (!Number.isFinite(prevMs) || !Number.isFinite(nextMs)) return false;
  return nextMs - prevMs === 7 * 24 * 60 * 60 * 1000;
}

/** Drop multi‑MB provenance trees; keep fields needed for search and IDs. */
function slimMovieRecord(r: Record<string, unknown>): Record<string, unknown> {
  return {
    title: r.title,
    original_title: r.original_title,
    year: r.year,
    release_date: r.release_date,
    medium: r.medium,
    genres: r.genres,
    runtime_minutes: r.runtime_minutes,
    country: r.country,
    language: r.language,
    director: r.director,
    principal_cast: r.principal_cast,
    studio: r.studio,
    box_office_domestic: r.box_office_domestic,
    box_office_worldwide: r.box_office_worldwide,
    imdb_rating: r.imdb_rating,
    imdb_votes: r.imdb_votes,
    critic_scores: r.critic_scores,
    awards_summary: r.awards_summary,
    popularity_signals: r.popularity_signals,
    source_ids: r.source_ids,
  };
}

function slimTvRecord(r: Record<string, unknown>): Record<string, unknown> {
  return {
    title: r.title,
    year: r.year,
    premiere_date: r.premiere_date,
    end_date: r.end_date,
    medium: r.medium,
    genres: r.genres,
    type: r.type,
    network: r.network,
    seasons: r.seasons,
    episodes: r.episodes,
    principal_cast: r.principal_cast,
    popularity_signals: r.popularity_signals,
    source_ids: r.source_ids,
  };
}

function main(): void {
  const errors: string[] = [];
  const canonicalDir = join(REPO_ROOT, "data/derived/media-index/canonical");
  const billboardPath = findLatestFile(canonicalDir, /^billboard_run_\d+\.json$/);
  const vdjPath = findLatestVdjLibraryRunPath(canonicalDir);
  const yearMasterPath = join(
    REPO_ROOT,
    "data/derived/year-masters/retroverse_year_master_1958_2024.json",
  );
  const moviesPath = join(
    REPO_ROOT,
    "data/raw/screen-culture/screen-culture/warehouse/movies_master.json",
  );
  const tvPath = join(
    REPO_ROOT,
    "data/raw/screen-culture/screen-culture/warehouse/television_master.json",
  );
  const bbHot100Path = join(REPO_ROOT, "data/raw/charts/billboard-hot-100.db");
  const bb200Path = join(REPO_ROOT, "data/raw/charts/billboard-200-albums-charts.db");
  const aliasesPath = join(REPO_ROOT, "data/registry/artist_aliases.json");

  if (!billboardPath) errors.push("Missing data/derived/media-index/canonical/billboard_run_*.json");
  if (!vdjPath) errors.push("Missing data/derived/media-index/canonical/vdj_library_run_*.json");
  if (!existsSync(yearMasterPath)) errors.push("Missing retroverse_year_master_1958_2024.json");
  if (!existsSync(moviesPath)) errors.push("Missing movies_master.json");
  if (!existsSync(tvPath)) errors.push("Missing television_master.json");
  if (!existsSync(bbHot100Path)) errors.push("Missing billboard-hot-100.db");
  if (!existsSync(bb200Path)) errors.push("Missing billboard-200-albums-charts.db");
  if (errors.length) {
    throw new Error(errors.join("\n"));
  }

  if (!existsSync(aliasesPath)) {
    mkdirSync(dirname(aliasesPath), { recursive: true });
    writeFileSync(
      aliasesPath,
      `[
  {
    "canonical": "Mouth & McNeal",
    "aliases": ["Mouth"]
  }
]
`,
      "utf8",
    );
  }
  const aliasEntries = loadJson<Array<{ canonical: string; aliases?: string[] }>>(aliasesPath);
  const aliasMap = buildAliasMap(aliasEntries);
  console.error(`[build_master_dataset] artist alias lookup keys: ${aliasMap.size}`);
  const artistCorrections = loadBillboardArtistCorrections(BILLBOARD_ARTIST_CORRECTIONS_PATH);
  console.error(`[build_master_dataset] billboard artist corrections: ${artistCorrections.size}`);

  console.error("[build_master_dataset] loading JSON sources…");
  const billboardDoc = loadJson<{
    meta?: Record<string, unknown>;
    songs: BillboardSong[];
  }>(billboardPath!);
  const billboardSongs: IndexedBillboardSong[] = (billboardDoc.songs ?? []).map((s) => {
    const correctedArtist = applyBillboardArtistCorrection(s.artist, artistCorrections);
    const artist_canonical = resolveCanonical(correctedArtist, aliasMap);
    return {
      ...s,
      artist: correctedArtist,
      artist_canonical,
      retroverse_id: retroverseSongId(s.title, artist_canonical, aliasMap),
    };
  });

  const vdjDoc = loadJson<{
    meta?: Record<string, unknown>;
    videos?: VdjVideo[];
  }>(vdjPath!);
  const vdjVideos = vdjDoc.videos ?? [];
  const vdjRunId =
    (vdjDoc.meta as { run_id?: string } | undefined)?.run_id ??
    vdjPath!.match(/run_(\d+)/)?.[1] ??
    null;

  const yearMasterDoc = loadJson<Record<string, YearBlock>>(yearMasterPath);

  console.error("[build_master_dataset] Fuse buckets (Hot 100 by artist prefix)…");
  const fuseOpts = {
    keys: [
      { name: "title", weight: 0.45 },
      { name: "artist_canonical", weight: 0.45 },
      { name: "_q", weight: 0.1 },
    ],
    threshold: 0.42,
    ignoreLocation: true,
    includeScore: true,
  } as const;
  const withQ = (s: IndexedBillboardSong) => {
    return { ...s, _q: `${s.artist_canonical} ${s.title}` };
  };
  function artistPrefix2(a: string): string {
    const n = norm(a);
    if (n.length >= 2) return n.slice(0, 2);
    if (n.length === 1) return `${n}?`;
    return "??";
  }
  const byArtistPrefix2 = new Map<string, IndexedBillboardSong[]>();
  for (const s of billboardSongs) {
    const p = artistPrefix2(s.artist_canonical);
    if (!byArtistPrefix2.has(p)) byArtistPrefix2.set(p, []);
    byArtistPrefix2.get(p)!.push(s);
  }
  const fuseByArtistPrefix = new Map<
    string,
    Fuse<IndexedBillboardSong & { _q: string }>
  >();
  for (const [p, songs] of byArtistPrefix2) {
    fuseByArtistPrefix.set(p, new Fuse(songs.map(withQ), fuseOpts));
  }

  const songById = new Map<string, MasterSong>();

  for (const s of billboardSongs) {
    const artist_canonical = s.artist_canonical;
    const id = s.retroverse_id;
    const songTitleNorm = normalizeTitle(s.title);
    const ms: MasterSong = {
      retroverse_id: id,
      title: s.title,
      artist: s.artist,
      artist_canonical,
      title_normalized: songTitleNorm,
      artist_normalized: norm(artist_canonical),
      year: s.first_chart_year ?? null,
      library_year: null,
      song_year: s.first_chart_year ?? null,
      year_context: {
        song: s.first_chart_year ?? null,
        library: null,
      },
      sources: [
        {
          source_system: "billboard_hot100_export",
          source_path: relative(REPO_ROOT, billboardPath!),
          source_id: s.chart_song_id,
        },
      ],
      billboard: {
        chart_song_id: s.chart_song_id,
        chart_appearances: s.chart_appearances ?? null,
        peak_position: s.peak_position ?? null,
        first_chart_week: s.first_chart_week ?? null,
        last_chart_week: s.last_chart_week ?? null,
        first_chart_year: s.first_chart_year ?? null,
        last_chart_year: s.last_chart_year ?? null,
        source_type: s.source_type ?? null,
      },
      chart_history: [],
      year_master: [],
      vdj_videos: [],
      play_count_total: 0,
      album: null,
      acoustic_features: null,
    };
    songById.set(id, ms);
  }

  for (const yk of Object.keys(yearMasterDoc)) {
    const block = yearMasterDoc[yk];
    if (!block?.top_40) continue;
    for (const row of block.top_40) {
      if (!row.title || !row.artist) continue;
      const correctedArtist = applyBillboardArtistCorrection(row.artist, artistCorrections);
      const artist_canonical = resolveCanonical(correctedArtist, aliasMap);
      const id = retroverseSongId(row.title, correctedArtist, aliasMap);
      const ym = {
        year: block.year,
        rv_rank: row.rv_rank ?? null,
        peak_rank: row.peak_rank ?? null,
        weeks_on_chart: row.weeks_on_chart ?? null,
        weeks_in_top_10: row.weeks_in_top_10 ?? null,
        weeks_in_top_40: row.weeks_in_top_40 ?? null,
      };
      const existing = songById.get(id);
      if (existing) {
        existing.year_master.push(ym);
        existing.sources.push({
          source_system: "year_master",
          source_path: relative(REPO_ROOT, yearMasterPath),
          source_record_ref: `${block.year}`,
        });
      } else {
        songById.set(id, {
          retroverse_id: id,
          title: row.title,
          artist: correctedArtist,
          artist_canonical,
          title_normalized: normalizeTitle(row.title),
          artist_normalized: norm(artist_canonical),
          year: null,
          library_year: null,
          song_year: null,
          year_context: {
            song: null,
            library: null,
          },
          sources: [
            {
              source_system: "year_master",
              source_path: relative(REPO_ROOT, yearMasterPath),
            },
          ],
          billboard: null,
          chart_history: [],
          year_master: [ym],
          vdj_videos: [],
          play_count_total: 0,
          album: null,
          acoustic_features: null,
        });
      }
    }
  }

  const artistSet = new Set<string>();
  for (const s of songById.values()) {
    artistSet.add(s.artist_normalized);
  }

  console.error("[build_master_dataset] loading Billboard weekly song history (SQLite)…");
  const hot100Db = new Database(bbHot100Path, { readonly: true, fileMustExist: true });
  type Hot100HistoryRow = {
    chart_date: string;
    rank: number;
    last_week: number | null;
    peak: number | null;
    weeks_on_chart: number | null;
    title: string;
    artist: string;
  };
  for (const row of hot100Db.prepare(
    `
      SELECT
        e.issue_date AS chart_date,
        ee.rank AS rank,
        ee.last_week AS last_week,
        ee.peak_pos AS peak,
        ee.weeks_on_chart AS weeks_on_chart,
        w.title_display AS title,
        p.name_display AS artist
      FROM event_entry ee
      JOIN event e ON e.event_id = ee.event_id
      JOIN work w ON w.work_id = ee.work_id
      JOIN person p ON p.person_id = w.primary_person_id
      ORDER BY e.issue_date ASC, ee.rank ASC
    `,
  ).iterate() as IterableIterator<Hot100HistoryRow>) {
    const correctedArtist = applyBillboardArtistCorrection(row.artist, artistCorrections);
    const sid = retroverseSongId(row.title, correctedArtist, aliasMap);
    const song = songById.get(sid);
    if (!song) continue;
    song.chart_history.push({
      chart_date: row.chart_date,
      rank: row.rank,
      last_week: row.last_week ?? null,
      peak: row.peak ?? null,
      weeks_on_chart: row.weeks_on_chart ?? null,
    });
  }
  hot100Db.close();

  console.error("[build_master_dataset] scanning Billboard 200 + acoustic_features (SQLite)…");
  const db = new Database(bb200Path, { readonly: true });
  type AlbumRow = {
    id: number;
    date: string | null;
    artist: string | null;
    album: string | null;
    rank: string | null;
    length: number | null;
    track_length: number | null;
  };
  type AlbumRowExt = AlbumRow & { _rowid: number };
  type AfRow = Record<string, unknown> & {
    song?: string;
    album?: string;
    artist?: string;
    album_id?: string;
  };

  const albumsOut: MasterAlbum[] = [];
  const albumById = new Map<string, MasterAlbum>();
  const bestAlbumByArtistNorm = new Map<string, AlbumRowExt>();

  for (const r of db.prepare("SELECT rowid AS _rowid, * FROM albums").iterate() as IterableIterator<AlbumRowExt>) {
    if (!r.artist || !r.album) continue;
    const an = norm(resolveCanonical(r.artist, aliasMap));
    if (!artistSet.has(an)) continue;
    const aid = retroverseAlbumId(r.artist, r.album, aliasMap);
    if (!albumById.has(aid)) {
      const ma: MasterAlbum = {
        retroverse_album_id: aid,
        album_title: r.album,
        artist: r.artist,
        artist_canonical: resolveCanonical(r.artist, aliasMap),
        chart_date: r.date,
        chart_rank: r.rank,
        chart_history: [],
        length: r.length ?? null,
        track_length: r.track_length ?? null,
        sources: [
          {
            source_system: "billboard_200_sqlite",
            source_path: relative(REPO_ROOT, bb200Path),
            sqlite_table: "albums",
            sqlite_rowid: r._rowid,
          },
        ],
        acoustic_features: null,
      };
      albumById.set(aid, ma);
      albumsOut.push(ma);
    }
    const prev = bestAlbumByArtistNorm.get(an);
    const d = r.date ?? "";
    const pd = prev?.date ?? "";
    if (!prev || d > pd) {
      bestAlbumByArtistNorm.set(an, r);
    }
  }

  const albumHistoryState = new Map<
    string,
    { lastDate: string | null; lastRank: number | null; peak: number | null; weeks: number }
  >();
  for (const r of db.prepare(
    "SELECT date, artist, album, rank FROM albums ORDER BY date ASC, CAST(rank AS INTEGER) ASC",
  ).iterate() as IterableIterator<AlbumRow>) {
    if (!r.artist || !r.album || !r.date || !r.rank) continue;
    const an = norm(resolveCanonical(r.artist, aliasMap));
    if (!artistSet.has(an)) continue;
    const rank = Number(r.rank);
    if (!Number.isFinite(rank)) continue;

    const aid = retroverseAlbumId(r.artist, r.album, aliasMap);
    const album = albumById.get(aid);
    if (!album) continue;

    const prev = albumHistoryState.get(aid) ?? {
      lastDate: null,
      lastRank: null,
      peak: null,
      weeks: 0,
    };
    const weeks = prev.weeks + 1;
    const peak = prev.peak == null ? rank : Math.min(prev.peak, rank);
    const lastWeek =
      prev.lastRank != null && isSequentialChartWeek(prev.lastDate, r.date)
        ? prev.lastRank
        : null;

    album.chart_history.push({
      chart_date: r.date,
      rank,
      last_week: lastWeek,
      peak,
      weeks_on_chart: weeks,
    });

    albumHistoryState.set(aid, {
      lastDate: r.date,
      lastRank: rank,
      peak,
      weeks,
    });
  }

  const songKeySet = new Set(
    [...songById.values()].map((s) => `${s.artist_normalized}|${s.title_normalized}`),
  );
  const albumAfKeys = new Set(
    albumsOut.map((a) => `${norm(a.artist_canonical)}|${norm(a.album_title)}`),
  );

  const afByKey = new Map<string, AfRow>();
  const afByArtistAlbum = new Map<string, AfRow>();

  for (const r of db.prepare("SELECT * FROM acoustic_features").iterate() as IterableIterator<AfRow>) {
    const a = `${r.artist ?? ""}`;
    const t = `${r.song ?? ""}`;
    const al = `${r.album ?? ""}`;
    const sk = `${norm(resolveCanonical(a, aliasMap))}|${normalizeTitle(t)}`;
    if (songKeySet.has(sk) && !afByKey.has(sk)) {
      afByKey.set(sk, r);
    }
    const ak = `${norm(resolveCanonical(a, aliasMap))}|${norm(al)}`;
    if (albumAfKeys.has(ak) && !afByArtistAlbum.has(ak)) {
      afByArtistAlbum.set(ak, r);
    }
  }

  for (const s of songById.values()) {
    const k = `${s.artist_normalized}|${s.title_normalized}`;
    const af = afByKey.get(k);
    if (af) {
      const { song: _x, ...rest } = af;
      void _x;
      s.acoustic_features = rest as Record<string, unknown>;
    }
  }

  for (const al of albumsOut) {
    const af = afByArtistAlbum.get(`${norm(al.artist_canonical)}|${norm(al.album_title)}`);
    if (af) {
      const { song: _s, ...rest } = af;
      void _s;
      al.acoustic_features = rest as Record<string, unknown>;
    }
  }

  for (const s of songById.values()) {
    const al = bestAlbumByArtistNorm.get(s.artist_normalized);
    if (al) {
      s.album = {
        retroverse_album_id: retroverseAlbumId(al.artist!, al.album!, aliasMap),
        album_title: al.album,
        chart_date: al.date,
        chart_rank: al.rank,
        attach_method: "best_billboard_200_row_for_artist",
      };
    }
  }

  db.close();

  console.error("[build_master_dataset] matching VDJ videos to Hot 100 (exact + Fuse on prefix bucket)…");
  const bbExact = new Map<string, IndexedBillboardSong>();
  for (const s of billboardSongs) {
    const songTitleNorm = normalizeTitle(s.title);
    bbExact.set(`${norm(s.artist_canonical)}|${songTitleNorm}`, s);
  }

  const videosOut: MasterVideo[] = [];
  let vdjMatched = 0;
  let vdjFuzzyHits = 0;
  let i = 0;
  const fuseThreshold = 0.45;
  for (const v of vdjVideos) {
    i++;
    if (i % 1000 === 0) {
      console.log("VDJ LOOP:", i);
    }
    const tags = v.tags ?? {};
    const artist = `${tags.artist ?? tags.artist_raw ?? ""}`.trim();
    const artist_canonical = resolveCanonical(artist, aliasMap);
    const title = `${tags.title ?? tags.title_raw ?? ""}`.trim();
    const videoTitleNormalized = normalizeTitle(title);
    const q = `${artist_canonical} ${title}`.trim();
    const exactKey = `${norm(artist_canonical)}|${videoTitleNormalized}`;
    let bs: (IndexedBillboardSong & { _q?: string }) | null = bbExact.get(exactKey) ?? null;
    let matchScore: number | null = bs ? 0 : null;
    let matchType: "exact_norm" | "fuse_bucket" | "title_include" = "exact_norm";
    if (!bs && q) {
      const p = artistPrefix2(artist_canonical);
      const mini = fuseByArtistPrefix.get(p);
      const hits = mini?.search(q, { limit: 15 }) ?? [];
      for (const hit of hits) {
        if (hit.score == null || hit.score >= fuseThreshold) continue;
        const cand = hit.item as IndexedBillboardSong & { _q: string };
        const candTitleNorm = normalizeTitle(cand.title);
        const artistScore = artistSimilarityScore(artist_canonical, cand.artist_canonical);
        if (titlesCompatible(candTitleNorm, videoTitleNormalized) && artistScore >= 0.5) {
          bs = cand;
          matchScore = hit.score;
          matchType = "fuse_bucket";
          vdjFuzzyHits++;
          break;
        }
      }
    }
    if (!bs) {
      const p = artistPrefix2(artist_canonical);
      const bucket = byArtistPrefix2.get(p) ?? [];
      let bestTitleInclude:
        | { song: IndexedBillboardSong; titleScore: number; artistScore: number }
        | null = null;
      for (const s of bucket) {
        const songTitleNorm = normalizeTitle(s.title);
        const titleScore = titleMatchScore(songTitleNorm, videoTitleNormalized);
        if (!titleScore) continue;

        const artistScore = artistSimilarityScore(artist_canonical, s.artist_canonical);
        if (artistScore < 0.5) continue;

        if (
          !bestTitleInclude ||
          titleScore > bestTitleInclude.titleScore ||
          (titleScore === bestTitleInclude.titleScore &&
            artistScore > bestTitleInclude.artistScore)
        ) {
          bestTitleInclude = { song: s, titleScore, artistScore };
        }
      }
      if (bestTitleInclude) {
        bs = bestTitleInclude.song;
        matchScore = 0.05;
        matchType = "title_include";
        vdjFuzzyHits++;
      }
    }
    let matched: Record<string, unknown> | null = null;
    let matchedSongId: string | null = null;
    if (bs && matchScore != null) {
      const sid =
        bs.retroverse_id ||
        retroverseSongId(bs.title, resolveCanonical(bs.artist, aliasMap), aliasMap);
      const song = songById.get(sid);
      matchedSongId = sid;
      matched = {
        retroverse_id: sid,
        chart_song_id: bs.chart_song_id,
        fuse_score: matchScore,
        match_type: matchType,
      };
      if (song) {
        vdjMatched++;
        const dur = (v.playback as { duration_ms?: number } | undefined)?.duration_ms;
        const vdjYear = v.year ?? null;
        const songYear = bs?.first_chart_year ?? null;
        song.vdj_videos.push({
          video_id: v.video_id,
          file_path: v.file?.path ?? null,
          filename: v.file?.filename ?? null,
          extension: v.file?.extension ?? null,
          year: vdjYear,
          library_year: vdjYear,
          song_year: songYear,
          year_context: {
            library: vdjYear,
            song: songYear,
          },
          fuse_score: matchScore,
          duration_ms: dur ?? null,
        });
      } else {
        console.log("SONG NOT FOUND FOR MATCH:", {
          title: bs.title,
          artist: bs.artist,
          sid,
        });
      }
    }
    const pb = (v.playback ?? {}) as {
      duration_ms?: number | null;
      play_count?: number | null;
      last_played?: number | null;
    };
    const meta = (v.metadata ?? {}) as {
      album?: string | null;
      year?: number | null;
      genre?: string | null;
      bpm?: number | null;
      key?: string | null;
    };
    const fp = v.file?.path ?? null;
    const paths = deriveCanonicalMediaPaths(fp);
    const vdjYear = v.year ?? null;
    if (!v.album && !v.genre && !pb.duration_ms) {
      console.log("MISSING METADATA:", v.file?.filename);
    }
    videosOut.push({
      video_id: v.video_id,
      file_path: fp,
      relative_path: paths.relative_path,
      video_url: paths.video_url,
      thumbnail_url: paths.thumbnail_url,
      filename: v.file?.filename ?? null,
      extension: v.file?.extension ?? null,
      artist: artist || null,
      artist_canonical: artist ? artist_canonical : null,
      title: title || null,
      title_normalized: videoTitleNormalized,
      album: v.album ?? meta.album ?? null,
      year: v.year ?? meta.year ?? null,
      library_year: vdjYear,
      song_year: bs?.first_chart_year ?? null,
      year_context: {
        library: vdjYear,
        song: bs?.first_chart_year ?? null,
      },
      genre: v.genre ?? meta.genre ?? null,
      duration_ms: pb.duration_ms ?? null,
      play_count: pb.play_count ?? 0,
      last_played: pb.last_played ?? null,
      bpm: v.bpm ?? meta.bpm ?? null,
      musical_key: v.musical_key ?? meta.key ?? null,
      matched_song_id: matchedSongId,
      sources: [
        {
          source_system: "vdj_library_export",
          source_path: relative(REPO_ROOT, vdjPath!),
          pipeline_run_id: vdjRunId,
        },
      ],
      matched_song: matched,
    });
  }
  console.log("STEP: VDJ LOOP COMPLETE");

  const songVideoMap = new Map<string, Array<Record<string, unknown>>>();
  for (const v of videosOut) {
    const matchedSong = v.matched_song as { retroverse_id?: string; fuse_score?: number } | null;
    const sid = v.matched_song_id || matchedSong?.retroverse_id || null;
    if (!sid) continue;

    if (!songVideoMap.has(sid)) {
      songVideoMap.set(sid, []);
    }

    songVideoMap.get(sid)!.push({
      video_id: v.video_id,
      file_path: v.file_path,
      relative_path: v.relative_path,
      video_url: v.video_url,
      thumbnail_url: v.thumbnail_url,
      filename: v.filename,
      extension: v.extension,
      year: v.year,
      library_year: v.library_year,
      song_year: v.song_year,
      year_context: v.year_context,
      play_count: v.play_count,
      duration_ms: v.duration_ms,
      fuse_score: matchedSong?.fuse_score ?? 0,
    });
  }

  for (const [sid, vids] of songVideoMap.entries()) {
    const song = songById.get(sid);
    if (!song) continue;

    song.vdj_videos = vids;
    song.play_count_total = vids.reduce(
      (sum, v) => sum + (typeof v.play_count === "number" ? v.play_count : 0),
      0,
    );
  }

  const videoMap = new Map<string, MasterVideo>();
  for (const v of videosOut) {
    videoMap.set(v.video_id, v);
  }
  for (const song of songById.values()) {
    for (const ref of song.vdj_videos) {
      const vid = ref.video_id as string;
      const full = videoMap.get(vid);
      const pc = full?.play_count ?? 0;
      ref.play_count = typeof pc === "number" ? pc : 0;
      if (full) {
        ref.relative_path = full.relative_path;
        ref.video_url = full.video_url;
        ref.thumbnail_url = full.thumbnail_url;
        ref.year = full.year;
        ref.library_year = full.library_year;
        ref.song_year = full.song_year;
        ref.year_context = full.year_context;
      } else {
        const p = deriveCanonicalMediaPaths((ref.file_path as string | null) ?? null);
        ref.relative_path = p.relative_path;
        ref.video_url = p.video_url;
        ref.thumbnail_url = p.thumbnail_url;
      }
    }
    const vdjYears = song.vdj_videos
      .map((v) => (typeof v.year === "number" ? v.year : null))
      .filter((y): y is number => y !== null);
    const library_year = vdjYears.length
      ? vdjYears[0]
      : null;
    const songBillboard = song.billboard as { first_chart_year?: number } | null;
    const song_year = typeof songBillboard?.first_chart_year === "number"
      ? songBillboard.first_chart_year
      : null;

    song.year = song_year;
    song.library_year = library_year;
    song.song_year = song_year;
    song.year_context = {
      song: song_year,
      library: library_year,
    };
    song.play_count_total = song.vdj_videos.reduce(
      (sum, v) => sum + (typeof v.play_count === "number" ? v.play_count : 0),
      0,
    );
  }

  console.log("STEP: BUILDING OUTPUT");
  console.error("[build_master_dataset] loading movies / TV (slim records)…");
  const moviesDoc = loadJson<{ records: Record<string, unknown>[] }>(moviesPath);
  const tvDoc = loadJson<{ records: Record<string, unknown>[] }>(tvPath);

  const movies = (moviesDoc.records ?? []).map((r) => ({
    ...slimMovieRecord(r),
    sources: [
      {
        source_system: "screen_culture_warehouse",
        source_path: relative(REPO_ROOT, moviesPath),
      },
    ],
  }));

  const tv = (tvDoc.records ?? []).map((r) => ({
    ...slimTvRecord(r),
    sources: [
      {
        source_system: "screen_culture_warehouse",
        source_path: relative(REPO_ROOT, tvPath),
      },
    ],
  }));

  const songs = [...songById.values()].sort((a, b) =>
    a.retroverse_id.localeCompare(b.retroverse_id),
  );

  const generatedAt = new Date().toISOString();
  const out = {
    meta: {
      generated_at_utc: generatedAt,
      schema_version: "1.0.0",
      sources: [
        { role: "artist_aliases", path: relative(REPO_ROOT, aliasesPath) },
        { role: "billboard_hot100_export", path: relative(REPO_ROOT, billboardPath!) },
        { role: "billboard_hot100_sqlite", path: relative(REPO_ROOT, bbHot100Path) },
        { role: "vdj_library_export", path: relative(REPO_ROOT, vdjPath!) },
        { role: "year_master", path: relative(REPO_ROOT, yearMasterPath) },
        { role: "billboard_200_sqlite", path: relative(REPO_ROOT, bb200Path) },
        { role: "movies_master", path: relative(REPO_ROOT, moviesPath) },
        { role: "television_master", path: relative(REPO_ROOT, tvPath) },
      ],
      normalized_schemas: [
        "data/normalized/songs.schema.json",
        "data/normalized/albums.schema.json",
        "data/normalized/videos.schema.json",
        "data/normalized/movies.schema.json",
        "data/normalized/tv.schema.json",
      ],
    },
    stats: {
      song_count: songs.length,
      billboard_song_count: billboardSongs.length,
      year_master_only_songs: songs.filter((s) => !s.billboard).length,
      songs_with_chart_history: songs.filter((s) => s.chart_history.length > 0).length,
      songs_with_year_master: songs.filter((s) => s.year_master.length > 0).length,
      songs_with_acoustic_features: songs.filter((s) => s.acoustic_features).length,
      songs_with_album_attach: songs.filter((s) => s.album).length,
      album_count: albumsOut.length,
      albums_with_chart_history: albumsOut.filter((a) => a.chart_history.length > 0).length,
      video_count: videosOut.length,
      vdj_matched_to_billboard: vdjMatched,
      vdj_fuzzy_matches: vdjFuzzyHits,
      movie_count: movies.length,
      tv_count: tv.length,
      artist_alias_lookup_keys: aliasMap.size,
    },
    songs,
    albums: albumsOut,
    videos: videosOut,
    movies,
    tv,
  };

  mkdirSync(dirname(OUT_PATH), { recursive: true });
  console.log("STEP: WRITING FILE");
  console.error("[build_master_dataset] writing retroverse_master.json…");
  writeFileSync(OUT_PATH, JSON.stringify(out), "utf8");
  console.log("DONE WRITING MASTER");
  console.error(`Wrote ${relative(REPO_ROOT, OUT_PATH)}`);
  console.log("BUILD COMPLETE");
  process.exit(0);
}

main();
