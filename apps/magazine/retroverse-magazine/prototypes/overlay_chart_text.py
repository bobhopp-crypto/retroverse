#!/usr/bin/env python3
"""Overlay chart data using chart_page_layout_map.json coordinates. Percent → pixels, padding, strict bounds."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROTO = Path(__file__).resolve().parent
IMG_PATH = PROTO / "chart_page_1978_full.png"
COORDS_PATH = PROTO / "chart_page_layout_map.json"
DATA_PATH = PROTO / "chart_page_1978_layout_map.json"
OUT_PATH = PROTO / "chart_page_1978_composed.png"

W, H = 2850, 3600
PAD = 25  # padding inside each box

BLACK = (30, 28, 26)
RED_ACCENT = (180, 50, 45)
GOLD_ACCENT = (180, 140, 50)
DARK_GRAY = (80, 75, 70)


def rect(coords: dict) -> tuple[int, int, int, int]:
    """Convert percent coords to pixel rect (x1, y1, x2, y2)."""
    x1 = int(coords["x"] * W)
    y1 = int(coords["y"] * H)
    x2 = int((coords["x"] + coords["w"]) * W)
    y2 = int((coords["y"] + coords["h"]) * H)
    return x1, y1, x2, y2


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    with open(COORDS_PATH) as f:
        coords = json.load(f)["coordinates_percent"]
    with open(DATA_PATH) as f:
        data = json.load(f)["text_placement"]

    img = Image.open(IMG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fonts
    serif = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"
    sans = "/System/Library/Fonts/Helvetica.ttc"
    sans_bold = "/System/Library/Fonts/ArialHB.ttc"

    # --- TITLE ---
    r = rect(coords["title"])
    x1, y1, x2, y2 = r[0] + PAD, r[1] + PAD, r[2] - PAD, r[3] - PAD
    box_w = x2 - x1
    font_title = get_font(serif, 80)
    font_sub = get_font(serif, 38)
    tw, th = draw.textbbox((0, 0), "Top Songs of 1978", font=font_title)[2:4]
    draw.text((x1 + (box_w - tw) // 2, y1 + 20), "Top Songs of 1978", fill=RED_ACCENT, font=font_title)
    sw, sh = draw.textbbox((0, 0), "The records that ruled the year", font=font_sub)[2:4]
    draw.text((x1 + (box_w - sw) // 2, y1 + 100), "The records that ruled the year", fill=DARK_GRAY, font=font_sub)

    # --- CHART GRID ---
    grid = rect(coords["chart_grid"])
    gx1, gy1, gx2, gy2 = grid[0] + PAD, grid[1] + PAD, grid[2] - PAD, grid[3] - PAD
    grid_h = gy2 - gy1
    row_h = grid_h // 24  # 1 header + 23 rows
    header_y = gy1

    cols = coords["chart_columns"]
    rank_r = rect(cols["rank"])
    title_r = rect(cols["title"])
    artist_r = rect(cols["artist"])
    weeks_r = rect(cols["weeks"])
    peak_r = rect(cols["peak"])

    rank_x = rank_r[0] + PAD
    title_x = title_r[0] + PAD
    artist_x = artist_r[0] + PAD
    weeks_x = weeks_r[0] + PAD
    peak_x = peak_r[0] + PAD

    rank_w = rank_r[2] - rank_r[0] - 2 * PAD
    title_w = title_r[2] - title_r[0] - 2 * PAD
    artist_w = artist_r[2] - artist_r[0] - 2 * PAD
    weeks_w = weeks_r[2] - weeks_r[0] - 2 * PAD
    peak_w = peak_r[2] - peak_r[0] - 2 * PAD

    font_hdr = get_font(sans_bold, 28)
    font_row = get_font(sans, 30)

    # Column headers (small caps feel)
    for label, px in [("#", rank_x), ("TITLE", title_x), ("ARTIST", artist_x), ("WKS", weeks_x), ("PK", peak_x)]:
        draw.text((px, header_y + 10), label, fill=GOLD_ACCENT, font=font_hdr)

    # 23 rows, even spacing within chart_grid
    cr = data["chart_rows"]
    for i, row in enumerate(cr["rows"]):
        y = header_y + (i + 1) * row_h + 6
        draw.text((rank_x, y), str(row["rank"]), fill=BLACK, font=font_row)
        draw.text((title_x, y), (row["title"] or "")[:35], fill=BLACK, font=font_row)
        draw.text((artist_x, y), (row["artist"] or "")[:22], fill=DARK_GRAY, font=font_row)
        draw.text((weeks_x, y), str(row["weeks"]), fill=BLACK, font=font_row)
        draw.text((peak_x, y), str(row["peak"]), fill=BLACK, font=font_row)

    # --- PANELS (left-aligned, slightly smaller) ---
    font_panel_hdr = get_font(sans_bold, 34)
    font_panel = get_font(sans, 26)

    def draw_panel(panel_coords: dict, header: str, items: list, line1: str, line2: str):
        r = rect(panel_coords)
        x1, y1 = r[0] + PAD, r[1] + PAD
        draw.text((x1, y1), header, fill=RED_ACCENT, font=font_panel_hdr)
        for i, item in enumerate(items):
            y = y1 + 55 + i * 52
            draw.text((x1, y), (line1(item) or "")[:38], fill=BLACK, font=font_panel)
            draw.text((x1, y + 28), (line2(item) or "")[:38], fill=DARK_GRAY, font=font_panel)

    # Biggest Albums
    pa = data["panel_albums"]
    draw_panel(
        coords["panel_biggest_albums"],
        pa["header"],
        pa["items"],
        lambda i: i["album"],
        lambda i: f"{i['artist']} • {i['detail']}",
    )

    # New Artists
    pn = data["panel_new_artists"]
    draw_panel(
        coords["panel_new_artists"],
        pn["header"],
        pn["items"],
        lambda i: i["artist"],
        lambda i: f"{i['song']} — #{i['rank']}",
    )

    # Fastest Risers
    pr = data["panel_risers"]
    r = rect(coords["panel_fastest_risers"])
    x1, y1 = r[0] + PAD, r[1] + PAD
    draw.text((x1, y1), pr["header"], fill=RED_ACCENT, font=font_panel_hdr)
    draw.text((x1, y1 + 55), pr["placeholder"], fill=DARK_GRAY, font=font_panel)

    # --- FOOTER ---
    r = rect(coords["footer"])
    x1, y1 = r[0] + PAD, r[1] + PAD
    fz = data["footer_zone"]
    txt = (fz["content"] or "")[:100]
    draw.text((x1, y1), txt, fill=DARK_GRAY, font=get_font(sans, 24))

    img.save(OUT_PATH)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
