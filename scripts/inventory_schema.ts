/**
 * Scans data/raw, data/derived, data/movies, data/registry and writes
 * data/docs/schema_inventory.json (read-only; does not modify sources).
 */
import Database from "better-sqlite3";
import {
  closeSync,
  createReadStream,
  existsSync,
  mkdirSync,
  openSync,
  readFileSync,
  readSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { createInterface } from "node:readline";
import { basename, dirname, extname, join, relative } from "node:path";
import { gunzipSync } from "node:zlib";

const REPO_ROOT = join(import.meta.dirname, "..");
const DATA_ROOTS = [
  join(REPO_ROOT, "data/raw"),
  join(REPO_ROOT, "data/derived"),
  join(REPO_ROOT, "data/movies"),
  join(REPO_ROOT, "data/registry"),
];
const OUT_PATH = join(REPO_ROOT, "data/docs/schema_inventory.json");

type Dataset = {
  path: string;
  entity_type: string;
  fields: string[];
  sample_records: unknown[];
  notes?: string;
};

function shouldSkip(absPath: string): boolean {
  const b = basename(absPath);
  if (b === ".DS_Store") return true;
  if (/\.bak\.\d+$/i.test(b)) return true;
  if (/\.(png|jpe?g|gif|webp|pdf)$/i.test(b)) return true;
  if (absPath.endsWith("-shm") || absPath.endsWith("-wal")) return true;
  return false;
}

function walkFilesSync(dir: string, out: string[]): void {
  if (!existsSync(dir)) return;
  const names = readdirSync(dir);
  for (const n of names) {
    const p = join(dir, n);
    if (shouldSkip(p)) continue;
    const st = statSync(p);
    if (st.isDirectory()) walkFilesSync(p, out);
    else if (st.isFile()) out.push(p);
  }
}

function relDataPath(absPath: string): string {
  return relative(REPO_ROOT, absPath).replaceAll("\\", "/");
}

function inferEntityFromPath(p: string, fields: string[], kind: string): string {
  const lower = p.toLowerCase();
  if (kind === "imdb_tsv" || lower.includes("/imdb/")) {
    if (lower.includes("title.basics")) return "movie";
    if (lower.includes("title.akas")) return "movie";
    if (lower.includes("title.principals")) return "other";
    if (lower.includes("name.basics")) return "other";
    if (lower.includes("title.ratings")) return "movie";
  }
  if (lower.includes("movie_memory")) return "movie";
  if (lower.includes("movies_master") || lower.includes("movies_by_year"))
    return "movie";
  if (
    lower.includes("television") ||
    lower.includes("tv_listings") ||
    lower.includes("tv.json")
  )
    return "tv";
  if (
    lower.includes("vdj") ||
    lower.includes("video") ||
    lower.includes("media-index")
  )
    return "video";
  if (
    lower.includes("billboard") ||
    lower.includes("hot100") ||
    lower.includes("hot-100") ||
    lower.includes("chart") ||
    lower.includes("year-masters") ||
    lower.includes("year_master") ||
    lower.includes("radio_airplay")
  )
    return "song";
  if (lower.includes("album") || lower.includes("billboard-200"))
    return "album";
  if (lower.includes("magazine_issues")) return "other";
  if (lower.endsWith(".md")) return "other";
  if (lower.includes("registry")) return "other";
  return "other";
}

function parseCsvHeader(line: string): string[] {
  return line.split(",").map((s) => s.trim());
}

async function readFirstLine(path: string): Promise<string | null> {
  return new Promise((resolve) => {
    const stream = createReadStream(path, { encoding: "utf8" });
    const rl = createInterface({ input: stream, crlfDelay: Infinity });
    let done = false;
    rl.once("line", (line) => {
      done = true;
      rl.close();
      resolve(line);
    });
    rl.once("close", () => {
      if (!done) resolve(null);
    });
    stream.once("error", () => resolve(null));
  });
}

function sqliteFields(dbPath: string): string[] {
  const db = new Database(dbPath, { readonly: true, fileMustExist: true });
  try {
    const tables = db
      .prepare(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
      )
      .all() as { name: string }[];
    const fields: string[] = [];
    for (const { name } of tables) {
      const cols = db.prepare(`PRAGMA table_info(${quoteIdent(name)})`).all() as {
        name: string;
      }[];
      for (const c of cols) {
        fields.push(`${name}.${c.name}`);
      }
    }
    return fields;
  } finally {
    db.close();
  }
}

function quoteIdent(name: string): string {
  return `"${name.replaceAll('"', '""')}"`;
}

function sampleSqliteRows(dbPath: string, limitPerTable: number): unknown[] {
  const db = new Database(dbPath, { readonly: true, fileMustExist: true });
  const samples: unknown[] = [];
  try {
    const tables = db
      .prepare(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
      )
      .all() as { name: string }[];
    for (const { name } of tables) {
      const rows = db
        .prepare(`SELECT * FROM ${quoteIdent(name)} LIMIT ?`)
        .all(limitPerTable) as Record<string, unknown>[];
      for (const row of rows) {
        samples.push({ _table: name, ...row });
        if (samples.length >= 5) return samples;
      }
    }
  } finally {
    db.close();
  }
  return samples.slice(0, 5);
}

function readJsonSample(absPath: string, maxBytes: number): {
  fields: string[];
  samples: unknown[];
} {
  const st = statSync(absPath);
  const readSize = Math.min(st.size, maxBytes);
  const fd = openSync(absPath, "r");
  const buf = Buffer.alloc(readSize);
  try {
    readSync(fd, buf, 0, readSize, 0);
  } finally {
    closeSync(fd);
  }
  const text = buf.toString("utf8");
  try {
    const parsed = JSON.parse(text) as unknown;
    return extractFromParsed(parsed);
  } catch {
    return extractFromPartialJson(text);
  }
}

function extractFromParsed(parsed: unknown): {
  fields: string[];
  samples: unknown[];
} {
  if (Array.isArray(parsed)) {
    const first = parsed[0];
    if (first && typeof first === "object" && !Array.isArray(first)) {
      return {
        fields: Object.keys(first as object),
        samples: parsed.slice(0, 5),
      };
    }
    return { fields: ["[array items]"], samples: parsed.slice(0, 5) };
  }
  if (parsed && typeof parsed === "object") {
    const o = parsed as Record<string, unknown>;
    const keys = Object.keys(o);
    if (keys.every((k) => /^\d{4}$/.test(k))) {
      const y = keys[0];
      const inner = o[y];
      if (inner && typeof inner === "object") {
        const innerKeys = Object.keys(inner as object);
        return {
          fields: [`year_key`, ...innerKeys],
          samples: [inner],
        };
      }
    }
    const songLike = o.songs ?? o.videos ?? o.records;
    if (Array.isArray(songLike) && songLike[0] && typeof songLike[0] === "object") {
      return {
        fields: Object.keys(songLike[0] as object),
        samples: songLike.slice(0, 5),
      };
    }
    return { fields: keys, samples: [parsed] };
  }
  return { fields: [], samples: [] };
}

function extractFromPartialJson(text: string): {
  fields: string[];
  samples: unknown[];
} {
  const m = text.match(/\{[\s\S]{0,8000}/);
  if (!m) return { fields: ["(unparsed large json)"], samples: [] };
  try {
    const parsed = JSON.parse(m[0] + "}") as unknown;
    return extractFromParsed(parsed);
  } catch {
    const keyMatch = [...text.matchAll(/"([^"]+)"\s*:/g)].map((x) => x[1]);
    const uniq = [...new Set(keyMatch)].slice(0, 40);
    return { fields: uniq.length ? uniq : ["(parse error)"], samples: [] };
  }
}

function tsvHeaderGz(path: string): string[] {
  const raw = readFileSync(path);
  const text = gunzipSync(raw).toString("utf8", 0, Math.min(raw.length * 10, 2_000_000));
  const line = text.split(/\r?\n/)[0] ?? "";
  return line.split("\t").map((s) => s.trim());
}

function tsvHeaderPlain(path: string): string[] {
  const fd = readFileSync(path, { encoding: "utf8" });
  const line = fd.split(/\r?\n/)[0] ?? "";
  return line.split("\t").map((s) => s.trim());
}

async function buildDatasetForFile(absPath: string): Promise<Dataset | null> {
  const rel = relDataPath(absPath);
  const ext = extname(absPath).toLowerCase();

  if (ext === ".yaml" || ext === ".yml") {
    const text = readFileSync(absPath, "utf8");
    const keys = [...text.matchAll(/^([a-zA-Z0-9_]+):/gm)].map((m) => m[1]);
    const fields = [...new Set(keys)].slice(0, 30);
    return {
      path: rel,
      entity_type: "other",
      fields: fields.length ? fields : ["(yaml lines)"],
      sample_records: [{ preview: text.slice(0, 400) }],
      notes: "YAML registry; structure is nested under datasets:",
    };
  }

  if (ext === ".md") {
    const text = readFileSync(absPath, "utf8");
    return {
      path: rel,
      entity_type: "other",
      fields: ["markdown"],
      sample_records: [{ text: text.slice(0, 500) }],
    };
  }

  if (ext === ".csv") {
    const line = await readFirstLine(absPath);
    if (!line) return null;
    const fields = parseCsvHeader(line);
    const full = readFileSync(absPath, "utf8");
    const lines = full.split(/\r?\n/).filter(Boolean);
    const samples = lines.slice(1, 6).map((row) => {
      const cols = row.split(",");
      const o: Record<string, string> = {};
      fields.forEach((f, i) => {
        o[f] = cols[i] ?? "";
      });
      return o;
    });
    return {
      path: rel,
      entity_type: inferEntityFromPath(rel, fields, "csv"),
      fields,
      sample_records: samples,
    };
  }

  if (ext === ".db" || ext === ".sqlite" || ext === ".sqlite3") {
    const fields = sqliteFields(absPath);
    const sample_records = sampleSqliteRows(absPath, 2);
    return {
      path: rel,
      entity_type: inferEntityFromPath(rel, fields, "sqlite"),
      fields,
      sample_records,
    };
  }

  if (ext === ".json") {
    const st = statSync(absPath);
    if (st.size > 1024 * 1024) {
      const { fields, samples } = readJsonSample(absPath, 500_000);
      return {
        path: rel,
        entity_type: inferEntityFromPath(rel, fields, "json"),
        fields,
        sample_records: samples,
        notes: `Large JSON (${st.size} bytes); sampled first ~500KB for structure.`,
      };
    }
    const parsed = JSON.parse(readFileSync(absPath, "utf8")) as unknown;
    const { fields, samples } = extractFromParsed(parsed);
    return {
      path: rel,
      entity_type: inferEntityFromPath(rel, fields, "json"),
      fields,
      sample_records: samples,
    };
  }

  if (ext === ".jsonl") {
    const lines = readFileSync(absPath, "utf8").split(/\r?\n/).filter(Boolean).slice(0, 5);
    const objs = lines.map((l) => JSON.parse(l) as unknown);
    const fields =
      objs[0] && typeof objs[0] === "object" ? Object.keys(objs[0] as object) : [];
    return {
      path: rel,
      entity_type: "other",
      fields,
      sample_records: objs,
    };
  }

  if (ext === ".tsv") {
    const fields = tsvHeaderPlain(absPath);
    return {
      path: rel,
      entity_type: inferEntityFromPath(rel, fields, "tsv"),
      fields,
      sample_records: [],
      notes: "TSV; header only sampled (rows not loaded).",
    };
  }

  if (ext === ".gz" && absPath.endsWith(".tsv.gz")) {
    const fields = tsvHeaderGz(absPath);
    return {
      path: rel,
      entity_type: inferEntityFromPath(rel, fields, "tsv_gz"),
      fields,
      sample_records: [],
      notes: "Gzipped TSV; header only sampled.",
    };
  }

  return {
    path: rel,
    entity_type: "other",
    fields: ["(unsupported extension)"],
    sample_records: [],
    notes: `No structured reader for ${ext}`,
  };
}

function sanitizeSample(x: unknown, depth = 0): unknown {
  if (depth > 5) return "[max depth]";
  if (x === null || typeof x === "number" || typeof x === "boolean") return x;
  if (typeof x === "string") return x.length > 500 ? `${x.slice(0, 500)}…` : x;
  if (Array.isArray(x)) {
    return x.slice(0, 10).map((e) => sanitizeSample(e, depth + 1));
  }
  if (typeof x === "object") {
    const o = x as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const k of Object.keys(o).slice(0, 40)) {
      out[k] = sanitizeSample(o[k], depth + 1);
    }
    return out;
  }
  return String(x);
}

function mergeRunGroups(datasets: Dataset[]): Dataset[] {
  const groups: { pattern: string; matcher: (p: string) => boolean; note: string }[] = [
    {
      pattern: "data/derived/media-index/canonical/billboard_run_*.json",
      matcher: (p) =>
        /data\/derived\/media-index\/canonical\/billboard_run_\d+\.json$/.test(p) &&
        !p.includes("decision_demo"),
      note: "Repeated pipeline exports; schema identical across run IDs.",
    },
    {
      pattern: "data/derived/media-index/canonical/vdj_library_run_*.json",
      matcher: (p) =>
        /data\/derived\/media-index\/canonical\/vdj_library_run_\d+\.json$/.test(p) &&
        !p.includes("decision_demo"),
      note: "Repeated pipeline exports; schema identical across run IDs.",
    },
    {
      pattern: "data/derived/media-index/matching/chart_matches_run_*.json",
      matcher: (p) =>
        /data\/derived\/media-index\/matching\/chart_matches_run_\d+\.json$/.test(p),
      note: "Repeated match runs; schema identical across run IDs.",
    },
    {
      pattern: "data/derived/year-masters/retroverse_year_end_*.csv",
      matcher: (p) =>
        /data\/derived\/year-masters\/retroverse_year_end_\d{4}\.csv$/.test(p),
      note: "One file per chart year; same columns.",
    },
    {
      pattern: "data/derived/year-masters/retroverse_year_end_*_top40.csv",
      matcher: (p) =>
        /data\/derived\/year-masters\/retroverse_year_end_\d{4}_top40\.csv$/.test(p),
      note: "One file per chart year; same columns as full year-end CSV.",
    },
  ];

  const used = new Set<string>();
  const out: Dataset[] = [];

  for (const g of groups) {
    const members = datasets.filter((d) => g.matcher(d.path));
    if (members.length === 0) continue;
    members.forEach((m) => used.add(m.path));
    const rep = members.sort((a, b) => a.path.localeCompare(b.path))[0]!;
    out.push({
      path: g.pattern,
      entity_type: rep.entity_type,
      fields: rep.fields,
      sample_records: rep.sample_records,
      notes: `${g.note} (${members.length} files). Representative: ${rep.path}`,
    });
  }

  for (const d of datasets) {
    if (!used.has(d.path)) out.push(d);
  }
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

async function main(): Promise<void> {
  const files: string[] = [];
  for (const root of DATA_ROOTS) walkFilesSync(root, files);

  const datasets: Dataset[] = [];
  for (const f of files.sort((a, b) => a.localeCompare(b))) {
    try {
      const ds = await buildDatasetForFile(f);
      if (ds) datasets.push(ds);
    } catch (e) {
      datasets.push({
        path: relDataPath(f),
        entity_type: "other",
        fields: ["(error)"],
        sample_records: [],
        notes: String(e),
      });
    }
  }

  const merged = mergeRunGroups(datasets).map((d) => ({
    ...d,
    sample_records: d.sample_records.slice(0, 5).map((r) => sanitizeSample(r)),
  }));
  mkdirSync(dirname(OUT_PATH), { recursive: true });
  writeFileSync(OUT_PATH, JSON.stringify({ datasets: merged }, null, 2), "utf8");
  console.error(`Wrote ${merged.length} dataset entries to ${relative(REPO_ROOT, OUT_PATH)}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
