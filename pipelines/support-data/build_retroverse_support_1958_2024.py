#!/usr/bin/env python3
"""Build RetroVerse support CSV with films, TV, and headlines for 1958-2024."""

from __future__ import annotations

import argparse
import csv
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from registry_loader import get_dataset_path

DEFAULT_START_YEAR = 1958
DEFAULT_END_YEAR = 2024
DEFAULT_OUT_PATH = get_dataset_path(
    "retroverse_support_cultural",
    fallback="data/support/retroverse/retroverse_support_cultural_1958_2024_top10.csv",
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36 RetroVerseDataBuilder/1.0"
)

RETRYABLE_STATUSES = {429, 500, 502, 503, 504}

CITATION_RE = re.compile(r"\[[^\]]+\]")
SEASON_LINK_RE = re.compile(
    r"/wiki/(\d{4})%E2%80%93(\d{2,4})_United_States_network_television_schedule"
)

FILM_COLUMNS = [f"top_film_{idx}" for idx in range(1, 11)]
TV_COLUMNS = [f"top_tv_program_{idx}" for idx in range(1, 11)]
HEADLINE_EVENT_COLUMNS = [f"headline_event_{idx}" for idx in range(1, 16)]
CSV_COLUMNS = ["year"] + FILM_COLUMNS + TV_COLUMNS + HEADLINE_EVENT_COLUMNS
FILM_TARGET_COUNT = 10
TV_TARGET_COUNT = 10
HEADLINE_TARGET_COUNT = 15
HEADLINE_MIN_REQUIRED = 10

try:
    import lxml  # noqa: F401

    BS_PARSER = "lxml"
except Exception:  # noqa: BLE001
    BS_PARSER = "html.parser"


class NonRetryableHttpError(RuntimeError):
    """HTTP status that should not be retried."""


class HttpClient:
    def __init__(
        self,
        logger: logging.Logger,
        rate_limit_seconds: float = 0.6,
        timeout_seconds: int = 30,
        max_retries: int = 5,
    ) -> None:
        self.logger = logger
        self.rate_limit_seconds = max(rate_limit_seconds, 0.0)
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.last_request_ts = 0.0
        self.use_curl_only = False
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def close(self) -> None:
        self.session.close()

    def _sleep_for_rate_limit(self) -> None:
        if self.rate_limit_seconds <= 0:
            return
        elapsed = time.time() - self.last_request_ts
        remaining = self.rate_limit_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    def _curl_get(self, url: str) -> str:
        self._sleep_for_rate_limit()
        completed = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "curl",
                "-L",
                "-sS",
                "-A",
                USER_AGENT,
                url,
            ],
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds + 20,
            check=True,
        )
        self.last_request_ts = time.time()
        return completed.stdout

    def _get_via_curl_with_retries(self, url: str) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._curl_get(url)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= self.max_retries:
                    break
                delay = min(30.0, float(2 ** (attempt - 1)))
                self.logger.warning(
                    "curl request failed (attempt %d/%d): %s [%s]; retrying in %.1fs",
                    attempt,
                    self.max_retries,
                    url,
                    exc,
                    delay,
                )
                time.sleep(delay)

        raise RuntimeError(
            f"curl request failed after {self.max_retries} attempts for {url}: {last_error}"
        )

    def get(self, url: str) -> str:
        if self.use_curl_only:
            return self._get_via_curl_with_retries(url)

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            self._sleep_for_rate_limit()
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
                self.last_request_ts = time.time()
                if response.status_code == 200:
                    return response.text
                if response.status_code in RETRYABLE_STATUSES:
                    raise RuntimeError(f"retryable status {response.status_code}")
                raise NonRetryableHttpError(f"HTTP {response.status_code}")
            except NonRetryableHttpError as exc:
                raise RuntimeError(str(exc)) from exc
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                message = str(exc)
                if "Failed to resolve" in message or "NameResolutionError" in message:
                    self.use_curl_only = True
                    self.logger.warning(
                        "Switching HTTP fetches to curl fallback due to DNS resolution failure in requests"
                    )
                    return self._get_via_curl_with_retries(url)
                if attempt >= self.max_retries:
                    break
                delay = min(30.0, float(2 ** (attempt - 1)))
                self.logger.warning(
                    "Request failed (attempt %d/%d): %s [%s]; retrying in %.1fs",
                    attempt,
                    self.max_retries,
                    url,
                    exc,
                    delay,
                )
                time.sleep(delay)

        raise RuntimeError(
            f"Request failed after {self.max_retries} attempts for {url}: {last_error}"
        )


def clean_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = CITATION_RE.sub("", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def article_content_root(soup: BeautifulSoup) -> Tag:
    selectors = [
        "#mw-content-text .mw-parser-output",
        "#bodyContent #mw-content-text .mw-parser-output",
        "main#content #mw-content-text .mw-parser-output",
    ]
    candidates: List[Tag] = []
    for selector in selectors:
        candidates.extend(soup.select(selector))

    if not candidates:
        candidates = soup.select("div.mw-parser-output")

    if candidates:
        return max(candidates, key=lambda node: len(node.get_text(" ", strip=True)))

    return soup


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, BS_PARSER)


def header_index(headers: List[str], keywords: Tuple[str, ...]) -> Optional[int]:
    for idx, header in enumerate(headers):
        if any(keyword in header for keyword in keywords):
            return idx
    return None


def parse_ranked_table_values(
    table: Tag,
    value_header_keywords: Tuple[str, ...],
    rank_header_keywords: Tuple[str, ...] = ("rank", "no", "no."),
    min_required: int = 10,
) -> List[str]:
    rows = table.find_all("tr")
    if not rows:
        return []

    header_row_idx: Optional[int] = None
    header_cells: List[Tag] = []
    for row_idx, row in enumerate(rows):
        th_cells = row.find_all("th", recursive=False)
        if th_cells:
            header_row_idx = row_idx
            header_cells = th_cells
            break

    if header_row_idx is None:
        return []

    headers = [clean_text(cell.get_text(" ", strip=True)).lower() for cell in header_cells]
    value_idx = header_index(headers, value_header_keywords)
    rank_idx = header_index(headers, rank_header_keywords)
    if value_idx is None:
        return []

    extracted: List[str] = []
    current_rank: Optional[int] = None
    header_count = len(headers)

    for row in rows[header_row_idx + 1 :]:
        cells = row.find_all(["td", "th"], recursive=False)
        if not cells:
            continue

        row_value_idx = value_idx
        if rank_idx is not None and rank_idx < len(cells):
            rank_text = clean_text(cells[rank_idx].get_text(" ", strip=True))
            rank_match = re.match(r"^(\d+)", rank_text)
            if rank_match:
                current_rank = int(rank_match.group(1))
            elif (
                rank_idx < value_idx
                and len(cells) == max(1, header_count - 1)
                and row_value_idx > 0
            ):
                # Rank cell is omitted due to rowspan, so the value column shifts left.
                row_value_idx -= 1
        elif rank_idx is not None and rank_idx < value_idx and len(cells) == max(1, header_count - 1):
            row_value_idx = max(0, row_value_idx - 1)

        if row_value_idx >= len(cells):
            continue

        value = clean_text(cells[row_value_idx].get_text(" ", strip=True))
        if not value:
            continue

        if current_rank is not None and current_rank > 10 and len(extracted) >= min_required:
            break

        if value not in extracted:
            extracted.append(value)

        if len(extracted) >= min_required:
            break

    return extracted


def fetch_films_from_box_office_mojo(client: HttpClient, year: int) -> List[str]:
    url = f"https://www.boxofficemojo.com/year/{year}/?grossesOption=totalGrosses"
    html = client.get(url)
    if "Error - Box Office Mojo" in html or "The requested page was not found." in html:
        raise RuntimeError("Box Office Mojo page unavailable for this year")
    soup = make_soup(html)
    table = soup.select_one("table.mojo-body-table")
    if table is None:
        raise RuntimeError("Missing Box Office Mojo table")

    films: List[str] = []
    for row in table.find_all("tr"):
        release_cell = row.select_one("td.mojo-field-type-release")
        if release_cell is None:
            continue
        title = clean_text(release_cell.get_text(" ", strip=True))
        if title:
            films.append(title)
        if len(films) >= 10:
            break

    if len(films) < 10:
        raise RuntimeError(f"Only found {len(films)} films on Box Office Mojo")

    return films[:10]


def fetch_films_from_wikipedia_year_in_film(client: HttpClient, year: int) -> List[str]:
    url = f"https://en.wikipedia.org/wiki/{year}_in_film"
    html = client.get(url)
    soup = make_soup(html)

    tables = soup.select("table.wikitable")
    if not tables:
        raise RuntimeError("No wikitable entries found on year-in-film page")

    strict_candidates: List[Tag] = []
    for table in tables:
        caption_text = clean_text(table.caption.get_text(" ", strip=True)).lower() if table.caption else ""
        header_row = None
        for row in table.find_all("tr"):
            th_cells = row.find_all("th", recursive=False)
            if th_cells:
                header_row = th_cells
                break
        headers = [clean_text(th.get_text(" ", strip=True)).lower() for th in (header_row or [])]
        combined = " ".join([caption_text] + headers)
        has_rank = "rank" in combined or "no." in combined or "no" in combined
        has_title = any(word in combined for word in ("title", "film", "movie"))
        has_gross = any(word in combined for word in ("gross", "box office", "domestic", "rental"))
        if has_rank and has_title and has_gross:
            strict_candidates.append(table)

    for table in strict_candidates:
        films = parse_ranked_table_values(
            table,
            value_header_keywords=("title", "film", "movie"),
            min_required=10,
        )
        if len(films) >= 10:
            return films[:10]

    for table in tables:
        films = parse_ranked_table_values(
            table,
            value_header_keywords=("title", "film", "movie"),
            min_required=10,
        )
        if len(films) >= 10:
            return films[:10]

    raise RuntimeError("Could not find a top-grossing films table with 10 titles")


def fetch_films_for_year(client: HttpClient, year: int, logger: logging.Logger) -> Tuple[List[str], str]:
    try:
        films = fetch_films_from_box_office_mojo(client, year)
        return films, "boxofficemojo"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Films primary source failed for %d: %s", year, exc)

    films = fetch_films_from_wikipedia_year_in_film(client, year)
    return films, "wikipedia-year-in-film"


def parse_tv_program_table(table: Tag) -> List[str]:
    return parse_ranked_table_values(
        table,
        value_header_keywords=("program", "show"),
        min_required=10,
    )


def build_tv_season_map_from_primary_page(html: str) -> Dict[int, List[str]]:
    soup = make_soup(html)
    content = article_content_root(soup)

    mapping: Dict[int, List[str]] = {}
    current_start_year: Optional[int] = None

    for node in content.find_all(["a", "table"]):
        if node.name == "a":
            href = node.get("href", "")
            match = SEASON_LINK_RE.search(href)
            if match:
                current_start_year = int(match.group(1))
            continue

        programs = parse_tv_program_table(node)
        if current_start_year is None or len(programs) < 10:
            continue
        if current_start_year not in mapping:
            mapping[current_start_year] = programs[:10]

    return mapping


def fetch_tv_season_map_primary(client: HttpClient) -> Dict[int, List[str]]:
    url = "https://en.wikipedia.org/wiki/Top-rated_United_States_television_programs_by_season"
    html = client.get(url)
    mapping = build_tv_season_map_from_primary_page(html)
    if not mapping:
        raise RuntimeError("Failed to build TV season map from primary source")
    return mapping


def season_page_urls(year: int) -> Iterable[str]:
    next_year = year + 1
    yy = f"{next_year % 100:02d}"
    yield f"https://en.wikipedia.org/wiki/{year}%E2%80%93{yy}_United_States_network_television_schedule"
    yield f"https://en.wikipedia.org/wiki/{year}%E2%80%93{next_year}_United_States_network_television_schedule"


def fetch_tv_programs_from_season_page(client: HttpClient, year: int) -> List[str]:
    last_error: Optional[Exception] = None

    for url in season_page_urls(year):
        try:
            html = client.get(url)
            soup = make_soup(html)
            for table in soup.select("table.wikitable"):
                programs = parse_tv_program_table(table)
                if len(programs) >= 10:
                    return programs[:10]
            last_error = RuntimeError(f"No top-rated table found on {url}")
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise RuntimeError(f"TV fallback failed for {year}: {last_error}")


def normalize_event_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_text(text).lower())


def dedupe_text_candidates(items: List[str]) -> List[str]:
    deduped: List[str] = []
    seen: set[str] = set()
    for item in items:
        key = normalize_event_key(item)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(clean_text(item))
    return deduped


def take_unique_candidates(
    selected: List[str],
    candidates: List[str],
    used_keys: set[str],
    limit: int,
) -> None:
    for candidate in candidates:
        if len(selected) >= limit:
            break
        key = normalize_event_key(candidate)
        if not key or key in used_keys:
            continue
        used_keys.add(key)
        selected.append(clean_text(candidate))


NOISE_PREFIXES = (
    "read more",
    "watch:",
    "video:",
    "photos:",
    "listen:",
    "advertisement",
    "newsletter",
)
AWARD_TOKENS = ("awards", "award winners", "nominations", "nominees")


def normalize_headline_text(text: str) -> str:
    normalized = clean_text(text)
    normalized = re.sub(r"^\s*(?:#|no\.?\s*)?\d{1,2}[\)\].:\- ]+\s*", "", normalized, flags=re.IGNORECASE)
    for sep in (" — ", " – ", " - "):
        if sep not in normalized:
            continue
        head, tail = normalized.split(sep, 1)
        if len(head) >= 12 and len(tail) >= 20:
            normalized = clean_text(head)
            break
    if ": " in normalized:
        head, tail = normalized.split(": ", 1)
        if len(head) >= 12 and len(tail) >= 40:
            normalized = clean_text(head)
    return normalized


def is_valid_editorial_headline(text: str) -> bool:
    normalized = normalize_headline_text(text)
    if len(normalized) < 12 or len(normalized) > 220:
        return False

    lower = normalized.lower()
    if lower.startswith(NOISE_PREFIXES):
        return False
    if any(token in lower for token in AWARD_TOKENS):
        return False
    if "newsletter" in lower or "sign up" in lower:
        return False
    if re.fullmatch(r"[\d\W]+", normalized):
        return False

    words = normalized.split()
    if len(words) < 3:
        return False

    if normalized.count(".") > 1:
        return False
    return True


def extract_structured_headline_items(soup: BeautifulSoup) -> List[str]:
    root = soup.select_one("main") or article_content_root(soup)
    candidates: List[str] = []

    for li in root.select("ol li, ul li"):
        if li.find_parent(["nav", "header", "footer", "aside"]):
            continue
        text = normalize_headline_text(li.get_text(" ", strip=True))
        if is_valid_editorial_headline(text):
            candidates.append(text)

    if len(candidates) < HEADLINE_TARGET_COUNT:
        for node in root.select("article h2, article h3, h2 a, h3 a, li a"):
            text = normalize_headline_text(node.get_text(" ", strip=True))
            if is_valid_editorial_headline(text):
                candidates.append(text)

    return dedupe_text_candidates(candidates)


def fetch_ap_top_stories(client: HttpClient, year: int, max_items: int = 10) -> List[str]:
    urls = [
        f"https://apnews.com/hub/{year}-year-in-review",
        "https://apnews.com/hub/year-in-review",
        f"https://apnews.com/search?q=Associated%20Press%20Top%20Stories%20of%20{year}",
        f"https://apnews.com/search?q=Top%20Stories%20of%20{year}",
    ]
    selected: List[str] = []
    used_keys: set[str] = set()

    for url in urls:
        try:
            html = client.get(url)
        except Exception:  # noqa: BLE001
            continue
        soup = make_soup(html)
        candidates = extract_structured_headline_items(soup)
        take_unique_candidates(selected, candidates, used_keys, max_items)
        if len(selected) >= max_items:
            break

    return selected[:max_items]


def find_britannica_year_in_review_url(client: HttpClient, year: int) -> Optional[str]:
    search_urls = [
        f"https://www.britannica.com/search?query=Year%20in%20Review%20{year}",
        f"https://www.britannica.com/search?query={year}%20year%20in%20review",
    ]
    for search_url in search_urls:
        try:
            html = client.get(search_url)
        except Exception:  # noqa: BLE001
            continue
        soup = make_soup(html)
        for anchor in soup.select("a[href]"):
            href = clean_text(anchor.get("href", ""))
            text = clean_text(anchor.get_text(" ", strip=True)).lower()
            href_lower = href.lower()
            if "/topic/" not in href_lower:
                continue
            if str(year) not in href_lower and str(year) not in text:
                continue
            if "review" not in href_lower and "review" not in text:
                continue
            if href.startswith("/"):
                href = f"https://www.britannica.com{href}"
            return href
    return None


def fetch_britannica_year_in_review_items(
    client: HttpClient,
    year: int,
    max_items: int = HEADLINE_TARGET_COUNT,
) -> List[str]:
    page_url = find_britannica_year_in_review_url(client, year)
    if not page_url:
        return []

    try:
        html = client.get(page_url)
    except Exception:  # noqa: BLE001
        return []
    soup = make_soup(html)
    candidates = extract_structured_headline_items(soup)
    return candidates[:max_items]


def fetch_reuters_year_in_review_items(
    client: HttpClient,
    year: int,
    max_items: int = HEADLINE_TARGET_COUNT,
) -> List[str]:
    urls = [
        f"https://www.reuters.com/world/year-in-review/{year}/",
        "https://www.reuters.com/world/year-in-review/",
        f"https://www.reuters.com/site-search/?query=year+in+review+{year}",
    ]
    selected: List[str] = []
    used_keys: set[str] = set()
    for url in urls:
        try:
            html = client.get(url)
        except Exception:  # noqa: BLE001
            continue
        lower_html = html.lower()
        if "please enable js" in lower_html or "captcha" in lower_html:
            continue
        soup = make_soup(html)
        candidates = extract_structured_headline_items(soup)
        take_unique_candidates(selected, candidates, used_keys, max_items)
        if len(selected) >= max_items:
            break
    return selected[:max_items]


def fetch_headlines_for_year(
    client: HttpClient,
    year: int,
    logger: logging.Logger,
) -> List[str]:
    selected: List[str] = []
    used_keys: set[str] = set()

    ap_events = fetch_ap_top_stories(client, year, max_items=10)
    take_unique_candidates(selected, ap_events, used_keys, HEADLINE_TARGET_COUNT)

    if len(selected) < HEADLINE_TARGET_COUNT:
        britannica_events = fetch_britannica_year_in_review_items(
            client,
            year,
            max_items=HEADLINE_TARGET_COUNT,
        )
        take_unique_candidates(selected, britannica_events, used_keys, HEADLINE_TARGET_COUNT)

    if len(selected) < HEADLINE_TARGET_COUNT:
        reuters_events = fetch_reuters_year_in_review_items(
            client,
            year,
            max_items=HEADLINE_TARGET_COUNT,
        )
        take_unique_candidates(selected, reuters_events, used_keys, HEADLINE_TARGET_COUNT)

    if len(selected) < 10:
        logger.warning("Year %d editorial events below minimum: %d", year, len(selected))

    logger.info("Year %d editorial events collected: %d", year, len(selected))
    return selected[:HEADLINE_TARGET_COUNT]


def setup_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("retroverse_support_builder")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    return logger


def row_complete(row: Dict[str, str]) -> bool:
    expected_by_group = (
        (FILM_COLUMNS, FILM_TARGET_COUNT),
        (TV_COLUMNS, TV_TARGET_COUNT),
        (HEADLINE_EVENT_COLUMNS, HEADLINE_TARGET_COUNT),
    )
    for col_group, expected in expected_by_group:
        if sum(1 for col in col_group if clean_text(row.get(col, ""))) != expected:
            return False
    return True


def load_existing_rows(path: Path, logger: logging.Logger) -> Dict[int, Dict[str, str]]:
    if not path.exists():
        return {}

    rows: Dict[int, Dict[str, str]] = {}
    with path.open("r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for incoming in reader:
            year_text = clean_text(incoming.get("year", ""))
            if not year_text.isdigit():
                continue
            year = int(year_text)
            row = {column: clean_text(incoming.get(column, "")) for column in CSV_COLUMNS}
            row["year"] = str(year)
            rows[year] = row

    logger.info("Loaded %d existing rows from %s", len(rows), path)
    return rows


def build_row(
    year: int,
    films: List[str],
    tv_programs: List[str],
    headline_events: List[str],
) -> Dict[str, str]:
    row: Dict[str, str] = {"year": str(year)}
    for idx, col in enumerate(FILM_COLUMNS):
        row[col] = clean_text(films[idx]) if idx < len(films) else ""
    for idx, col in enumerate(TV_COLUMNS):
        row[col] = clean_text(tv_programs[idx]) if idx < len(tv_programs) else ""
    for idx, col in enumerate(HEADLINE_EVENT_COLUMNS):
        row[col] = clean_text(headline_events[idx]) if idx < len(headline_events) else ""
    return row


def write_rows(path: Path, rows: Dict[int, Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for year in sorted(rows):
            row = rows[year]
            normalized = {column: clean_text(row.get(column, "")) for column in CSV_COLUMNS}
            normalized["year"] = str(year)
            writer.writerow(normalized)


def non_empty_count(row: Dict[str, str], columns: List[str]) -> int:
    return sum(1 for col in columns if clean_text(row.get(col, "")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate RetroVerse support CSV (films, TV, headlines) for one row per year."
        )
    )
    parser.add_argument("--start", type=int, default=DEFAULT_START_YEAR, help="Start year (default: 1958)")
    parser.add_argument("--end", type=int, default=DEFAULT_END_YEAR, help="End year (default: 2024)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute requested years even when already complete in output CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_PATH,
        help=f"Output CSV path (default: {DEFAULT_OUT_PATH})",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Log file path (default: alongside output CSV with .log extension)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.6,
        help="Minimum seconds between HTTP requests (default: 0.6)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run minimal sanity range 1958-1960 and print short count summary",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.smoke:
        start_year = 1958
        end_year = 1960
    else:
        start_year = args.start
        end_year = args.end

    if start_year > end_year:
        print("--start must be less than or equal to --end", file=sys.stderr)
        return 2

    out_path = args.out.expanduser().resolve()
    log_path = args.log.expanduser().resolve() if args.log else out_path.with_suffix(".log")
    logger = setup_logger(log_path)

    logger.info("Output CSV: %s", out_path)
    logger.info("Log file: %s", log_path)
    logger.info("Year range: %d-%d", start_year, end_year)
    logger.info("Rate limit: %.2fs", args.rate_limit)
    logger.info("Force mode: %s", args.force)
    logger.info("Smoke mode: %s", args.smoke)

    existing_rows = load_existing_rows(out_path, logger)
    failures: List[Tuple[int, List[str]]] = []

    client = HttpClient(logger=logger, rate_limit_seconds=args.rate_limit)
    tv_map_cache: Dict[int, List[str]] = {}

    try:
        for year in range(start_year, end_year + 1):
            if not args.force and year in existing_rows and row_complete(existing_rows[year]):
                logger.info("Skipping %d (already complete)", year)
                continue

            logger.info("Processing %d", year)

            films: List[str] = []
            tv_programs: List[str] = []
            headline_events: List[str] = []
            year_errors: List[str] = []

            try:
                films, film_source = fetch_films_for_year(client, year, logger)
                logger.info("%d films from %s for %d", len(films), film_source, year)
            except Exception as exc:  # noqa: BLE001
                year_errors.append(f"films: {exc}")

            try:
                if not tv_map_cache:
                    tv_map_cache = fetch_tv_season_map_primary(client)
                    logger.info("Loaded TV season map with %d seasons", len(tv_map_cache))

                if year in tv_map_cache and len(tv_map_cache[year]) >= 10:
                    tv_programs = tv_map_cache[year][:10]
                    logger.info("%d TV programs from primary map for %d", len(tv_programs), year)
                else:
                    tv_programs = fetch_tv_programs_from_season_page(client, year)
                    tv_map_cache[year] = tv_programs[:10]
                    logger.info("%d TV programs from fallback season page for %d", len(tv_programs), year)
            except Exception as exc:  # noqa: BLE001
                year_errors.append(f"tv: {exc}")

            try:
                headline_events = fetch_headlines_for_year(client, year, logger)
                logger.info("%d headlines for %d", len(headline_events), year)
            except Exception as exc:  # noqa: BLE001
                year_errors.append(f"headlines: {exc}")

            films = films[:FILM_TARGET_COUNT]
            tv_programs = tv_programs[:TV_TARGET_COUNT]
            headline_events = headline_events[:HEADLINE_TARGET_COUNT]

            if len(films) != FILM_TARGET_COUNT:
                year_errors.append(f"films_count={len(films)}")
            if len(tv_programs) != TV_TARGET_COUNT:
                year_errors.append(f"tv_count={len(tv_programs)}")
            if len(headline_events) < HEADLINE_MIN_REQUIRED:
                logger.warning("Year %d headline count below minimum: %d", year, len(headline_events))

            new_row = build_row(year, films, tv_programs, headline_events)

            if year_errors:
                failures.append((year, year_errors))
                if year in existing_rows and row_complete(existing_rows[year]):
                    logger.error(
                        "Year %d failed (%s). Keeping existing complete row.",
                        year,
                        " | ".join(year_errors),
                    )
                else:
                    existing_rows[year] = new_row
                    logger.error("Year %d failed: %s", year, " | ".join(year_errors))
            else:
                existing_rows[year] = new_row
                logger.info("Year %d complete", year)

            write_rows(out_path, existing_rows)
            logger.info("Progress written to %s", out_path)
    finally:
        client.close()

    if args.smoke:
        logger.info("Smoke summary:")
        smoke_ok = True
        for year in range(1958, 1961):
            row = existing_rows.get(year, {})
            film_count = non_empty_count(row, FILM_COLUMNS)
            tv_count = non_empty_count(row, TV_COLUMNS)
            event_count = non_empty_count(row, HEADLINE_EVENT_COLUMNS)
            logger.info("  %d: films=%d tv=%d headlines=%d", year, film_count, tv_count, event_count)
            if (
                film_count != FILM_TARGET_COUNT
                or tv_count != TV_TARGET_COUNT
                or event_count < HEADLINE_MIN_REQUIRED
            ):
                smoke_ok = False
        if smoke_ok and not failures:
            print("SMOKE OK: all years 1958-1960 have 10 films, 10 TV programs, and at least 10 headlines")
        else:
            print("SMOKE FAIL: one or more smoke years are incomplete")

    if failures:
        logger.error("Completed with %d failing year(s)", len(failures))
        for year, reasons in failures:
            logger.error("Failure %d: %s", year, " | ".join(reasons))
        return 1

    logger.info("Completed successfully with no year failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
