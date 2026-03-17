#!/usr/bin/env python3
"""Deterministically composite the 1974 Retroverse deck into fixed trading-card frames."""

from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

YEAR = "1974"
CARD_WIDTH = 1024
CARD_HEIGHT = 1536
SUIT_HEART = "\u2665"

ROOT = Path(__file__).resolve().parents[1]
MASTER_JSON = ROOT / "retroverse-output" / "retroverse_year_master_1958_2024.json"
ART_DIR = ROOT / "retroverse-output" / "decks" / YEAR
ASSETS_DIR = ART_DIR / "assets"
FRAME_PATH = ASSETS_DIR / "frame_1974.png"
FINAL_DIR = ART_DIR / "final"

ART_CUTOUT_BOX = (202, 174, 822, 1104)
ART_BEZEL_BOX = (184, 156, 840, 1122)
HEADER_BOX = (264, 50, 870, 132)
RIBBON_BOX = (64, 58, 238, 170)
TITLE_BOX = (142, 1124, 882, 1206)
ARTIST_BOX = (180, 1218, 844, 1266)
STATS_BOX = (212, 1276, 812, 1310)
FOOTER_BOX = (282, 1458, 742, 1506)
LIST_BOX = (236, 598, 788, 1002)

PANEL_BAND_BOX = (78, 1324, 946, 1444)
PANEL_GAP = 18
PANEL_WIDTH = (PANEL_BAND_BOX[2] - PANEL_BAND_BOX[0] - PANEL_GAP * 2) // 3
PANEL_BOXES = [
    (
        PANEL_BAND_BOX[0] + index * (PANEL_WIDTH + PANEL_GAP),
        PANEL_BAND_BOX[1],
        PANEL_BAND_BOX[0] + index * (PANEL_WIDTH + PANEL_GAP) + PANEL_WIDTH,
        PANEL_BAND_BOX[3],
    )
    for index in range(3)
]

OUTER_BROWN = (28, 18, 12, 255)
DEEP_BROWN = (52, 33, 21, 255)
MID_BROWN = (84, 54, 33, 255)
PANEL_BROWN = (112, 76, 44, 255)
AGED_GOLD = (194, 152, 100, 255)
AGED_GOLD_DIM = (154, 119, 74, 255)
PARCHMENT = (232, 212, 180, 255)
INK_DARK = (24, 16, 11, 255)
CREAM = (247, 233, 206, 255)
TEXT_GOLD = (227, 195, 144, 255)

RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS

FONT_CANDIDATES = {
    "regular": [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Baskerville.ttc",
        "/Library/Fonts/Times New Roman.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "bold": [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/Library/Fonts/Times New Roman Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
}

COURT_RANGES = {
    "J": (11, 20),
    "Q": (21, 30),
    "K": (31, 40),
}


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    family = "bold" if bold else "regular"
    for candidate in FONT_CANDIDATES[family]:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    if not text:
        return 0
    left, _, right, _ = draw.textbbox((0, 0), text, font=font)
    return right - left


def line_height(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), "Ag", font=font)
    return bottom - top


def truncate_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    candidate = normalize_space(text)
    if text_width(draw, candidate, font) <= max_width:
        return candidate

    ellipsis = "..."
    words = candidate.split()
    while words:
        reduced = " ".join(words).strip()
        probe = f"{reduced}{ellipsis}"
        if text_width(draw, probe, font) <= max_width:
            return probe
        words.pop()

    raw = candidate
    while raw:
        probe = f"{raw}{ellipsis}"
        if text_width(draw, probe, font) <= max_width:
            return probe
        raw = raw[:-1]
    return ellipsis


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int,
) -> list[str]:
    normalized = normalize_space(text)
    if not normalized:
        return []

    words = normalized.split(" ")
    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        probe = f"{current} {word}"
        if text_width(draw, probe, font) <= max_width:
            current = probe
            continue
        lines.append(current)
        current = word

    lines.append(current)

    if len(lines) <= max_lines:
        return lines

    trimmed = lines[: max_lines - 1]
    overflow = " ".join(lines[max_lines - 1 :])
    trimmed.append(truncate_text(draw, overflow, font, max_width))
    return trimmed


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    max_size: int,
    min_size: int,
    max_lines: int,
    bold: bool = False,
) -> tuple[ImageFont.ImageFont, list[str]]:
    width = box[2] - box[0]
    height = box[3] - box[1]

    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, width, max_lines)
        if not lines:
            return font, []

        current_height = line_height(draw, font)
        total_height = current_height * len(lines) + max(0, len(lines) - 1) * max(2, size // 8)
        if total_height <= height and all(text_width(draw, line, font) <= width for line in lines):
            return font, lines

    fallback = load_font(min_size, bold=bold)
    return fallback, wrap_text(draw, text, fallback, width, max_lines)


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    max_size: int,
    min_size: int,
    max_lines: int,
    fill: tuple[int, int, int, int],
    bold: bool = False,
    align: str = "center",
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
) -> None:
    font, lines = fit_lines(
        draw,
        text,
        box,
        max_size=max_size,
        min_size=min_size,
        max_lines=max_lines,
        bold=bold,
    )
    if not lines:
        return

    current_height = line_height(draw, font)
    gap = max(2, getattr(font, "size", min_size) // 8)
    total_height = current_height * len(lines) + gap * max(0, len(lines) - 1)
    y = box[1] + ((box[3] - box[1] - total_height) / 2)

    for line in lines:
        width = text_width(draw, line, font)
        if align == "left":
            x = box[0]
        elif align == "right":
            x = box[2] - width
        else:
            x = box[0] + ((box[2] - box[0] - width) / 2)

        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        y += current_height + gap


def add_distress_texture(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(19740101)

    for _ in range(1600):
        x = rng.randint(12, CARD_WIDTH - 12)
        y = rng.randint(12, CARD_HEIGHT - 12)
        radius = rng.choice((1, 1, 1, 2))
        color = rng.choice(
            (
                (255, 234, 198, 18),
                (0, 0, 0, 24),
                (118, 82, 49, 28),
            )
        )
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    for _ in range(180):
        x1 = rng.randint(24, CARD_WIDTH - 24)
        y1 = rng.randint(24, CARD_HEIGHT - 24)
        x2 = x1 + rng.randint(-90, 90)
        y2 = y1 + rng.randint(-20, 20)
        width = rng.choice((1, 1, 2))
        color = rng.choice(
            (
                (0, 0, 0, 20),
                (238, 214, 174, 16),
            )
        )
        draw.line((x1, y1, x2, y2), fill=color, width=width)


def draw_star(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, fill: tuple[int, int, int, int]) -> None:
    cx, cy = center
    points: list[tuple[float, float]] = []
    for index in range(10):
        angle = -math.pi / 2 + index * (math.pi / 5)
        current_radius = radius if index % 2 == 0 else radius * 0.42
        points.append((cx + math.cos(angle) * current_radius, cy + math.sin(angle) * current_radius))
    draw.polygon(points, fill=fill)


def clear_alpha_box(image: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    alpha = image.getchannel("A")
    alpha_draw = ImageDraw.Draw(alpha)
    alpha_draw.rounded_rectangle(box, radius=radius, fill=0)
    image.putalpha(alpha)


def build_frame_template() -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    frame = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), OUTER_BROWN)
    draw = ImageDraw.Draw(frame, "RGBA")

    draw.rounded_rectangle((20, 20, CARD_WIDTH - 20, CARD_HEIGHT - 20), radius=54, fill=OUTER_BROWN)
    draw.rounded_rectangle((42, 42, CARD_WIDTH - 42, CARD_HEIGHT - 42), radius=44, fill=DEEP_BROWN, outline=AGED_GOLD_DIM, width=3)
    draw.rounded_rectangle((64, 64, CARD_WIDTH - 64, CARD_HEIGHT - 64), radius=36, fill=MID_BROWN, outline=AGED_GOLD, width=4)
    draw.rounded_rectangle((84, 84, CARD_WIDTH - 84, 1484), radius=30, outline=PARCHMENT, width=2)

    draw.rounded_rectangle(HEADER_BOX, radius=24, fill=DEEP_BROWN, outline=AGED_GOLD, width=3)
    draw.rounded_rectangle((HEADER_BOX[0] + 12, HEADER_BOX[1] + 10, HEADER_BOX[2] - 12, HEADER_BOX[3] - 10), radius=18, outline=(236, 218, 184, 96), width=2)

    ribbon_points = [
        (RIBBON_BOX[0], RIBBON_BOX[1]),
        (RIBBON_BOX[2], RIBBON_BOX[1]),
        (RIBBON_BOX[2], RIBBON_BOX[3] - 18),
        (RIBBON_BOX[0] + 110, RIBBON_BOX[3] - 18),
        (RIBBON_BOX[0] + 84, RIBBON_BOX[3] + 18),
        (RIBBON_BOX[0] + 58, RIBBON_BOX[3] - 18),
        (RIBBON_BOX[0], RIBBON_BOX[3] - 18),
    ]
    draw.polygon(ribbon_points, fill=PANEL_BROWN, outline=AGED_GOLD)
    draw.line(ribbon_points + [ribbon_points[0]], fill=AGED_GOLD, width=3)

    draw.rounded_rectangle(ART_BEZEL_BOX, radius=30, fill=DEEP_BROWN, outline=AGED_GOLD, width=4)
    draw.rounded_rectangle(
        (ART_BEZEL_BOX[0] + 12, ART_BEZEL_BOX[1] + 12, ART_BEZEL_BOX[2] - 12, ART_BEZEL_BOX[3] - 12),
        radius=24,
        outline=(244, 224, 186, 84),
        width=2,
    )

    draw.rounded_rectangle(TITLE_BOX, radius=30, fill=DEEP_BROWN, outline=AGED_GOLD, width=3)
    draw.rounded_rectangle(ARTIST_BOX, radius=18, fill=PANEL_BROWN, outline=AGED_GOLD_DIM, width=3)
    draw.rounded_rectangle(STATS_BOX, radius=16, fill=DEEP_BROWN, outline=AGED_GOLD_DIM, width=2)

    draw.rounded_rectangle(PANEL_BAND_BOX, radius=24, fill=DEEP_BROWN, outline=AGED_GOLD, width=3)
    for panel_box in PANEL_BOXES:
        draw.rounded_rectangle(panel_box, radius=18, fill=PANEL_BROWN, outline=AGED_GOLD_DIM, width=2)

    draw.rounded_rectangle(FOOTER_BOX, radius=18, fill=DEEP_BROWN, outline=AGED_GOLD_DIM, width=3)

    corner_boxes = [
        (94, 94, 180, 180),
        (844, 94, 930, 180),
        (94, 1364, 180, 1450),
        (844, 1364, 930, 1450),
    ]
    for corner in corner_boxes:
        draw.arc(corner, start=0, end=360, fill=(240, 220, 186, 72), width=3)

    for x in (308, 512, 716):
        draw_star(draw, (x, 92), 10, AGED_GOLD)
    for x in (360, 512, 664):
        draw_star(draw, (x, 1482), 8, AGED_GOLD_DIM)

    add_distress_texture(frame)
    clear_alpha_box(frame, ART_CUTOUT_BOX, radius=26)

    lip = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    lip_draw = ImageDraw.Draw(lip, "RGBA")
    lip_draw.rounded_rectangle(ART_CUTOUT_BOX, radius=26, outline=AGED_GOLD, width=4)
    lip_draw.rounded_rectangle(
        (ART_CUTOUT_BOX[0] + 8, ART_CUTOUT_BOX[1] + 8, ART_CUTOUT_BOX[2] - 8, ART_CUTOUT_BOX[3] - 8),
        radius=20,
        outline=(246, 228, 198, 110),
        width=2,
    )
    frame = Image.alpha_composite(frame, lip)

    frame.save(FRAME_PATH)
    return FRAME_PATH


def load_year_data() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with MASTER_JSON.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    year_data = payload.get(YEAR)
    if not isinstance(year_data, dict):
        raise ValueError(f"Year {YEAR} not found in {MASTER_JSON}")

    top_40 = year_data.get("top_40")
    culture = year_data.get("culture")
    if not isinstance(top_40, list) or len(top_40) < 40:
        raise ValueError(f"Expected 40 songs for {YEAR}")
    if not isinstance(culture, dict):
        raise ValueError(f"Culture block missing for {YEAR}")
    return top_40[:40], culture


def symbol_for_rank(rank: int) -> str:
    return "A" if rank == 1 else str(rank)


def art_path_for_label(label: str) -> Path:
    if label == "A":
        return ART_DIR / "1974_deck_A.png"
    if label in COURT_RANGES:
        return ART_DIR / f"1974_deck_{label}.png"
    return ART_DIR / f"1974_deck_{int(label):02d}.png"


def final_path_for_label(label: str) -> Path:
    if label.isdigit():
        return FINAL_DIR / f"1974_final_{int(label):02d}.png"
    return FINAL_DIR / f"1974_final_{label}.png"


def fit_art_to_window(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"Artwork not found: {path}")
    with Image.open(path) as raw_image:
        art = raw_image.convert("RGBA")

    target_size = (ART_CUTOUT_BOX[2] - ART_CUTOUT_BOX[0], ART_CUTOUT_BOX[3] - ART_CUTOUT_BOX[1])
    return ImageOps.fit(art, target_size, method=RESAMPLE, centering=(0.5, 0.5))


def base_card_with_frame(frame: Image.Image, art_path: Path) -> Image.Image:
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), OUTER_BROWN)
    art = fit_art_to_window(art_path)
    card.paste(art, ART_CUTOUT_BOX[:2], art)
    return Image.alpha_composite(card, frame)


def rank_header_text(rank: int) -> str:
    return f"#{rank} SONG OF {YEAR}"


def clean_headline(entry: Any) -> str:
    if isinstance(entry, dict):
        date_value = normalize_space(str(entry.get("date", "")))
        event = normalize_space(str(entry.get("event", "")))
    else:
        date_value = ""
        event = normalize_space(str(entry))

    event = re.sub(r"^[A-Za-z]+\s+\d+\s+[–-]\s+", "", event)
    if len(event) > 92:
        event = event[:92].rsplit(" ", 1)[0].rstrip(" ,.;:") + "..."

    if date_value:
        return f"{date_value} - {event}"
    return event


def draw_static_frame_text(
    draw: ImageDraw.ImageDraw,
    *,
    header_text: str,
    ribbon_text: str,
    title_text: str,
    artist_text: str,
    stats_text: str,
) -> None:
    draw_text_block(
        draw,
        header_text,
        HEADER_BOX,
        max_size=32,
        min_size=18,
        max_lines=1,
        bold=True,
        fill=TEXT_GOLD,
    )
    draw_text_block(
        draw,
        ribbon_text,
        (RIBBON_BOX[0] + 16, RIBBON_BOX[1] + 8, RIBBON_BOX[2] - 16, RIBBON_BOX[3] - 14),
        max_size=48,
        min_size=24,
        max_lines=1,
        bold=True,
        fill=CREAM,
    )
    draw_text_block(
        draw,
        SUIT_HEART,
        (862, 56, 954, 132),
        max_size=52,
        min_size=26,
        max_lines=1,
        bold=True,
        fill=TEXT_GOLD,
    )
    draw_text_block(
        draw,
        title_text,
        TITLE_BOX,
        max_size=42,
        min_size=18,
        max_lines=2,
        bold=True,
        fill=CREAM,
    )
    draw_text_block(
        draw,
        artist_text,
        ARTIST_BOX,
        max_size=28,
        min_size=14,
        max_lines=1,
        bold=True,
        fill=TEXT_GOLD,
    )
    draw_text_block(
        draw,
        stats_text,
        STATS_BOX,
        max_size=21,
        min_size=13,
        max_lines=1,
        bold=False,
        fill=PARCHMENT,
    )
    draw_text_block(
        draw,
        YEAR,
        FOOTER_BOX,
        max_size=28,
        min_size=16,
        max_lines=1,
        bold=True,
        fill=TEXT_GOLD,
    )


def draw_panel(
    draw: ImageDraw.ImageDraw,
    label: str,
    value: str,
    panel_box: tuple[int, int, int, int],
) -> None:
    label_box = (panel_box[0] + 10, panel_box[1] + 8, panel_box[2] - 10, panel_box[1] + 34)
    value_box = (panel_box[0] + 12, panel_box[1] + 36, panel_box[2] - 12, panel_box[3] - 10)
    draw_text_block(
        draw,
        label,
        label_box,
        max_size=19,
        min_size=12,
        max_lines=1,
        bold=True,
        fill=TEXT_GOLD,
    )
    draw_text_block(
        draw,
        value,
        value_box,
        max_size=21,
        min_size=12,
        max_lines=4,
        bold=False,
        fill=CREAM,
    )


def compose_number_card(
    frame: Image.Image,
    song: dict[str, Any],
    culture: dict[str, Any],
) -> Path:
    rank = int(song["rv_rank"])
    label = symbol_for_rank(rank)
    card = base_card_with_frame(frame, art_path_for_label(label))
    draw = ImageDraw.Draw(card)

    films = culture.get("films") or []
    tv = culture.get("tv") or []
    headlines = culture.get("headlines") or []
    index = rank - 1

    film_text = str(films[index]) if index < len(films) else "Unavailable"
    tv_text = str(tv[index]) if index < len(tv) else "Unavailable"
    headline_text = clean_headline(headlines[index]) if index < len(headlines) else "Unavailable"
    stats_text = f"PEAK #{int(song['peak_rank'])}  |  {int(song['weeks_on_chart'])} WEEKS ON CHART"

    draw_static_frame_text(
        draw,
        header_text=rank_header_text(rank),
        ribbon_text=label,
        title_text=str(song["title"]),
        artist_text=str(song["artist"]),
        stats_text=stats_text,
    )

    draw_panel(draw, "FILM", film_text, PANEL_BOXES[0])
    draw_panel(draw, "TV", tv_text, PANEL_BOXES[1])
    draw_panel(draw, "HEADLINE", headline_text, PANEL_BOXES[2])

    output_path = final_path_for_label(label)
    card.save(output_path)
    return output_path


def draw_court_song_list(draw: ImageDraw.ImageDraw, titles: list[str]) -> None:
    draw.rounded_rectangle(LIST_BOX, radius=24, fill=(28, 18, 12, 170), outline=(224, 186, 132, 220), width=3)
    draw.rounded_rectangle(
        (LIST_BOX[0] + 10, LIST_BOX[1] + 10, LIST_BOX[2] - 10, LIST_BOX[3] - 10),
        radius=18,
        outline=(248, 230, 202, 76),
        width=2,
    )

    column_gap = 26
    list_left = LIST_BOX[0] + 26
    list_top = LIST_BOX[1] + 26
    list_width = LIST_BOX[2] - LIST_BOX[0] - 52
    column_width = (list_width - column_gap) // 2
    row_height = 68

    title_font = load_font(19, bold=False)
    rows_per_column = 5

    for index, title in enumerate(titles):
        column = 0 if index < rows_per_column else 1
        row = index % rows_per_column
        x = list_left + column * (column_width + column_gap)
        y = list_top + row * row_height
        box = (x, y, x + column_width, y + row_height - 6)
        draw_text_block(
            draw,
            title,
            box,
            max_size=getattr(title_font, "size", 19),
            min_size=13,
            max_lines=2,
            bold=False,
            fill=CREAM,
            align="left",
        )


def compose_court_card(
    frame: Image.Image,
    label: str,
    songs: list[dict[str, Any]],
) -> Path:
    card = base_card_with_frame(frame, art_path_for_label(label))
    draw = ImageDraw.Draw(card)

    range_start = int(songs[0]["rv_rank"])
    range_end = int(songs[-1]["rv_rank"])
    header_text = f"RANKS {range_start}-{range_end} OF {YEAR}"
    title_text = f"{range_start}-{range_end} YEAR-END ROTATION"
    artist_text = f"{len(songs)} TITLES  |  TWO-COLUMN LIST"
    stats_text = "CURATED YEAR-END GROUPING"

    draw_static_frame_text(
        draw,
        header_text=header_text,
        ribbon_text=label,
        title_text=title_text,
        artist_text=artist_text,
        stats_text=stats_text,
    )

    draw_court_song_list(draw, [str(song["title"]) for song in songs])

    output_path = final_path_for_label(label)
    card.save(output_path)
    return output_path


def main() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    top_40, culture = load_year_data()
    frame_path = build_frame_template()
    frame = Image.open(frame_path).convert("RGBA")

    generated_paths: list[Path] = []
    for song in top_40[:10]:
        generated_paths.append(compose_number_card(frame, song, culture))

    for label, (start, end) in COURT_RANGES.items():
        generated_paths.append(compose_court_card(frame, label, top_40[start - 1 : end]))

    print(f"Frame template: {frame_path}")
    for path in generated_paths:
        print(path)


if __name__ == "__main__":
    main()
