#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "video_links_recovered.csv"

YOUTUBE_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?[^ \t\r\n<>'\"]*v=[A-Za-z0-9_-]{11}[^ \t\r\n<>'\"]*|shorts/[A-Za-z0-9_-]{11}[^ \t\r\n<>'\"]*|embed/[A-Za-z0-9_-]{11}[^ \t\r\n<>'\"]*)|youtu\.be/[A-Za-z0-9_-]{11}[^ \t\r\n<>'\"]*)",
    re.IGNORECASE,
)
PRIORITY_NAME_RE = re.compile(r"(video|youtube|tag|vdj|playlist|export)", re.IGNORECASE)
TEXT_EXTENSIONS = {
    ".csv",
    ".tsv",
    ".json",
    ".xml",
    ".txt",
    ".md",
    ".html",
    ".htm",
    ".m3u",
    ".m3u8",
    ".vdjfolder",
}
SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".next",
    ".cache",
    ".Trash",
    "Library/Caches",
}


@dataclass(frozen=True)
class Record:
    artist: str
    title: str
    youtube_url: str
    source: str


def normalize_space(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_name(value: str | None) -> str:
    return normalize_space(value).lower()


def normalize_url(value: str | None) -> str:
    raw = normalize_space(value)
    if not raw:
      return ""
    match = YOUTUBE_URL_RE.search(raw)
    return match.group(0) if match else ""


def youtube_url_from_id(value: str | None) -> str:
    candidate = normalize_space(value)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return "https://www.youtube.com/watch?v=" + candidate
    return ""


def parse_artist_title_from_filename(value: str | None) -> tuple[str, str]:
    filename = Path(str(value or "")).name
    if not filename:
        return "", ""
    stem = Path(filename).stem
    stem = normalize_space(stem.replace("_", " "))
    if " - " in stem:
        artist, title = stem.split(" - ", 1)
        return normalize_space(artist), normalize_space(title)
    if " – " in stem:
        artist, title = stem.split(" – ", 1)
        return normalize_space(artist), normalize_space(title)
    return "", stem


def record_key(artist: str, title: str, youtube_url: str) -> tuple[str, str, str]:
    return (normalize_name(artist), normalize_name(title), normalize_url(youtube_url))


def candidate_roots() -> list[Path]:
    home = Path.home()
    requested = [
        home / "Documents",
        home / "Downloads",
        home / "Desktop",
        home / "Sites",
        Path("/Users/bobmbp/Documents/VDJ"),
        Path("/Users/bobmbp/Documents/VDJ_XML_Tools"),
        Path("/Users/bobmbp/Library/Mobile Documents"),
    ]

    inferred_equivalents = [
        home / "Documents" / "VDJ",
        home / "Documents" / "VDJ_XML_Tools",
        home / "Library" / "Mobile Documents",
    ]

    roots: list[Path] = []
    seen: set[Path] = set()
    for path in requested + inferred_equivalents:
        if path.exists() and path not in seen:
            roots.append(path)
            seen.add(path)
    return roots


def rg_content_candidates(roots: list[Path]) -> list[Path]:
    import subprocess

    if not roots:
        return []

    cmd = ["rg", "-i", "-l"]
    for ext in sorted(TEXT_EXTENSIONS):
        cmd.extend(["--glob", "*" + ext])
    cmd.append(r"youtube\.com|youtu\.be|watch\?v=")
    cmd.extend([str(root) for root in roots])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return []

    files: list[Path] = []
    seen: set[Path] = set()
    for line in result.stdout.splitlines():
        path = Path(line.strip())
        if path.exists() and path not in seen:
            files.append(path)
            seen.add(path)
    return files


def walk_priority_zip_candidates(roots: list[Path]) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    home = Path.home()
    zip_scan_roots: list[Path] = []
    for root in roots:
        root_text = str(root)
        if root == home / "Documents" or root == home / "Downloads" or "VDJ" in root_text:
            zip_scan_roots.append(root)

    for root in zip_scan_roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in SKIP_DIR_NAMES and not name.startswith(".")
            ]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix.lower() != ".zip":
                    continue
                text = str(path)
                if "VDJ Backups" in text or PRIORITY_NAME_RE.search(text):
                    if path not in seen:
                        candidates.append(path)
                        seen.add(path)
    return candidates


def fields_lookup(row: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in row.items():
        clean = re.sub(r"[^a-z0-9]+", "", str(key).lower())
        if clean and clean not in normalized:
            normalized[clean] = value
    return normalized


def pick_value(mapping: dict[str, object], *keys: str) -> str:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return normalize_space(str(mapping[key]))
    return ""


def extract_from_row_dict(row: dict[str, object], source: str) -> list[Record]:
    normalized = fields_lookup(row)

    artist = pick_value(normalized, "artist", "author", "artistcanonical", "performer")
    title = pick_value(normalized, "title", "song", "track", "name")
    file_hint = pick_value(normalized, "filepath", "filename", "path", "file", "sourcepath")
    if (not artist or not title) and file_hint:
        parsed_artist, parsed_title = parse_artist_title_from_filename(file_hint)
        artist = artist or parsed_artist
        title = title or parsed_title

    youtube_url = ""
    for key in ("youtubeurl", "youtube", "url", "link", "comment", "description", "notes"):
        youtube_url = normalize_url(pick_value(normalized, key))
        if youtube_url:
            break

    if not youtube_url:
        youtube_url = youtube_url_from_id(pick_value(normalized, "youtubeid", "videoid"))

    if not youtube_url:
        for value in row.values():
            youtube_url = normalize_url(value if isinstance(value, str) else "")
            if youtube_url:
                break

    artist = normalize_name(artist)
    title = normalize_name(title)
    youtube_url = normalize_url(youtube_url)
    if not artist or not title or not youtube_url:
        return []

    return [Record(artist=artist, title=title, youtube_url=youtube_url, source=source)]


def parse_csv_text(text: str, source: str) -> list[Record]:
    stripped = text.lstrip("\ufeff")
    lines = stripped.splitlines()
    delimiter = ","
    if lines and lines[0].lower().startswith("sep="):
        delimiter = lines[0][4:5] or ","
        stripped = "\n".join(lines[1:])
    elif "\t" in stripped[:2048] and stripped[:2048].count("\t") > stripped[:2048].count(","):
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(stripped), delimiter=delimiter)
    records: list[Record] = []
    for row in reader:
        if not row:
            continue
        records.extend(extract_from_row_dict(row, source))
    return records


def iter_json_objects(value: object) -> Iterable[dict[str, object]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from iter_json_objects(nested)
    elif isinstance(value, list):
        for item in value:
            yield from iter_json_objects(item)


def parse_json_text(text: str, source: str) -> list[Record]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []

    records: list[Record] = []
    for obj in iter_json_objects(payload):
        string_values = [v for v in obj.values() if isinstance(v, str)]
        if not any(YOUTUBE_URL_RE.search(value) for value in string_values):
            continue

        candidate: dict[str, object] = dict(obj)
        tags = obj.get("tags")
        file_info = obj.get("file")
        if isinstance(tags, dict):
            for key, value in tags.items():
                candidate["tags_" + str(key)] = value
        if isinstance(file_info, dict):
            for key, value in file_info.items():
                candidate["file_" + str(key)] = value

        records.extend(extract_from_row_dict(candidate, source))
    return records


def parse_xml_text(text: str, source: str) -> list[Record]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []

    records: list[Record] = []
    for song in root.findall(".//Song"):
        row: dict[str, object] = dict(song.attrib)
        for child in song:
            if child.attrib:
                for key, value in child.attrib.items():
                    row[child.tag + "_" + key] = value
        if not any(YOUTUBE_URL_RE.search(str(value)) for value in row.values()):
            continue
        records.extend(extract_from_row_dict(row, source))
    return records


def parse_text_lines(text: str, source: str) -> list[Record]:
    records: list[Record] = []
    for line in text.splitlines():
        youtube_url = normalize_url(line)
        if not youtube_url:
            continue
        cleaned = normalize_space(line.replace(youtube_url, ""))
        artist, title = parse_artist_title_from_filename(cleaned)
        if not artist or not title:
            if " - " in cleaned:
                artist, title = [normalize_name(part) for part in cleaned.split(" - ", 1)]
            else:
                continue
        artist = normalize_name(artist)
        title = normalize_name(title)
        if artist and title:
            records.append(Record(artist=artist, title=title, youtube_url=youtube_url, source=source))
    return records


def parse_text_by_extension(text: str, ext: str, source: str) -> list[Record]:
    lower_ext = ext.lower()
    if lower_ext in {".csv", ".tsv"}:
        return parse_csv_text(text, source)
    if lower_ext == ".json":
        return parse_json_text(text, source)
    if lower_ext in {".xml", ".vdjfolder"}:
        return parse_xml_text(text, source)
    return parse_text_lines(text, source)


def parse_file(path: Path) -> list[Record]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return parse_text_by_extension(text, path.suffix, str(path))


def parse_zip_file(path: Path) -> list[Record]:
    records: list[Record] = []
    try:
        with ZipFile(path) as archive:
            for member in archive.namelist():
                member_path = Path(member)
                ext = member_path.suffix.lower()
                if ext not in TEXT_EXTENSIONS:
                    continue
                try:
                    raw = archive.read(member)
                except KeyError:
                    continue
                try:
                    text = raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                if not YOUTUBE_URL_RE.search(text):
                    continue
                source = str(path) + "::" + member
                records.extend(parse_text_by_extension(text, ext, source))
    except OSError:
        return []
    return records


def gather_records(roots: list[Path]) -> tuple[list[Record], Counter[str], list[str]]:
    text_candidates = rg_content_candidates(roots)
    zip_candidates = walk_priority_zip_candidates(roots)

    extracted: dict[tuple[str, str, str], Record] = {}
    source_counts: Counter[str] = Counter()
    missing_roots: list[str] = []

    for path in text_candidates:
        for record in parse_file(path):
            key = record_key(record.artist, record.title, record.youtube_url)
            if not all(key):
                continue
            if key not in extracted:
                extracted[key] = record
            source_counts[record.source] += 1

    for path in zip_candidates:
        for record in parse_zip_file(path):
            key = record_key(record.artist, record.title, record.youtube_url)
            if not all(key):
                continue
            if key not in extracted:
                extracted[key] = record
            source_counts[record.source] += 1

    requested = [
        str(Path.home() / "Documents"),
        str(Path.home() / "Downloads"),
        str(Path.home() / "Desktop"),
        str(Path.home() / "Sites"),
        "/Users/bobmbp/Documents/VDJ",
        "/Users/bobmbp/Documents/VDJ_XML_Tools",
        "/Users/bobmbp/Library/Mobile Documents",
    ]
    for path in requested:
        if not Path(path).exists():
            missing_roots.append(path)

    records = sorted(
        extracted.values(),
        key=lambda record: (record.artist, record.title, record.youtube_url),
    )
    return records, source_counts, missing_roots


def write_csv(records: list[Record], out_path: Path) -> None:
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["artist", "title", "youtube_url"])
        for record in records:
            writer.writerow([record.artist, record.title, record.youtube_url])


def main() -> int:
    roots = candidate_roots()
    records, source_counts, missing_roots = gather_records(roots)
    write_csv(records, OUT_PATH)

    print("WROTE", OUT_PATH)
    print("RECORDS", len(records))
    print("SOURCE_FILES", len(source_counts))
    if missing_roots:
        print("MISSING_ROOTS")
        for root in missing_roots:
            print(root)
    if source_counts:
        print("SOURCES_USED")
        for source, count in source_counts.most_common():
            print(f"{count}\t{source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
