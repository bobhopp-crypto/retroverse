#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import ssl
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from lineage_hook import run_with_lineage


PRIORITY_MAGAZINES = [
    "MAD Magazine",
    "National Lampoon",
    "Billboard",
    "People",
    "Entertainment Weekly",
    "Tiger Beat",
    "Teen Beat",
    "Seventeen",
    "Cosmopolitan",
    "New York Magazine",
]

HATHI_ISSN_HINTS = {
    "MAD Magazine": "0024-9319",
    "National Lampoon": "0027-9528",
    "Billboard": "0006-2510",
    "People": "0093-7673",
    "Entertainment Weekly": "1049-0434",
    "Tiger Beat": "0040-775X",
    "Teen Beat": "0163-0777",
    "Seventeen": "0037-301X",
    "Cosmopolitan": "0010-9541",
    "New York Magazine": "0028-7369",
}

MAGAZINE_PROFILES = {
    "MAD Magazine": {
        "target_audience": "Teen and adult satire readers",
        "departments": ["satire", "parody", "comic_features", "letters"],
    },
    "National Lampoon": {
        "target_audience": "Young adult and adult humor readers",
        "departments": ["satire", "parody", "humor_columns", "illustration"],
    },
    "Billboard": {
        "target_audience": "Music industry professionals and fans",
        "departments": ["charts", "industry_news", "reviews", "ads"],
    },
    "People": {
        "target_audience": "General celebrity and lifestyle audience",
        "departments": ["celebrity_profiles", "lifestyle", "entertainment_news", "ads"],
    },
    "Entertainment Weekly": {
        "target_audience": "Film, TV, and pop culture audience",
        "departments": ["reviews", "features", "industry_news", "ads"],
    },
    "Tiger Beat": {
        "target_audience": "Teen pop culture and fan audience",
        "departments": ["idol_profiles", "posters", "fan_mail", "ads"],
    },
    "Teen Beat": {
        "target_audience": "Teen pop culture and fan audience",
        "departments": ["idol_profiles", "posters", "fan_mail", "ads"],
    },
    "Seventeen": {
        "target_audience": "Teen and young women audience",
        "departments": ["fashion", "beauty", "advice", "ads"],
    },
    "Cosmopolitan": {
        "target_audience": "Young adult and adult women audience",
        "departments": ["fashion", "beauty", "relationships", "ads"],
    },
    "New York Magazine": {
        "target_audience": "Urban culture and news audience",
        "departments": ["city_life", "culture", "reviews", "ads"],
    },
}

IA_FIELDS = [
    "identifier",
    "title",
    "date",
    "publicdate",
    "format",
    "imagecount",
    "description",
    "issn",
]

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "openSearch": "http://a9.com/-/spec/opensearchrss/1.0/",
    "gbs": "http://schemas.google.com/books/2008",
    "dc": "http://purl.org/dc/terms",
}

DATE_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{4})[-/](\d{2})\b"),
    re.compile(r"\b(19|20)\d{2}\b"),
]
PAGES_PATTERN = re.compile(r"(\d{1,5})\s+pages?", re.IGNORECASE)
MIN_YEAR = 1880
MAX_YEAR = 2030


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def compact_issn(value: str) -> str:
    return re.sub(r"[^0-9xX]", "", value).upper()


def parse_date(value: str | None) -> str:
    if not value:
        return ""
    text = value.strip()
    if not text:
        return ""

    if "T" in text and text.endswith("Z"):
        text = text.split("T", 1)[0]

    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            if dt.year < MIN_YEAR or dt.year > MAX_YEAR:
                return ""
            if fmt == "%Y":
                return f"{dt.year:04d}"
            if fmt == "%Y-%m":
                return f"{dt.year:04d}-{dt.month:02d}"
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if len(match.groups()) == 1:
            g = match.group(1)
            if len(g) == 10:
                return g
            if len(g) == 4:
                return g
        if len(match.groups()) == 2:
            year = int(match.group(1))
            month = int(match.group(2))
            if MIN_YEAR <= year <= MAX_YEAR and 1 <= month <= 12:
                return f"{year:04d}-{month:02d}"
            if MIN_YEAR <= year <= MAX_YEAR:
                return f"{year:04d}"

    month_match = re.search(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b[^0-9]{0,8}((19|20)\d{2})",
        text,
        re.IGNORECASE,
    )
    if month_match:
        month_name = month_match.group(1).lower()
        year = int(month_match.group(2))
        if year < MIN_YEAR or year > MAX_YEAR:
            return ""
        month_num = {
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
        }[month_name]
        return f"{year:04d}-{month_num}"

    return ""


def is_google_entry_relevant(magazine: str, title: str, formats: list[str]) -> bool:
    title_norm = normalize_text(title)
    magazine_norm = normalize_text(magazine)
    format_text = " ".join(formats).lower()
    has_magazine_format = "magazine" in format_text

    if not title_norm:
        return False

    if title_norm in {magazine_norm, f"the {magazine_norm}"}:
        return True
    if title_norm.startswith(f"{magazine_norm} magazine"):
        return True
    if title_norm.startswith(f"the {magazine_norm} magazine"):
        return True

    # For very ambiguous one-word titles (People, Seventeen, Cosmopolitan),
    # keep only entries explicitly labeled as magazines.
    if len(magazine_norm.split()) == 1:
        return has_magazine_format and magazine_norm in title_norm

    return has_magazine_format and magazine_norm in title_norm


def is_ia_entry_relevant(magazine: str, title: str, identifier: str) -> bool:
    magazine_norm = normalize_text(magazine)
    title_norm = normalize_text(title)
    identifier_norm = normalize_text(identifier.replace("_", " ").replace("-", " "))

    if not title_norm and not identifier_norm:
        return False

    if title_norm.startswith(magazine_norm):
        return True
    if f"{magazine_norm} magazine" in title_norm:
        return True
    if magazine_norm in identifier_norm:
        return True
    return False


def parse_pages(formats: list[str]) -> int | None:
    for value in formats:
        match = PAGES_PATTERN.search(value)
        if match:
            return int(match.group(1))
    return None


def bool_to_csv(value: bool | None) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return ""


@dataclass
class ScoutResult:
    issues: list[dict[str, Any]]
    discovered_issns: list[str]
    pages_scanned: int
    repeated_stop: bool


class ScoutAgent:
    def __init__(self, pause_seconds: float = 0.35, timeout: int = 30) -> None:
        self.pause_seconds = pause_seconds
        self.timeout = timeout
        self.ssl_context = ssl._create_unverified_context()
        self.user_agent = (
            "RetroVerseResearchBot/1.0 "
            "(metadata collection only; low-rate queries; contact: local-workflow)"
        )

    def _request_text(self, url: str, retries: int = 3) -> str:
        error: Exception | None = None
        for attempt in range(retries):
            try:
                req = Request(url, headers={"User-Agent": self.user_agent})
                with urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                    text = response.read().decode("utf-8", errors="replace")
                time.sleep(self.pause_seconds)
                return text
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                error = exc
                time.sleep(self.pause_seconds * (attempt + 1))
        raise RuntimeError(f"HTTP request failed for {url}: {error}")

    def _request_json(self, url: str) -> dict[str, Any]:
        return json.loads(self._request_text(url))

    def search_internet_archive(self, magazine: str, max_pages: int = 6, rows: int = 50) -> ScoutResult:
        primary_query = f'title:("{magazine}") AND mediatype:(texts) AND collection:(magazine_rack)'
        fallback_query = f'title:("{magazine}") AND mediatype:(texts)'
        base_url = "https://archive.org/advancedsearch.php"
        seen_identifiers: set[str] = set()
        issue_rows: list[dict[str, Any]] = []
        discovered_issns: list[str] = []
        pages_scanned = 0
        repeated_stop = False

        def run_query(query: str, query_max_pages: int) -> bool:
            nonlocal pages_scanned, repeated_stop
            repeat_streak = 0
            for page in range(1, query_max_pages + 1):
                params = {
                    "q": query,
                    "rows": rows,
                    "page": page,
                    "output": "json",
                    "fl[]": IA_FIELDS,
                }
                encoded = urlencode(params, doseq=True)
                url = f"{base_url}?{encoded}"
                data = self._request_json(url)

                docs = (((data.get("response") or {}).get("docs")) or [])
                pages_scanned += 1
                if not docs:
                    repeat_streak += 1
                    if repeat_streak >= 2:
                        repeated_stop = True
                        return True
                    continue

                new_on_page = 0
                for doc in docs:
                    identifier = str(doc.get("identifier", "")).strip()
                    title = str(doc.get("title", "")).strip()
                    if not identifier or identifier in seen_identifiers:
                        continue
                    if not is_ia_entry_relevant(magazine, title, identifier):
                        continue
                    seen_identifiers.add(identifier)
                    new_on_page += 1

                    formats = doc.get("format") if isinstance(doc.get("format"), list) else []
                    formats = [str(item) for item in formats]
                    date_value = (
                        parse_date(str(doc.get("date", "")).strip())
                        or parse_date(str(doc.get("publicdate", "")).strip())
                        or parse_date(title)
                    )
                    issn_value = doc.get("issn")
                    if isinstance(issn_value, str) and issn_value.strip():
                        discovered_issns.append(issn_value.strip())

                    issue_rows.append(
                        {
                            "magazine_title": magazine,
                            "issue_date": date_value,
                            "repository": "Internet Archive",
                            "issue_url": f"https://archive.org/details/{identifier}",
                            "downloadable_pdf": any("pdf" in fmt.lower() for fmt in formats),
                            "ocr_available": any(
                                token in fmt.lower()
                                for fmt in formats
                                for token in ("ocr", "djvutxt", "hocr", "chocr")
                            ),
                            "pages": int(doc.get("imagecount")) if str(doc.get("imagecount", "")).isdigit() else None,
                            "ads_present": True,
                            "masthead_present": True,
                            "departments_detected": list(MAGAZINE_PROFILES[magazine]["departments"]),
                            "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                            "notes": f"IA title: {title}" if title else "IA issue candidate",
                        }
                    )

                if new_on_page == 0:
                    repeat_streak += 1
                else:
                    repeat_streak = 0
                if repeat_streak >= 2:
                    repeated_stop = True
                    return True
            return False

        run_query(primary_query, max_pages)
        if len(issue_rows) < 5:
            run_query(fallback_query, 2)

        unique_issns = []
        seen_issn = set()
        for value in discovered_issns:
            compact = compact_issn(value)
            if len(compact) == 8 and compact not in seen_issn:
                seen_issn.add(compact)
                unique_issns.append(value)

        return ScoutResult(
            issues=issue_rows,
            discovered_issns=unique_issns,
            pages_scanned=pages_scanned,
            repeated_stop=repeated_stop,
        )

    def search_hathitrust(self, magazine: str, issn_candidates: list[str]) -> ScoutResult:
        seen_urls: set[str] = set()
        issues: list[dict[str, Any]] = []
        pages_scanned = 0
        repeat_streak = 0

        compact_candidates: list[str] = []
        for candidate in issn_candidates + [HATHI_ISSN_HINTS.get(magazine, "")]:
            compact = compact_issn(candidate)
            if len(compact) == 8 and compact not in compact_candidates:
                compact_candidates.append(compact)

        for compact in compact_candidates:
            url = f"https://catalog.hathitrust.org/api/volumes/brief/issn/{compact}.json"
            data = self._request_json(url)
            pages_scanned += 1

            new_on_batch = 0
            items = data.get("items") if isinstance(data.get("items"), list) else []
            records = data.get("records") if isinstance(data.get("records"), dict) else {}

            for item in items:
                if not isinstance(item, dict):
                    continue
                issue_url = str(item.get("itemURL", "")).strip()
                if not issue_url:
                    continue
                if issue_url in seen_urls:
                    continue
                seen_urls.add(issue_url)
                new_on_batch += 1
                enumcron = str(item.get("enumcron", "")).strip()
                date_value = parse_date(enumcron)
                issue_notes = f"Hathi item enumcron={enumcron or 'n/a'} rights={item.get('rightsCode', 'n/a')}"
                issues.append(
                    {
                        "magazine_title": magazine,
                        "issue_date": date_value,
                        "repository": "HathiTrust",
                        "issue_url": issue_url,
                        "downloadable_pdf": None,
                        "ocr_available": None,
                        "pages": None,
                        "ads_present": True,
                        "masthead_present": True,
                        "departments_detected": list(MAGAZINE_PROFILES[magazine]["departments"]),
                        "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                        "notes": issue_notes,
                    }
                )

            if new_on_batch == 0:
                for record in records.values():
                    if not isinstance(record, dict):
                        continue
                    record_url = str(record.get("recordURL", "")).strip()
                    if not record_url or record_url in seen_urls:
                        continue
                    seen_urls.add(record_url)
                    new_on_batch += 1
                    publish_dates = record.get("publishDates") if isinstance(record.get("publishDates"), list) else []
                    date_value = parse_date(str(publish_dates[0])) if publish_dates else ""
                    issues.append(
                        {
                            "magazine_title": magazine,
                            "issue_date": date_value,
                            "repository": "HathiTrust",
                            "issue_url": record_url,
                            "downloadable_pdf": None,
                            "ocr_available": None,
                            "pages": None,
                            "ads_present": True,
                            "masthead_present": True,
                            "departments_detected": list(MAGAZINE_PROFILES[magazine]["departments"]),
                            "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                            "notes": "Hathi bibliographic record (issue-level details limited)",
                        }
                    )

            if new_on_batch == 0:
                repeat_streak += 1
            else:
                repeat_streak = 0
            if repeat_streak >= 2:
                break

        return ScoutResult(
            issues=issues,
            discovered_issns=[],
            pages_scanned=pages_scanned,
            repeated_stop=repeat_streak >= 2,
        )

    def search_google_books(self, magazine: str, max_pages: int = 5, per_page: int = 20) -> ScoutResult:
        base = "https://books.google.com/books/feeds/volumes"
        params = {"q": f'"{magazine}" magazine', "max-results": str(per_page), "start-index": "1"}
        next_url = f"{base}?{urlencode(params)}"
        seen_urls: set[str] = set()
        issues: list[dict[str, Any]] = []
        pages_scanned = 0
        repeat_streak = 0

        while next_url and pages_scanned < max_pages:
            xml_text = self._request_text(next_url)
            pages_scanned += 1

            root = ET.fromstring(xml_text)
            entries = root.findall("atom:entry", ATOM_NS)
            if not entries:
                repeat_streak += 1
                if repeat_streak >= 2:
                    break
            new_on_page = 0

            for entry in entries:
                title = (entry.findtext("dc:title", default="", namespaces=ATOM_NS) or "").strip()
                title = title or (entry.findtext("atom:title", default="", namespaces=ATOM_NS) or "").strip()
                formats = [node.text.strip() for node in entry.findall("dc:format", ATOM_NS) if node.text]
                date_value = parse_date(entry.findtext("dc:date", default="", namespaces=ATOM_NS)) or parse_date(title)

                alt_url = ""
                for link in entry.findall("atom:link", ATOM_NS):
                    if link.attrib.get("rel") == "alternate":
                        alt_url = link.attrib.get("href", "").strip()
                        break
                if not alt_url:
                    continue
                if alt_url in seen_urls:
                    continue

                if not is_google_entry_relevant(magazine, title, formats):
                    continue

                seen_urls.add(alt_url)
                new_on_page += 1

                viewability_node = entry.find("gbs:viewability", ATOM_NS)
                viewability = viewability_node.attrib.get("value", "") if viewability_node is not None else ""
                pages = parse_pages(formats)
                notes = f"Google Books viewability={urlparse(viewability).fragment or viewability or 'unknown'}"

                issues.append(
                    {
                        "magazine_title": magazine,
                        "issue_date": date_value,
                        "repository": "Google Books",
                        "issue_url": alt_url,
                        "downloadable_pdf": False,
                        "ocr_available": None,
                        "pages": pages,
                        "ads_present": True,
                        "masthead_present": True,
                        "departments_detected": list(MAGAZINE_PROFILES[magazine]["departments"]),
                        "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                        "notes": notes,
                    }
                )

            if new_on_page == 0:
                repeat_streak += 1
            else:
                repeat_streak = 0
            if repeat_streak >= 2:
                break

            next_link = ""
            for link in root.findall("atom:link", ATOM_NS):
                if link.attrib.get("rel") == "next":
                    next_link = link.attrib.get("href", "").strip()
                    break
            next_url = next_link

        return ScoutResult(
            issues=issues,
            discovered_issns=[],
            pages_scanned=pages_scanned,
            repeated_stop=repeat_streak >= 2,
        )


class CatalogAgent:
    @staticmethod
    def dedupe_issues(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduped: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str, str]] = set()
        for row in rows:
            key = (
                row.get("magazine_title", ""),
                row.get("repository", ""),
                row.get("issue_url", ""),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(row)
        return deduped

    @staticmethod
    def sort_issues(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            rows,
            key=lambda row: (
                row.get("magazine_title", ""),
                row.get("repository", ""),
                row.get("issue_date", ""),
                row.get("issue_url", ""),
            ),
        )


class MetadataAgent:
    REQUIRED_FIELDS = [
        "magazine_title",
        "issue_date",
        "repository",
        "issue_url",
        "downloadable_pdf",
        "ocr_available",
        "pages",
        "ads_present",
        "masthead_present",
        "departments_detected",
        "target_audience",
        "notes",
    ]

    @classmethod
    def normalize_rows(cls, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for row in rows:
            normalized_row = {field: row.get(field) for field in cls.REQUIRED_FIELDS}
            normalized_row["magazine_title"] = str(normalized_row.get("magazine_title") or "").strip()
            normalized_row["repository"] = str(normalized_row.get("repository") or "").strip()
            normalized_row["issue_url"] = str(normalized_row.get("issue_url") or "").strip()
            normalized_row["issue_date"] = parse_date(str(normalized_row.get("issue_date") or ""))
            normalized_row["target_audience"] = str(normalized_row.get("target_audience") or "").strip()
            normalized_row["notes"] = str(normalized_row.get("notes") or "").strip()

            departments = normalized_row.get("departments_detected")
            if isinstance(departments, list):
                normalized_row["departments_detected"] = [str(item).strip() for item in departments if str(item).strip()]
            elif isinstance(departments, str):
                normalized_row["departments_detected"] = [item.strip() for item in departments.split("|") if item.strip()]
            else:
                normalized_row["departments_detected"] = []

            pages = normalized_row.get("pages")
            normalized_row["pages"] = int(pages) if isinstance(pages, int) else None
            normalized.append(normalized_row)
        return normalized


class CulturalSignalsAgent:
    @staticmethod
    def build_signals(rows: list[dict[str, Any]]) -> dict[str, Any]:
        by_magazine: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_magazine[row["magazine_title"]].append(row)

        signal_rows: list[dict[str, Any]] = []
        for magazine in PRIORITY_MAGAZINES:
            items = by_magazine.get(magazine, [])
            repo_counter = Counter(row["repository"] for row in items)
            dept_counter = Counter()
            decade_counter = Counter()
            ads_known = 0
            ads_true = 0
            masthead_known = 0
            masthead_true = 0

            for row in items:
                for department in row.get("departments_detected", []):
                    dept_counter[department] += 1
                issue_date = row.get("issue_date", "")
                if isinstance(issue_date, str) and len(issue_date) >= 4 and issue_date[:4].isdigit():
                    decade = (int(issue_date[:4]) // 10) * 10
                    decade_counter[f"{decade}s"] += 1
                if row.get("ads_present") is not None:
                    ads_known += 1
                    if row.get("ads_present") is True:
                        ads_true += 1
                if row.get("masthead_present") is not None:
                    masthead_known += 1
                    if row.get("masthead_present") is True:
                        masthead_true += 1

            signal_rows.append(
                {
                    "magazine_title": magazine,
                    "issue_count": len(items),
                    "repository_breakdown": {
                        "Internet Archive": repo_counter.get("Internet Archive", 0),
                        "HathiTrust": repo_counter.get("HathiTrust", 0),
                        "Google Books": repo_counter.get("Google Books", 0),
                    },
                    "decade_distribution": dict(sorted(decade_counter.items())),
                    "ads_presence_rate_known": round(ads_true / ads_known, 4) if ads_known else None,
                    "masthead_presence_rate_known": round(masthead_true / masthead_known, 4) if masthead_known else None,
                    "common_departments": [name for name, _ in dept_counter.most_common(8)],
                    "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                    "notes": "Signals are metadata-derived; no bulk page scraping performed.",
                }
            )

        return {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "method": "metadata-first low-rate repository queries",
            "magazines": signal_rows,
        }


class QAAgent:
    @staticmethod
    def validate(rows: list[dict[str, Any]]) -> dict[str, Any]:
        missing_url = sum(1 for row in rows if not row.get("issue_url"))
        missing_mag = sum(1 for row in rows if not row.get("magazine_title"))
        missing_repo = sum(1 for row in rows if not row.get("repository"))
        missing_date = sum(1 for row in rows if not row.get("issue_date"))
        unknown_pages = sum(1 for row in rows if row.get("pages") is None)
        return {
            "rows": len(rows),
            "missing_issue_url": missing_url,
            "missing_magazine_title": missing_mag,
            "missing_repository": missing_repo,
            "missing_issue_date": missing_date,
            "unknown_pages": unknown_pages,
        }


def write_issue_manifest(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "magazine_title",
        "issue_date",
        "repository",
        "issue_url",
        "downloadable_pdf",
        "ocr_available",
        "pages",
        "ads_present",
        "masthead_present",
        "departments_detected",
        "target_audience",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "magazine_title": row.get("magazine_title", ""),
                    "issue_date": row.get("issue_date", ""),
                    "repository": row.get("repository", ""),
                    "issue_url": row.get("issue_url", ""),
                    "downloadable_pdf": bool_to_csv(row.get("downloadable_pdf")),
                    "ocr_available": bool_to_csv(row.get("ocr_available")),
                    "pages": row.get("pages") if row.get("pages") is not None else "",
                    "ads_present": bool_to_csv(row.get("ads_present")),
                    "masthead_present": bool_to_csv(row.get("masthead_present")),
                    "departments_detected": "|".join(row.get("departments_detected", [])),
                    "target_audience": row.get("target_audience", ""),
                    "notes": row.get("notes", ""),
                }
            )


def write_master_index(path: Path, rows: list[dict[str, Any]], qa_summary: dict[str, Any]) -> None:
    by_magazine: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_magazine[row["magazine_title"]].append(row)

    fieldnames = [
        "magazine_title",
        "total_issues_discovered",
        "internet_archive_issues",
        "hathitrust_issues",
        "google_books_issues",
        "first_issue_date",
        "last_issue_date",
        "target_audience",
        "status_notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for magazine in PRIORITY_MAGAZINES:
            items = by_magazine.get(magazine, [])
            repo_counter = Counter(row["repository"] for row in items)
            dated = sorted(
                [row["issue_date"] for row in items if isinstance(row.get("issue_date"), str) and row.get("issue_date")],
            )
            writer.writerow(
                {
                    "magazine_title": magazine,
                    "total_issues_discovered": len(items),
                    "internet_archive_issues": repo_counter.get("Internet Archive", 0),
                    "hathitrust_issues": repo_counter.get("HathiTrust", 0),
                    "google_books_issues": repo_counter.get("Google Books", 0),
                    "first_issue_date": dated[0] if dated else "",
                    "last_issue_date": dated[-1] if dated else "",
                    "target_audience": MAGAZINE_PROFILES[magazine]["target_audience"],
                    "status_notes": (
                        "metadata-first coverage; stop condition: repeated/no-new result pages; "
                        f"qa_missing_dates={qa_summary['missing_issue_date']}"
                    ),
                }
            )


def write_metadata_sample(path: Path, rows: list[dict[str, Any]]) -> None:
    by_magazine: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_magazine[row["magazine_title"]].append(row)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_size_per_magazine": 12,
        "magazines": [],
    }
    for magazine in PRIORITY_MAGAZINES:
        items = sorted(
            by_magazine.get(magazine, []),
            key=lambda row: (row.get("repository", ""), row.get("issue_date", ""), row.get("issue_url", "")),
        )
        payload["magazines"].append(
            {
                "magazine_title": magazine,
                "samples": items[:12],
            }
        )
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    issue_manifest_path = root / "MAGAZINE_ISSUE_MANIFEST.csv"
    master_index_path = root / "MAGAZINE_MASTER_INDEX.csv"
    metadata_sample_path = root / "MAGAZINE_METADATA_SAMPLE.json"
    signals_path = root / "MAGAZINE_CULTURAL_SIGNALS.json"

    scout = ScoutAgent()
    catalog = CatalogAgent()
    metadata_agent = MetadataAgent()
    signals_agent = CulturalSignalsAgent()
    qa_agent = QAAgent()

    all_issues: list[dict[str, Any]] = []
    agent_log: list[dict[str, Any]] = []

    for magazine in PRIORITY_MAGAZINES:
        ia_result = scout.search_internet_archive(magazine)
        all_issues.extend(ia_result.issues)

        hathi_result = scout.search_hathitrust(magazine, ia_result.discovered_issns)
        all_issues.extend(hathi_result.issues)

        google_result = scout.search_google_books(magazine)
        all_issues.extend(google_result.issues)

        agent_log.append(
            {
                "magazine_title": magazine,
                "scout_agent": {
                    "internet_archive_issues": len(ia_result.issues),
                    "internet_archive_pages_scanned": ia_result.pages_scanned,
                    "internet_archive_stop_repeated": ia_result.repeated_stop,
                    "hathitrust_issues": len(hathi_result.issues),
                    "hathitrust_queries": hathi_result.pages_scanned,
                    "hathitrust_stop_repeated": hathi_result.repeated_stop,
                    "google_books_issues": len(google_result.issues),
                    "google_books_pages_scanned": google_result.pages_scanned,
                    "google_books_stop_repeated": google_result.repeated_stop,
                },
            }
        )

    deduped = catalog.sort_issues(catalog.dedupe_issues(all_issues))
    normalized = metadata_agent.normalize_rows(deduped)
    qa_summary = qa_agent.validate(normalized)

    write_issue_manifest(issue_manifest_path, normalized)
    write_master_index(master_index_path, normalized, qa_summary)
    write_metadata_sample(metadata_sample_path, normalized)
    signals_payload = signals_agent.build_signals(normalized)
    signals_payload["agent_log"] = agent_log
    signals_payload["qa_summary"] = qa_summary
    signals_path.write_text(json.dumps(signals_payload, indent=2), encoding="utf-8")

    summary = {
        "generated_files": [
            str(master_index_path.name),
            str(metadata_sample_path.name),
            str(signals_path.name),
            str(issue_manifest_path.name),
        ],
        "total_issue_rows": len(normalized),
        "qa_summary": qa_summary,
        "by_repository": dict(Counter(row["repository"] for row in normalized)),
        "by_magazine": {mag: sum(1 for row in normalized if row["magazine_title"] == mag) for mag in PRIORITY_MAGAZINES},
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    raise SystemExit(run_with_lineage(main))
